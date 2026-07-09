from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from langchain_core.embeddings import Embeddings

from patient_sim.config.settings import get_settings
from patient_sim.models.factory import ModelProvider
from patient_sim.models.azure_foundry_provider import AzureFoundryProviderImpl
from patient_sim.retriever_factory import create_retriever_for_persona
from patient_sim.personas.schemas import load_persona


class _MockEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[0.0] * 4 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 4


def test_foundry_embeddings_can_be_created():
    settings = get_settings()
    settings.embedding_provider = "azure_foundry"
    settings.embedding_model = "text-embedding-3-large"
    settings.azure_foundry_endpoint = "https://example.inference.ai.azure.com"
    settings.azure_foundry_deployment = "text-embedding-3-large"
    settings.azure_foundry_api_key = "fake-key"

    provider = ModelProvider(settings=settings)
    with patch.object(AzureFoundryProviderImpl, "embeddings", return_value=_MockEmbeddings()) as mock_embeddings:
        embeddings = provider.embeddings()
        assert mock_embeddings.called
        assert isinstance(embeddings, Embeddings)


def test_foundry_retriever_factory_uses_foundry_embeddings():
    settings = get_settings()
    settings.embedding_provider = "azure_foundry"
    settings.embedding_model = "text-embedding-3-large"
    settings.azure_foundry_endpoint = "https://example.inference.ai.azure.com"
    settings.azure_foundry_deployment = "text-embedding-3-large"
    settings.azure_foundry_api_key = "fake-key"

    persona = load_persona(Path("personas/anxious_newly_diagnosed_diabetic.yaml"))
    with patch.object(AzureFoundryProviderImpl, "embeddings", return_value=_MockEmbeddings()) as mock_embeddings:
        vector_store = create_retriever_for_persona(persona, settings=settings)
        assert mock_embeddings.called
        assert hasattr(vector_store, "as_retriever")
