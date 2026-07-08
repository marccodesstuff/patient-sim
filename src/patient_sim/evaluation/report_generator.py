from __future__ import annotations

import json

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from patient_sim.evaluation.report import aggregate_session_evaluation
from patient_sim.evaluation.rubric import Rubric, RubricCriterion, TurnEvaluation


def build_report_prompt(rubric: Rubric, session_eval: Any, transcript_segments: list[str]) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", "You are an instructor report generator for clinical communication training."),
        ("user", "RUBRIC:\n{rubric}\n\nEVALUATION:\n{evaluation}\n\nTRANSCRIPT:\n{transcript}\n\nWrite a concise end-of-session report with scores, strengths, improvements, and 2-3 highlights from the transcript."),
    ]).partial(
        rubric="\n".join([f"- {c.name}: {c.description}" for c in rubric.criteria]),
        evaluation=json.dumps(session_eval.model_dump(), ensure_ascii=False, default=str),
        transcript="\n".join(transcript_segments[-6:]),
    )


def render_session_report(model: BaseChatModel, rubric: Rubric, session_eval: Any, transcript_segments: list[str]) -> str:
    prompt = build_report_prompt(rubric, session_eval, transcript_segments)
    chain = prompt | model | StrOutputParser()
    return chain.invoke({})


def build_session_evaluation(rubric: Rubric, turn_evaluations: list[TurnEvaluation]):
    return aggregate_session_evaluation(rubric, turn_evaluations)
