from __future__ import annotations

from typing import Any

from patient_sim.evaluation.rubric import Rubric, SessionEvaluation, TurnEvaluation


def aggregate_session_evaluation(
    rubric: Rubric,
    turn_evaluations: list[TurnEvaluation],
) -> SessionEvaluation:
    if not turn_evaluations:
        return SessionEvaluation(rubric_id=rubric.rubric_id, rubric_version=rubric.version)

    criteria = {c.name: c for c in rubric.criteria}
    sums: dict[str, int] = {name: 0 for name in criteria}
    counts: dict[str, int] = {name: 0 for name in criteria}
    all_feedback: list[str] = []
    all_flags: list[str] = []

    for ev in turn_evaluations:
        for name, score in ev.scores.items():
            if name in sums:
                sums[name] += int(score)
                counts[name] += 1
        if ev.feedback:
            all_feedback.append(ev.feedback)
        all_flags.extend(ev.flags or [])

    criteria_scores: dict[str, float] = {}
    for name in criteria:
        if counts[name]:
            criteria_scores[name] = sums[name] / counts[name]

    overall = sum(criteria_scores.values()) / max(len(criteria_scores), 1) if criteria_scores else None
    return SessionEvaluation(
        rubric_id=rubric.rubric_id,
        rubric_version=rubric.version,
        overall_score=overall,
        criteria_scores=criteria_scores,
        strengths=_infer_strengths(criteria_scores),
        improvements=_infer_improvements(criteria_scores),
        evidence=_top_feedback(all_feedback, max_items=5),
    )


def _infer_strengths(criteria_scores: dict[str, float], threshold: float = 3.0) -> list[str]:
    return [name for name, score in criteria_scores.items() if score >= threshold]


def _infer_improvements(criteria_scores: dict[str, float], threshold: float = 2.5) -> list[str]:
    return [name for name, score in criteria_scores.items() if score < threshold]


def _top_feedback(items: list[str], max_items: int = 5) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.strip()
        if key and key not in seen:
            seen.add(key)
            out.append(key)
            if len(out) >= max_items:
                break
    return out
