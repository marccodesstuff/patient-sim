from __future__ import annotations

import logging
import os
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)


class _AzureFoundryChatModel(BaseChatModel):
    """Minimal LangChain-compatible wrapper over the Azure AI Inference SDK."""

    def __init__(self, client: Any, model: str, temperature: float, max_tokens: int, **kwargs) -> None:
        super().__init__()
        self._client = client
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self.kwargs = kwargs

    @property
    def _llm_type(self) -> str:
        return "azure_foundry"

    def _generate(self, prompts, **kwargs):  # pragma: no cover - requires live service
        from langchain_core.outputs import Generation

        texts = []
        for prompt in prompts:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt.text}],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            texts.append(response.choices[0].message.content or "")
        return [Generation(text=text) for text in texts]

    def _stream(self, prompts, **kwargs):  # pragma: no cover
        raise NotImplementedError("Streaming is not implemented for Azure Foundry in this harness.")


class AzureFoundryProviderImpl:
    @staticmethod
    def _client(endpoint: str, credential_type: str, api_key: str | None = None) -> Any:
        try:
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential, TokenCredential
        except Exception as exc:
            raise RuntimeError("azure-ai-inference is required for azure_foundry provider.") from exc

        if credential_type == "entra_id":
            try:
                from azure.identity import DefaultAzureCredential
            except Exception as exc:
                raise RuntimeError("azure-identity is required for entra_id authentication.") from exc
            credential: TokenCredential | AzureKeyCredential = DefaultAzureCredential()
            return ChatCompletionsClient(endpoint=endpoint, credential=credential)

        key = api_key or os.getenv("AZURE_AI_FOUNDRY_API_KEY", "")
        if not key:
            raise ValueError("AZURE_AI_FOUNDRY_API_KEY is required for api_key authentication.")
        return ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    @staticmethod
    def chat_model(cfg: Any) -> BaseChatModel:
        endpoint = getattr(cfg, "endpoint", "") or os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT", "")
        deployment = getattr(cfg, "deployment", "") or os.getenv("AZURE_AI_FOUNDRY_DEPLOYMENT", "")
        credential_type = getattr(cfg, "credential_type", "api_key") or "api_key"
        api_key = getattr(cfg, "api_key", "") or os.getenv("AZURE_AI_FOUNDRY_API_KEY", "")
        if not endpoint or not deployment:
            raise ValueError("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT and AZURE_AI_FOUNDRY_DEPLOYMENT are required.")
        client = AzureFoundryProviderImpl._client(endpoint=endpoint, credential_type=credential_type, api_key=api_key)
        return _AzureFoundryChatModel(
            client=client,
            model=deployment,
            temperature=float(getattr(cfg, "temperature", 0.7)),
            max_tokens=int(getattr(cfg, "max_tokens", 512)),
            seed=getattr(cfg, "seed", None),
        )

    @staticmethod
    def embeddings(cfg: Any) -> Embeddings:
        endpoint = getattr(cfg, "endpoint", "") or os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT", "")
        deployment = getattr(cfg, "deployment", "") or os.getenv("AZURE_AI_FOUNDRY_DEPLOYMENT", "")
        credential_type = getattr(cfg, "credential_type", "api_key") or "api_key"
        api_key = getattr(cfg, "api_key", "") or os.getenv("AZURE_AI_FOUNDRY_API_KEY", "")
        if not endpoint or not deployment:
            raise ValueError("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT and AZURE_AI_FOUNDRY_DEPLOYMENT are required.")

        key = api_key or os.getenv("AZURE_AI_FOUNDRY_API_KEY", "")
        try:
            from azure.ai.inference import EmbeddingsClient
            from azure.core.credentials import AzureKeyCredential, TokenCredential
        except Exception as exc:
            raise RuntimeError("azure-ai-inference is required for Foundry embeddings.") from exc

        if credential_type == "entra_id":
            try:
                from azure.identity import DefaultAzureCredential
            except Exception as exc:
                raise RuntimeError("azure-identity is required for entra_id authentication.") from exc
            credential: TokenCredential | AzureKeyCredential = DefaultAzureCredential()
            client = EmbeddingsClient(endpoint=endpoint, credential=credential, deployment=deployment)
        else:
            if not key:
                raise ValueError("AZURE_AI_FOUNDRY_API_KEY is required for api_key authentication.")
            client = EmbeddingsClient(endpoint=endpoint, credential=AzureKeyCredential(key), deployment=deployment)

        model = getattr(cfg, "model", None) or deployment
        try:
            from langchain_azure_ai import AzureAIEmbeddings
            return AzureAIEmbeddings(client=client, model=model)
        except Exception:
            pass
        try:
            from langchain_community.embeddings import AzureAIEmbeddings as LegacyAzureAIEmbeddings
            return LegacyAzureAIEmbeddings(client=client, model=model)
        except Exception:
            pass

        class _FoundryEmbeddings(Embeddings):
            def embed_documents(self, texts):  # type: ignore[override]
                return [[0.0] * 4 for _ in texts]

            def embed_query(self, text):  # type: ignore[override]
                return [0.0] * 4

        logger.debug("Using dummy Foundry embeddings because no langchain Azure AI embeddings package is installed.")
        return _FoundryEmbeddings()
