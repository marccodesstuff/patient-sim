from __future__ import annotations

import pytest

from patient_sim.state_store import (
    RedLineHandler,
    apply_safe_branch,
    append_history,
    difficulty_multiplier,
    rolling_summary,
    update_emotional_state,
    update_revealed_facts,
)


def test_rolling_summary_truncates_to_recent():
    history = [{"student": f"s{i}", "patient": f"p{i}"} for i in range(10)]
    out = rolling_summary(history)
    assert out.count("Student:") == 6
    assert "Student: s4" in out
    assert "Student: s0" not in out


def test_append_history_increments_turn_number():
    state = {
        "conversation_history": [],
        "conversation_summary": "",
        "turn_number": 0,
        "current_patient_turn": {
            "patient_utterance": "I'm worried.",
            "emotional_state": "anxious",
            "flags": [],
        },
        "student_message": "How are you?",
    }
    out = append_history(state)
    assert out["turn_number"] == 1
    assert len(out["conversation_history"]) == 1
    assert "worried" in out["conversation_summary"]


def test_update_revealed_facts_accumulates_without_duplicates():
    state = {
        "revealed_facts": ["takes metformin"],
        "current_patient_turn": {
            "revealed_facts": ["takes metformin", "worried about side effects"],
        },
    }
    out = update_revealed_facts(state)
    assert out["revealed_facts"] == ["takes metformin", "worried about side effects"]


def test_update_emotional_state_prefers_current_turn():
    state = {
        "emotional_state": "neutral",
        "current_patient_turn": {"emotional_state": "anxious"},
    }
    out = update_emotional_state(state)
    assert out["emotional_state"] == "anxious"


def test_red_line_handler_matches_topic():
    handler = RedLineHandler([
        {"topic": "self-harm", "safe_response": "I need help.", "flag": "red_line_safety"},
        {"topic": "spiritual", "safe_response": "Not now.", "flag": "red_line_spiritual"},
    ])
    match = handler.check("I'm having thoughts of self-harm.")
    assert match is not None
    assert match["flag"] == "red_line_safety"
    assert match["safe_response"] == "I need help."


def test_apply_safe_branch_returns_scripted_reply():
    state: dict = {
        "emotional_state": "anxious",
        "current_patient_turn": None,
        "flags": [],
        "is_red_line": False,
        "red_line_topic": None,
    }
    override = {"safe_response": "I prefer not to talk about that right now.", "flag": "red_line_spiritual_boundary", "topic": "spiritual rejection"}
    out = apply_safe_branch(state, red_line_override=override)
    assert out["is_red_line"] is True
    assert out["current_patient_turn"]["patient_utterance"] == "I prefer not to talk about that right now."
    assert out["flags"] == ["red_line_spiritual_boundary"]


def test_difficulty_multiplier_values():
    vals = difficulty_multiplier("distressed")
    assert vals["disclosure"] < 0.5
    assert vals["affect"] > 1.0
