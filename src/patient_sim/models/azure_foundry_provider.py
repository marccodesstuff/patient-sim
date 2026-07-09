from __future__ import annotations

import logging
import os
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)


class AzureFoundryProviderImpl:
    @staticmethod
    def _cohere_embed(cfg: Any) -> Embeddings:
        try:
            from langchain_cohere import CohereEmbeddings
            return CohereEmbeddings(model=cfg.model)
        except Exception as exc:  # pragma: no cover - optional path
            logger.debug("Cohere embeddings unavailable: %s", exc)
        try:
            from langchain_community.embeddings import CohereEmbeddings as LegacyCohereEmbeddings
            return LegacyCohereEmbeddings(model=cfg.model)
        except Exception as exc:
            logger.debug("Legacy Cohere embeddings unavailable: %s", exc)
        try:
            from langchain_core.embeddings import Embeddings

            class _AzureFoundryDummyEmbeddings(Embeddings):
                def embed_documents(self, texts):
                    return [[0.0] * 4 for _ in texts]

                def embed_query(self, text):
                    return [0.0] * 4

            return _AzureFoundryDummyEmbeddings()
        except Exception as exc:
            raise RuntimeError("No usable Azure Foundry embeddings implementation is available.") from exc

    @staticmethod
    def chat_model(cfg: Any) -> BaseChatModel:
        raise NotImplementedError("Azure Foundry chat wiring is not yet implemented.")

    @staticmethod
    def embeddings(cfg: Any) -> Embeddings:
        return AzureFoundryProviderImpl._cohere_embed(cfg)
