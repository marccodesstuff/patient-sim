from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from patient_sim.graph.graph import build_graph
from patient_sim.graph.state import ConversationState
from patient_sim.logging.structured_logger import TurnLogger, get_logger
from patient_sim.logging.replay import SessionReplayer
from patient_sim.personas.schemas import load_persona_from_file, load_scenario_from_file
from patient_sim.retriever_factory import load_persona_from_file as _load_persona_from_file
from patient_sim.rag.ingestor import get_retriever

app = FastAPI(title="Patient Communication Simulator")
logger = get_logger(__name__)


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
    return StartResponse(session_id=session_id, state=state)


@app.post("/sessions/{session_id}/turn")
def session_turn(session_id: str, req: TurnRequest) -> dict[str, Any]:
    state = sessions.get(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="session not found")
    state["student_message"] = req.student_message
    graph = build_graph()
    result = graph.invoke(state)
    sessions[session_id] = result
    TurnLogger(session_id).log_turn({"event": "turn", **result})
    return result


@app.get("/sessions/{session_id}/replay")
def replay_session(session_id: str) -> dict[str, Any]:
    replayer = SessionReplayer(session_id)
    return {"events": replayer.replay()}
