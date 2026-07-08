from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RubricCriterion(BaseModel):
    name: str
    description: str
    scale: str = "1-4"
    weight: float = 1.0


class Rubric(BaseModel):
    rubric_id: str
    version: int = 1
    criteria: list[RubricCriterion] = Field(default_factory=list)


class TurnEvaluation(BaseModel):
    turn_number: int
    student_input: str
    scores: dict[str, int] = Field(default_factory=dict)
    feedback: str = ""
    flags: list[str] = Field(default_factory=list)


class SessionEvaluation(BaseModel):
    rubric_id: str
    rubric_version: int
    overall_score: float | None = None
    criteria_scores: dict[str, float] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class TurnJudgeRequest(BaseModel):
    rubric: Rubric
    transcript_segment: str
    student_input: str
    patient_turn: dict[str, Any]
