from __future__ import annotations

from typing import Any, TypedDict


class ConversationState(TypedDict, total=False):
    session_id: str
    scenario_id: str
    persona_id: str
    turn_number: int
    max_turns: int
    seed: int | None
    difficulty: str
    student_message: str | None
    retrieved_chunks: list[str]
    conversation_history: list[dict[str, Any]]
    conversation_summary: str
    emotional_state: str
    revealed_facts: list[str]
    flags: list[str]
    current_patient_turn: dict[str, Any] | None
    is_red_line: bool
    red_line_topic: str | None
    next: str | None
