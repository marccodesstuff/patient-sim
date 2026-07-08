from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

from patient_sim.schemas import PatientTurn
from patient_sim.prompts.patient_system import PATIENT_SYSTEM_V1, PATIENT_SYSTEM_PROMPT_VERSION

FORMAT_INSTRUCTIONS = (
    "Respond as the patient. "
    "Use XML-like tags: <response>, <emotional_state>, <revealed_facts>, "
    "<internal_notes>, <flags>, <citations>."
)


class VersionedPrompts:
    def __init__(self) -> None:
        self._current_version = PATIENT_SYSTEM_PROMPT_VERSION

    @property
    def current_version(self) -> str:
        return self._current_version

    def build_prompt(self, *, retrieved_context: str, conversation_summary: str, student_message: str) -> ChatPromptTemplate:
        human_template = (
            "PERSONA/CONTEXT:\n{context}\n\n"
            "CONVERSATION SUMMARY (so far):\n{summary}\n\n"
            "STUDENT MESSAGE:\n{student}\n\n"
            "Remember to respond in the persona's voice and keep grounded in the provided context.\n"
            "{format_instructions}\n"
        )
        system = SystemMessage(content=PATIENT_SYSTEM_V1)
        human = HumanMessage(
            content=human_template,
        )
        return ChatPromptTemplate.from_messages([system, human]).partial(
            context=retrieved_context,
            summary=conversation_summary,
            student=student_message,
            format_instructions=FORMAT_INSTRUCTIONS,
        )

    def chain(self, model: BaseChatModel) -> Runnable:
        prompt = self.build_prompt(
            retrieved_context="",
            conversation_summary="",
            student_message="",
        )
        return prompt | model | StrOutputParser()
