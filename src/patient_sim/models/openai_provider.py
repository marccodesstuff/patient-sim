from __future__ import annotations

import logging
import os
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

logger = logging.getLogger(__name__)


class OpenAIProviderImpl:
    @staticmethod
    def chat_model(cfg: Any) -> BaseChatModel:
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY is required for openai provider.")
        logger.debug("ChatOpenAI: model=%s", cfg.model)
        return ChatOpenAI(
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            seed=cfg.seed,
        )

    @staticmethod
    def embeddings(cfg: Any) -> Embeddings:
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY is required for openai embeddings.")
        logger.debug("OpenAIEmbeddings: model=%s", cfg.model)
        return OpenAIEmbeddings(model=cfg.model)
