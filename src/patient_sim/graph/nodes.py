from __future__ import annotations

import logging
import time
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from posthog import capture

from patient_sim.config.settings import get_settings
from patient_sim.graph.parser import parse_patient_turn
from patient_sim.graph.state import ConversationState
from patient_sim.models.factory import ModelProvider
from patient_sim.prompts.patient_system import PATIENT_SYSTEM_V1

logger = logging.getLogger(__name__)


def _state_to_prompt_input(state: ConversationState) -> dict[str, Any]:
    return {
        "context": "\n\n".join(state.get("retrieved_chunks", [])),
        "summary": state.get("conversation_summary", ""),
        "student": state.get("student_message", ""),
    }


def input_guard(state: ConversationState) -> ConversationState:
    msg = (state.get("student_message") or "").strip()
    if not msg:
        state["next"] = "end_session"
    return state


def retrieve(state: ConversationState, retriever: Any | None = None, *, k: int = 4) -> ConversationState:
    if state.get("retrieved_chunks"):
        return state
    if retriever is not None:
        docs = retriever.invoke(state.get("student_message") or "")
        state["retrieved_chunks"] = [d.page_content for d in docs]
        capture(
            "rag_retrieved",
            properties={
                "session_id": state.get("session_id"),
                "scenario_id": state.get("scenario_id"),
                "chunk_count": len(state["retrieved_chunks"]),
                "turn_number": state.get("turn_number"),
            },
        )
    return state


def respond(state: ConversationState, model: BaseChatModel | None = None) -> ConversationState:
    if model is None:
        settings = get_settings()
        provider = ModelProvider(settings)
        model = provider.chat_model(for_patient=True)

    prompt = ChatPromptTemplate.from_messages([\
        ("system", PATIENT_SYSTEM_V1),
        ("user", "PERSONA/CONTEXT:\n{context}\n\nCONVERSATION SUMMARY:\n{summary}\n\nSTUDENT MESSAGE:\n{student}\n\nRespond as the patient in the persona's voice."),
    ])
    chain = prompt | model | StrOutputParser()
    t0 = time.time()
    raw = chain.invoke(_state_to_prompt_input(state))
    latency_ms = int((time.time() - t0) * 1000)

    citations = state.get("retrieved_chunks", [])[:2]
    parsed = parse_patient_turn(raw, citations)
    state["current_patient_turn"] = parsed.model_dump()
    state["emotional_state"] = parsed.emotional_state
    state["revealed_facts"] = parsed.revealed_facts
    state["flags"] = parsed.flags

    capture(
        "patient_model_invoked",
        properties={
            "session_id": state.get("session_id"),
            "scenario_id": state.get("scenario_id"),
            "turn_number": state.get("turn_number"),
            "latency_ms": latency_ms,
            "emotional_state": parsed.emotional_state,
            "is_red_line": state.get("is_red_line", False),
            "flags": parsed.flags,
        },
    )

    return state


def parse_structured(state: ConversationState) -> ConversationState:
    current = state.get("current_patient_turn") or {}
    state["current_patient_turn"] = current
    return state


def update_state(state: ConversationState) -> ConversationState:
    if state.get("current_patient_turn"):
        turn = state["current_patient_turn"]
        history = state.get("conversation_history", [])
        history.append({
            "student": state.get("student_message"),
            "patient": turn.get("patient_utterance"),
            "emotional_state": turn.get("emotional_state"),
            "flags": turn.get("flags", []),
        })
        state["conversation_history"] = history
        state["conversation_summary"] = _rolling_summary(history)
        state["turn_number"] = int(state.get("turn_number", 0)) + 1
    return state


def evaluate_turn(state: ConversationState) -> ConversationState:
    state["next"] = "log_turn"
    return state


def log_turn(state: ConversationState) -> ConversationState:
    state["next"] = "maybe_end"
    return state


def _rolling_summary(history: list[dict[str, Any]], max_turns: int = 6) -> str:
    if not history:
        return ""
    recent = history[-max_turns:]
    parts = []
    for item in recent:
        s = item.get("student") or ""
        p = item.get("patient") or ""
        parts.append(f"Student: {s}\nPatient: {p}")
    return "\n\n".join(parts)
