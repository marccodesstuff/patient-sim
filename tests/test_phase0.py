from __future__ import annotations

import pytest


def test_defaults_are_sensible():
    from patient_sim.config.settings import get_settings

    s = get_settings()
    assert s.app_name == "PatientCommSim"
    assert s.patient_llm.provider == "openai"
    assert s.patient_llm.model == "gpt-4o"
    assert s.patient_llm.seed == 42
    assert s.judge_llm.provider == "openai"
    assert s.judge_llm.model == "gpt-4o"


def test_factory_imports():
    from patient_sim.models.factory import ModelProvider  # noqa: F401

    provider = ModelProvider()
    assert provider is not None
