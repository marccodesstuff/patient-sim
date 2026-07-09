from __future__ import annotations

from patient_sim.config.settings import get_settings


def test_defaults_do_not_include_foundry():
    s = get_settings()
    assert s.patient_provider == "openai"
    assert s.judge_provider == "openai"


def test_foundry_settings_are_present():
    s = get_settings()
    assert hasattr(s, "azure_foundry_endpoint")
    assert hasattr(s, "azure_foundry_deployment")
    assert hasattr(s, "azure_foundry_api_key")


def test_foundry_factory_branch_importable():
    from patient_sim.models.factory import ModelProvider

    provider = ModelProvider()
    assert "azure_foundry" in provider._impls
