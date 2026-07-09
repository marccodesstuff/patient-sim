from __future__ import annotations

from unittest.mock import patch

from patient_sim.config.settings import get_settings
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
