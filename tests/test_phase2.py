from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from patient_sim.graph.graph import build_graph
from patient_sim.graph.nodes import input_guard, retrieve, respond, parse_structured, update_state, evaluate_turn, log_turn
from patient_sim.graph.parser import parse_patient_turn
from patient_sim.graph.prompts import VersionedPrompts
from patient_sim.graph.state import ConversationState
from patient_sim.retriever_factory import load_persona_from_file
from patient_sim.schemas import PatientTurn


class DeterministicChatModel(BaseChatModel):
    def __init__(self, response_text: str = "Hello, I'm the patient."):
        super().__init__()
        self._response_text = response_text

    @property
    def _llm_type(self) -> str:
        return "deterministic-chat"

    def _generate(self, prompts, stop=None, run_manager=None, **kwargs):
        texts = []
        for prompt in prompts:
            texts.append(self._response_text)
        response = AIMessage(content="\n".join(texts))
        from langchain_core.outputs import LLMResult

        return LLMResult(generations=[[response]])

    def _call(self, prompt: str, stop=None, run_manager=None, **kwargs) -> str:
        return self._response_text

    def invoke(self, prompt, config=None, **kwargs):
        return self._call(str(prompt))


class DeterministicEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[0.0, 1.0, 2.0, 3.0] for _ in texts]

    def embed_query(self, text):
        return [0.0, 1.0, 2.0, 3.0]


def test_graph_node_respond_produces_structured_patient_turn():
    raw = """<response>
I'm okay, just worried about the medicine.
</response>

<emotional_state>
anxious but trying to stay calm
</emotional_state>

<revealed_facts>
- takes metformin
- worried about side effects
</revealed_facts>

<internal_notes>
She is more likely to open up if asked about specific symptoms.
</internal_notes>

<flags>
- patient_expresses_anxiety
</flags>

<citations>
- persona_background.md
- condition_summary.md
</citations>
"""
    citations = ["persona_background.md", "condition_summary.md"]
    turn = parse_patient_turn(raw, citations)
    assert isinstance(turn, PatientTurn)
    assert "worried about the medicine" in turn.patient_utterance
    assert "anxious" in turn.emotional_state
    assert "takes metformin" in turn.revealed_facts
    assert turn.internal_notes
    assert "patient_expresses_anxiety" in turn.flags
    assert turn.retrieval_citations == citations


def test_parser_fallback_when_malformed():
    raw = "This is just free-form text without tags."
    turn = parse_patient_turn(raw, [])
    assert isinstance(turn, PatientTurn)
    assert turn.patient_utterance.strip()


def test_graph_compiles_and_runs_single_turn():
    graph = build_graph()
    deterministic_text = """<response>
I'm okay, just worried about the medicine.
</response>

<emotional_state>
anxious but trying to stay calm
</emotional_state>

<revealed_facts>
- takes metformin
- worried about side effects
</revealed_facts>

<internal_notes>
She is more likely to open up if asked about specific symptoms.
</internal_notes>

<flags>
- patient_expresses_anxiety
</flags>

<citations>
- persona_background.md
- condition_summary.md
</citations>
"""
    fake_model = DeterministicChatModel(response_text=deterministic_text)
    state: ConversationState = {
        "session_id": "test-1",
        "scenario_id": "first_visit_new_diagnosis",
        "persona_id": "anxious_newly_diagnosed_diabetic",
        "turn_number": 0,
        "max_turns": 3,
        "seed": 42,
        "difficulty": "distressed",
        "student_message": "Hi Maria, how are you feeling about starting the medication?",
        "retrieved_chunks": ["Maria is anxious about metformin side effects."],
        "conversation_history": [],
        "conversation_summary": "",
        "emotional_state": "anxious and somber",
        "revealed_facts": [],
        "flags": [],
        "current_patient_turn": None,
        "is_red_line": False,
        "red_line_topic": None,
        "next": None,
        "_model_override": fake_model,
    }
    state = retrieve(state, retriever=None, k=2)
    model = state.pop("_model_override", None) or fake_model
    state = respond(state, model=model)

    assert "current_patient_turn" in state
    assert state["current_patient_turn"] is not None
    assert isinstance(state["current_patient_turn"], dict)
    assert "patient_utterance" in state["current_patient_turn"]
    assert "emotional_state" in state["current_patient_turn"]
    assert "revealed_facts" in state["current_patient_turn"]
    assert "flags" in state["current_patient_turn"]

def test_versioned_prompts_emit_version():
    vp = VersionedPrompts()
    assert vp.current_version == "v1-2026-07-08"


def test_respond_maybe_end_session_on_empty_input():
    state: ConversationState = {
        "session_id": "test-2",
        "scenario_id": "first_visit_new_diagnosis",
        "persona_id": "anxious_newly_diagnosed_diabetic",
        "turn_number": 0,
        "max_turns": 3,
        "seed": 42,
        "difficulty": "distressed",
        "student_message": " ",
        "retrieved_chunks": [],
        "conversation_history": [],
        "conversation_summary": "",
        "emotional_state": "anxious and somber",
        "revealed_facts": [],
        "flags": [],
        "current_patient_turn": None,
        "is_red_line": False,
        "red_line_topic": None,
        "next": None,
    }
    state = input_guard(state)
    assert state.get("next") == "end_session"
