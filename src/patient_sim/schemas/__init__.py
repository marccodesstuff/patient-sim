from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PatientTurn(BaseModel):
    patient_utterance: str
    emotional_state: str
    revealed_facts: list[str] = Field(default_factory=list)
    internal_notes: str = ""
    flags: list[str] = Field(default_factory=list)
    retrieval_citations: list[str] = Field(default_factory=list)


class TurnRecord(BaseModel):
    turn_number: int
    student_input: str
    retrieved_chunks: list[str] = Field(default_factory=list)
    prompt_version: str = ""
    raw_output: str = ""
    parsed_output: PatientTurn | None = None
    tokens: int | None = None
    latency_ms: int | None = None
    cost: float | None = None


class SessionLog(BaseModel):
    session_id: str
    persona_version: str
    scenario_id: str
    provider_config: dict[str, Any] = Field(default_factory=dict)
    seed: int | None = None
    turns: list[TurnRecord] = Field(default_factory=list)
    session_evaluation: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
