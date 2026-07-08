from __future__ import annotations

from typing import Any

import pytest

from patient_sim.evaluation.judge import build_judge_messages, evaluate_turn, rubric_to_text
from patient_sim.evaluation.report import aggregate_session_evaluation
from patient_sim.evaluation.report_generator import build_report_prompt
from patient_sim.evaluation.rubric import Rubric, RubricCriterion, TurnEvaluation


class DummyChatModel:
    def invoke(self, prompt, config=None, **kwargs):
        return '{"scores":{"empathy":3,"clarity":4},"feedback":"Good opening.","flags":[]}'


def test_rubric_to_text_lists_criteria():
    rubric = Rubric(rubric_id="r1", criteria=[RubricCriterion(name="empathy", description="Show empathy")])
    text = rubric_to_text(rubric)
    assert "Rubric: r1" in text
    assert "empathy" in text


def test_evaluate_turn_returns_parsed_scores():
    rubric = Rubric(rubric_id="r1", criteria=[RubricCriterion(name="empathy", description="Show empathy")])
    fake_model = DummyChatModel()
    ev = evaluate_turn(
        rubric,
        student_input="I understand this is scary.",
        patient_turn={"patient_utterance": "It is scary."},
        transcript_segment="Student: ...\nPatient: ...",
        judge_model=fake_model,
    )
    assert isinstance(ev, TurnEvaluation)
    assert ev.scores.get("empathy") == 3


def test_aggregate_session_evaluation_computes_overall():
    rubric = Rubric(
        rubric_id="r1",
        version=1,
        criteria=[
            RubricCriterion(name="empathy", description="Show empathy"),
            RubricCriterion(name="clarity", description="Clear language"),
        ],
    )
    evs = [
        TurnEvaluation(turn_number=1, student_input="", scores={"empathy": 3, "clarity": 4}, feedback="Great empathy"),
        TurnEvaluation(turn_number=2, student_input="", scores={"empathy": 2, "clarity": 3}, feedback="A bit more empathy"),
    ]
    session = aggregate_session_evaluation(rubric, evs)
    assert session.overall_score is not None
    assert session.rubric_id == "r1"


def test_build_report_prompt_is_callable():
    rubric = Rubric(rubric_id="r1", criteria=[RubricCriterion(name="empathy", description="Show empathy")])
    prompt = build_report_prompt(rubric, aggregate_session_evaluation(rubric, []), ["Student: hi\nPatient: hello"])
    assert prompt is not None
