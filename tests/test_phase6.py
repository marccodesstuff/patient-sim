from __future__ import annotations

from pathlib import Path

import pytest

from patient_sim.personas.schemas import load_persona


def test_second_persona_loads():
    p = load_persona(Path("personas/cooperative_young_professional_hypertensive.yaml"))
    assert p.persona_id == "cooperative_young_professional_hypertensive"
    assert p.difficulty == "cooperative"
    assert p.demographics.age == 32
    assert len(p.knowledge_documents) >= 4


def test_second_persona_red_lines():
    p = load_persona(Path("personas/cooperative_young_professional_hypertensive.yaml"))
    flags = [r.flag for r in p.red_lines]
    assert "red_line_spiritual_boundary" in flags
    assert "red_line_safety_concern" in flags
