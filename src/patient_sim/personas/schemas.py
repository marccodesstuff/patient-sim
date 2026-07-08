from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class Demographics(BaseModel):
    name: str
    age: int
    gender: str
    occupation: str
    background: str


class Condition(BaseModel):
    primary: str
    relevant_history: str = ""
    medications: str = ""


class EmotionalProfile(BaseModel):
    baseline_mood: str
    triggers: list[str] = Field(default_factory=list)
    reassurance_response: str = ""


class CommunicationStyle(BaseModel):
    verbosity: str = Field(json_schema_extra={"enum": ["concise", "moderate", "verbose"]})
    jargon_comfort: str = Field(json_schema_extra={"enum": ["none", "low", "moderate", "high"]})
    openness: str = Field(json_schema_extra={"enum": ["guarded", "moderate", "open"]})


class RedLine(BaseModel):
    topic: str
    safe_response: str
    flag: str = "red_line_triggered"


class Persona(BaseModel):
    persona_id: str
    version: int = 1
    demographics: Demographics
    condition: Condition
    emotional_profile: EmotionalProfile
    communication_style: CommunicationStyle
    hidden_concerns: list[str] = Field(default_factory=list)
    disclosure_rules: list[str] = Field(default_factory=list)
    red_lines: list[RedLine] = Field(default_factory=list)
    knowledge_documents: list[str] = Field(default_factory=list)
    difficulty: str = Field(json_schema_extra={"enum": ["cooperative", "guarded", "distressed"]})


class Scenario(BaseModel):
    scenario_id: str
    title: str
    learning_objectives: list[str]
    persona_ref: str
    opening_situation: str
    success_criteria: list[str]
    max_turns: int = 12
    rubric_ref: str | None = None


class RubricCriterion(BaseModel):
    name: str
    description: str
    scale: str = "1-4"
    weight: float = 1.0


class Rubric(BaseModel):
    rubric_id: str
    version: int = 1
    criteria: list[RubricCriterion] = Field(default_factory=list)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_persona(path: Path) -> Persona:
    return Persona.model_validate(load_yaml(path))


def load_scenario(path: Path) -> Scenario:
    return Scenario.model_validate(load_yaml(path))


def load_rubric(path: Path) -> Rubric:
    return Rubric.model_validate(load_yaml(path))
