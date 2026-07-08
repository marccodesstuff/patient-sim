from __future__ import annotations

import logging
import re
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

from patient_sim.graph.state import ConversationState
from patient_sim.graph.prompts import VersionedPrompts
from patient_sim.schemas import PatientTurn

logger = logging.getLogger(__name__)


class PromptBuilder:
    def __init__(self, prompts: Any | None = None) -> None:
        self.prompts = prompts or VersionedPrompts()

    def build_prompt(self, *, retrieved_context: str, conversation_summary: str, student_message: str):
        return self.prompts.build_prompt(
            retrieved_context=retrieved_context,
            conversation_summary=conversation_summary,
            student_message=student_message,
        )


class PatientTurnParser:
    def parse(self, text: str, *, citations: list[str]) -> PatientTurn:
        return self._parse_regex(text=text, citations=citations)

    def _parse_regex(self, *, text: str, citations: list[str]) -> PatientTurn:
        utterance = ""
        m = re.search(r"<response>(.*?)</response>", text, re.S)
        if m:
            utterance = m.group(1).strip()
        if not utterance:
            utterance = re.sub(r"<[^>]+>", "", text).strip() or text[:500]

        emotional_state = self._block(text, "emotional_state") or "neutral"
        raw_facts = self._block_list(text, "revealed_facts")
        raw_notes = self._block(text, "internal_notes") or ""
        raw_flags = self._block_list(text, "flags")

        return PatientTurn(
            patient_utterance=utterance,
            emotional_state=emotional_state,
            revealed_facts=raw_facts,
            internal_notes=raw_notes,
            flags=raw_flags if raw_flags else [],
            retrieval_citations=citations,
        )

    def _block(self, text: str, name: str) -> str:
        m = re.search(rf"<{name}>(.*?)</{name}>", text, re.S)
        return m.group(1).strip() if m else ""

    def _block_list(self, text: str, name: str) -> list[str]:
        block = self._block(text, name)
        items = [line.strip("- ") for line in block.splitlines() if line.strip()]
        return [item for item in items if item]


def parse_patient_turn(text: str, citations: list[str]) -> PatientTurn:
    parser = PatientTurnParser()
    return parser.parse(text, citations=citations)
