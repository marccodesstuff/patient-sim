from __future__ import annotations

import logging
import os
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_anthropic import ChatAnthropic

logger = logging.getLogger(__name__)


class AnthropicProviderImpl:
    @staticmethod
    def chat_model(cfg: Any) -> BaseChatModel:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise EnvironmentError("ANTHROPIC_API_KEY is required for anthropic provider.")
        logger.debug("ChatAnthropic: model=%s", cfg.model)
        return ChatAnthropic(
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
        )

    @staticmethod
    def embeddings(cfg: Any) -> Embeddings:
        raise NotImplementedError("Anthropic embeddings not implemented in this build; use openai for embeddings.")
