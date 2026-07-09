from __future__ import annotations

import sys
from unittest.mock import patch

from patient_sim.evaluation.foundry_evaluator import FoundryEvaluationAdapter, FoundryEvaluationResult


def test_foundry_evaluator_noop_when_sdk_missing():
    result = FoundryEvaluationAdapter.evaluate(
        rubric_scores={},
        patient_turn={"patient_utterance": "I'm okay.", "retrieval_citations": []},
        student_message="How do you feel?",
    )
    assert isinstance(result, FoundryEvaluationResult)
    assert result.groundedness is None
    assert result.relevance is None
    assert result.coherence is None


def test_foundry_evaluator_handles_runtime_error():
    with patch.dict("sys.modules", {"azure.ai.evaluation": None}):
        try:
            result = FoundryEvaluationAdapter.evaluate(
                rubric_scores={},
                patient_turn={"patient_utterance": "I'm okay.", "retrieval_citations": []},
                student_message="How do you feel?",
            )
            assert result.raw is None
        finally:
            pass
