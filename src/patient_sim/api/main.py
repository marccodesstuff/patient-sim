from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import posthog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from posthog import capture, identify_context, new_context
from pydantic import BaseModel

from patient_sim.config.settings import get_settings
from patient_sim.graph.graph import build_graph
from patient_sim.graph.state import ConversationState
from patient_sim.logging.replay import SessionReplayer
from patient_sim.logging.structured_logger import TurnLogger, get_logger
from patient_sim.personas.schemas import load_scenario_from_file
from patient_sim.retriever_factory import load_persona_from_file as _load_persona_from_file

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.posthog_disabled:
        posthog.api_key = settings.posthog_project_token
        posthog.host = settings.posthog_host
    yield
    if not settings.posthog_disabled:
        posthog.flush()


app = FastAPI(title="Patient Communication Simulator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartRequest(BaseModel):
    scenario_path: str
    persona_path: str | None = None
    difficulty: str = "distressed"
    max_turns: int = 12
    seed: int | None = 42


class TurnRequest(BaseModel):
    student_message: str


class StartResponse(BaseModel):
    session_id: str
    state: dict[str, Any]
    patient_turn: dict[str, Any] | None = None


sessions: dict[str, dict[str, Any]] = {}


@app.post("/sessions/start", response_model=StartResponse)
def start_session(req: StartRequest) -> StartResponse:
    scenario = load_scenario_from_file(req.scenario_path)
    persona_path = req.persona_path or f"personas/{scenario.persona_ref}.yaml"
    persona = _load_persona_from_file(persona_path)
    session_id = f"{scenario.scenario_id}-{len(sessions)+1}"
    state: ConversationState = {
        "session_id": session_id,
        "scenario_id": scenario.scenario_id,
        "persona_id": persona.persona_id,
        "turn_number": 0,
        "max_turns": req.max_turns or scenario.max_turns,
        "seed": req.seed,
        "difficulty": req.difficulty,
        "student_message": None,
        "retrieved_chunks": [],
        "conversation_history": [],
        "conversation_summary": "",
        "emotional_state": persona.emotional_profile.baseline_mood,
        "revealed_facts": [],
        "flags": [],
        "current_patient_turn": None,
        "is_red_line": False,
        "red_line_topic": None,
        "next": None,
    }
    sessions[session_id] = state
    TurnLogger(session_id).log_turn({"event": "session_start", **state})

    with new_context():
        identify_context(session_id)
        capture(
            "session_started",
            properties={
                "scenario_id": scenario.scenario_id,
                "persona_id": persona.persona_id,
                "difficulty": req.difficulty,
                "max_turns": state["max_turns"],
            },
        )

    return StartResponse(session_id=session_id, state=state)


@app.post("/sessions/{session_id}/turn")
def session_turn(session_id: str, req: TurnRequest) -> dict[str, Any]:
    state = sessions.get(session_id)
    if state is None:
        with new_context():
            capture(
                "session_not_found",
                properties={"session_id": session_id},
            )
        raise HTTPException(status_code=404, detail="session not found")

    state["student_message"] = req.student_message
    graph = build_graph()

    with new_context():
        identify_context(session_id)
        result = graph.invoke(state, {"configurable": {"thread_id": session_id}})
        sessions[session_id] = result
        TurnLogger(session_id).log_turn({"event": "turn", **result})

        turn_number = int(result.get("turn_number", 0))
        max_turns = int(result.get("max_turns", 0))
        message_length = len(req.student_message)

        capture(
            "session_turn_completed",
            properties={
                "scenario_id": result.get("scenario_id"),
                "persona_id": result.get("persona_id"),
                "turn_number": turn_number,
                "max_turns": max_turns,
                "emotional_state": result.get("emotional_state"),
                "message_length": message_length,
                "flags": result.get("flags", []),
            },
        )

        if result.get("is_red_line"):
            capture(
                "red_line_triggered",
                properties={
                    "scenario_id": result.get("scenario_id"),
                    "persona_id": result.get("persona_id"),
                    "turn_number": turn_number,
                    "red_line_topic": result.get("red_line_topic"),
                },
            )

        if max_turns > 0 and turn_number >= max_turns:
            capture(
                "session_max_turns_reached",
                properties={
                    "scenario_id": result.get("scenario_id"),
                    "persona_id": result.get("persona_id"),
                    "turn_number": turn_number,
                    "max_turns": max_turns,
                },
            )

    return result


@app.get("/sessions/{session_id}/replay")
def replay_session(session_id: str) -> dict[str, Any]:
    replayer = SessionReplayer(session_id)
    events = replayer.replay()

    with new_context():
        identify_context(session_id)
        capture(
            "session_replayed",
            properties={
                "session_id": session_id,
                "event_count": len(events),
            },
        )

    return {"events": events}
