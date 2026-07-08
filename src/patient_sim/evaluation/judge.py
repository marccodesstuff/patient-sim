from __future__ import annotations

import json
from typing import Any, Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from patient_sim.config.settings import get_settings
from patient_sim.evaluation.rubric import Rubric, RubricCriterion, TurnEvaluation
from patient_sim.models.factory import ModelProvider


JUDGE_SYSTEM_PROMPT = """You are an evaluator for medical communication training.
Score the learner on each criterion using a 1-4 integer scale.
Return JSON only, with keys: scores, feedback, flags.
Example:
{{"scores":{"empathy":3,"clarity":4},"feedback":"...","flags":[]}}
"""


def rubric_to_text(rubric: Rubric) -> str:
    lines = [f"Rubric: {rubric.rubric_id} v{rubric.version}"]
    for item in rubric.criteria:
        lines.append(f"- {item.name}: {item.description} (scale={item.scale}, weight={item.weight})")
    return "\n".join(lines)


def build_judge_messages(rubric: Rubric, student_input: str, patient_turn: dict[str, Any], transcript_segment: str) -> list[BaseMessage]:
    rubric_text = rubric_to_text(rubric)
    patient_text = json.dumps(patient_turn, ensure_ascii=True)
    user_text = (
        f"RUBRIC:\n{rubric_text}\n\n"
        f"TRANSCRIPT_SEGMENT:\n{transcript_segment}\n\n"
        f"STUDENT_INPUT:\n{student_input}\n\n"
        f"PATIENT_TURN:\n{patient_text}\n\n"
        "Return JSON scores now."
    )
    return [SystemMessage(content=JUDGE_SYSTEM_PROMPT), HumanMessage(content=user_text)]


def call_judge(model: BaseChatModel, messages: Sequence[BaseMessage]) -> dict[str, Any]:
    response = model.invoke(list(messages))
    text = getattr(response, "content", str(response))
    try:
        return json.loads(text)
    except Exception:
        return {"scores": {}, "feedback": str(text)[:500], "flags": ["parse_failed"]}


def evaluate_turn(
    rubric: Rubric,
    *,
    student_input: str,
    patient_turn: dict[str, Any],
    transcript_segment: str,
    judge_model: BaseChatModel | None = None,
) -> TurnEvaluation:
    model = judge_model or ModelProvider(get_settings()).chat_model(for_patient=False)
    messages = build_judge_messages(rubric, student_input=student_input, patient_turn=patient_turn, transcript_segment=transcript_segment)
    result = call_judge(model, messages)
    scores = {str(k): int(v) for k, v in (result.get("scores") or {}).items() if str(v).isdigit()}
    return TurnEvaluation(
        turn_number=0,
        student_input=student_input,
        scores=scores,
        feedback=result.get("feedback", ""),
        flags=result.get("flags", []),
    )
