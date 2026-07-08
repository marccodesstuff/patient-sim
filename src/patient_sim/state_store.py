from __future__ import annotations

from collections import deque
from typing import Any

from patient_sim.graph.state import ConversationState


MAX_HISTORY_TURNS = 6


def rolling_summary(history: list[dict[str, Any]]) -> str:
    if not history:
        return ""
    recent = history[-MAX_HISTORY_TURNS:]
    parts = []
    for item in recent:
        s = item.get("student") or ""
        p = item.get("patient") or ""
        parts.append(f"Student: {s}\nPatient: {p}")
    return "\n\n".join(parts)


def update_revealed_facts(state: ConversationState) -> ConversationState:
    revealed: list[str] = list(state.get("revealed_facts", []))
    for fact in (state.get("current_patient_turn") or {}).get("revealed_facts", []):
        fact = (fact or "").strip()
        if fact and fact not in revealed:
            revealed.append(fact)
    state["revealed_facts"] = revealed
    return state


def update_emotional_state(state: ConversationState) -> ConversationState:
    turn = state.get("current_patient_turn") or {}
    emotional_state = (turn.get("emotional_state") or state.get("emotional_state") or "neutral").strip()
    state["emotional_state"] = emotional_state
    return state


def conversation_history_deque(maxlen: int = MAX_HISTORY_TURNS) -> deque:
    return deque(maxlen=maxlen)


def append_history(state: ConversationState, *, maxlen: int = MAX_HISTORY_TURNS) -> ConversationState:
    if not state.get("current_patient_turn"):
        return state
    history: deque = deque(state.get("conversation_history") or [], maxlen=maxlen)
    history.append(
        {
            "student": state.get("student_message"),
            "patient": state["current_patient_turn"].get("patient_utterance"),
            "emotional_state": state["current_patient_turn"].get("emotional_state"),
            "flags": state["current_patient_turn"].get("flags", []),
        }
    )
    state["conversation_history"] = list(history)
    state["conversation_summary"] = rolling_summary(list(history))
    state["turn_number"] = int(state.get("turn_number", 0)) + 1
    return state


def difficulty_multiplier(difficulty: str) -> dict[str, float]:
    mapping = {
        "cooperative": {"disclosure": 1.0, "affect": 1.0, "threshold": 0.1},
        "guarded": {"disclosure": 0.4, "affect": 0.6, "threshold": 0.6},
        "distressed": {"disclosure": 0.25, "affect": 1.4, "threshold": 0.8},
    }
    return mapping.get(difficulty, mapping["cooperative"])


class RedLineHandler:
    def __init__(self, red_lines: list[dict[str, str]]) -> None:
        self.red_lines = red_lines or []

    def check(self, text: str) -> dict[str, Any] | None:
        lower = text.lower()
        for item in self.red_lines:
            topic = item.get("topic", "")
            if topic and topic.lower() in lower:
                return {
                    "safe_response": item.get("safe_response", ""),
                    "flag": item.get("flag", "red_line_triggered"),
                    "topic": topic,
                }
        return None


def apply_safe_branch(state: ConversationState, *, red_line_override: dict[str, Any] | None = None) -> ConversationState:
    red_line = red_line_override or {
        "safe_response": "I prefer not to talk about that right now.",
        "flag": "red_line_triggered",
        "topic": "",
    }
    state["is_red_line"] = True
    state["red_line_topic"] = red_line.get("topic")
    state["current_patient_turn"] = {
        "patient_utterance": red_line.get("safe_response", ""),
        "emotional_state": state.get("emotional_state", "neutral"),
        "revealed_facts": [],
        "internal_notes": f"Red-line topic triggered: {red_line.get('topic')}.",
        "flags": [red_line.get("flag", "red_line_triggered")],
        "retrieval_citations": [],
    }
    state["flags"] = [red_line.get("flag", "red_line_triggered")]
    return state
