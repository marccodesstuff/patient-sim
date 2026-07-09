from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FoundryEvaluationResult(BaseModel):
    groundedness: float | None = None
    relevance: float | None = None
    coherence: float | None = None
    raw: dict[str, Any] | None = None


class FoundryEvaluationAdapter:
    """Optional additive pass using Azure AI Foundry Evaluation SDK.

    If the SDK is unavailable or the project is not configured, the adapter
    returns a no-op result so the existing rubric judge remains the source of truth.
    """

    @staticmethod
    def evaluate(*, rubric_scores: dict[str, Any], patient_turn: dict[str, Any], student_message: str) -> FoundryEvaluationResult:
        try:
            from azure.ai.evaluation import evaluate
        except Exception as exc:
            logger.debug("Azure AI Evaluation SDK unavailable: %s", exc)
            return FoundryEvaluationResult()

        try:
            result = evaluate(
                query=student_message,
                response=patient_turn.get("patient_utterance", ""),
                context="\n".join(patient_turn.get("retrieval_citations", [])),
            )
            return FoundryEvaluationResult(
                groundedness=result.get("groundedness"),
                relevance=result.get("relevance"),
                coherence=result.get("coherence"),
                raw=result,
            )
        except Exception as exc:
            logger.debug("Foundry evaluation failed: %s", exc)
            return FoundryEvaluationResult()
