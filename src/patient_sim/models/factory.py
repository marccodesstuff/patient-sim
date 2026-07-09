from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from patient_sim.config.settings import _ProviderConfig, get_settings
from patient_sim.models.anthropic_provider import AnthropicProviderImpl
from patient_sim.models.azure_foundry_provider import AzureFoundryProviderImpl
from patient_sim.models.openai_provider import OpenAIProviderImpl


class ModelProvider:
    def __init__(self, settings: Any | None = None) -> None:
        self.settings = settings or get_settings()
        self._impls = {
            "openai": OpenAIProviderImpl,
            "anthropic": AnthropicProviderImpl,
            "azure_foundry": AzureFoundryProviderImpl,
            }

    def chat_model(self, *, for_patient: bool = True) -> BaseChatModel:
        cfg = self.settings.patient_llm if for_patient else self.settings.judge_llm
        return self._build(cfg, role="patient" if for_patient else "judge")

    def embeddings(self) -> Embeddings:
        cfg = self.settings.embedding
        impl = self._impls.get(cfg.provider)
        if impl is None:
            raise ValueError(f"Unsupported embedding provider: {cfg.provider}")
        return impl.embeddings(cfg)

    def _build(self, cfg: _ProviderConfig, role: str) -> BaseChatModel:
        impl = self._impls.get(cfg.provider)
        if impl is None:
            raise ValueError(f"Unsupported provider: {cfg.provider}")
        return impl.chat_model(cfg)
