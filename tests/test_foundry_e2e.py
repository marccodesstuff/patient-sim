from __future__ import annotations

from typing import Any
from unittest.mock import patch

from patient_sim.config.settings import get_settings
from patient_sim.graph.nodes import parse_structured, update_state
from patient_sim.graph.parser import parse_patient_turn
from patient_sim.models.factory import ModelProvider
from patient_sim.models.azure_foundry_provider import AzureFoundryProviderImpl


def test_foundry_provider_factory_uses_foundry_impl():
    settings = get_settings()
    settings.patient_provider = "azure_foundry"
    settings.patient_model = "azure-deployment"
    settings.azure_foundry_endpoint = "https://example.inference.ai.azure.com"
    settings.azure_foundry_deployment = "azure-deployment"

    provider = ModelProvider(settings=settings)
    with patch.object(AzureFoundryProviderImpl, "chat_model", return_value="mocked-model") as mock_chat:
        model = provider.chat_model(for_patient=True)
        assert mock_chat.called


def test_foundry_flow_reaches_parser_and_state():
    settings = get_settings()
    settings.patient_provider = "azure_foundry"
    settings.patient_model = "azure-deployment"
    settings.patient_temperature = 0.0
    settings.patient_max_tokens = 64
    settings.patient_seed = 7
    settings.azure_foundry_endpoint = "https://example.inference.ai.azure.com"
    settings.azure_foundry_deployment = "azure-deployment"

    canned = (
        "<response>I'm okay.</response>\n"
        "<emotional_state>anxious</emotional_state>\n"
        "<revealed_facts>\n</revealed_facts>\n"
        "<internal_notes></internal_notes>\n"
        "<flags>\n</flags>\n"
    )

    class _FakeChatModel:
        def invoke(self, _prompt, **_kwargs):
            return canned

    with patch.object(ModelProvider, "chat_model", return_value=_FakeChatModel()):
        state: dict[str, Any] = {
            "session_id": "foundry-1",
            "scenario_id": "first_visit_new_diagnosis",
            "persona_id": "anxious_newly_diagnosed_diabetic",
            "turn_number": 0,
            "max_turns": 3,
            "seed": 7,
            "difficulty": "distressed",
            "student_message": "Can you tell me how you feel about the diagnosis?",
            "retrieved_chunks": [],
            "conversation_history": [],
            "conversation_summary": "",
            "emotional_state": "anxious",
            "revealed_facts": [],
            "flags": [],
            "current_patient_turn": None,
            "is_red_line": False,
            "red_line_topic": None,
            "next": None,
        }
        state["current_patient_turn"] = parse_patient_turn(canned, citations=[]).model_dump()
        state = parse_structured(state)
        state = update_state(state)
    assert state["current_patient_turn"]["patient_utterance"].startswith("I'm okay")
    assert state["turn_number"] == 1
    assert state["conversation_history"][-1]["patient"].startswith("I'm okay")


def test_mixed_provider_config():
    settings = get_settings()
    settings.patient_provider = "azure_foundry"
    settings.patient_model = "patient-deployment"
    settings.azure_foundry_endpoint = "https://example.inference.ai.azure.com"
    settings.azure_foundry_deployment = "patient-deployment"
    settings.judge_provider = "anthropic"
    settings.judge_model = "claude-3-5-haiku-20241022"

    provider = ModelProvider(settings=settings)
    patient_cfg = settings.patient_llm
    judge_cfg = settings.judge_llm
    assert patient_cfg.provider == "azure_foundry"
    assert patient_cfg.deployment == "patient-deployment"
    assert judge_cfg.provider == "anthropic"
