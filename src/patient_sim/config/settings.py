from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _ProviderConfig(BaseModel):
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, gt=0)
    seed: int | None = Field(default=42)
    endpoint: str = Field(default="")
    deployment: str = Field(default="")
    credential_type: str = Field(default="api_key")
    api_key: str = Field(default="")


class _EmbeddingConfig(BaseModel):
    provider: str = Field(default="openai")
    model: str = Field(default="text-embedding-3-small")
    endpoint: str = Field(default="")
    deployment: str = Field(default="")
    credential_type: str = Field(default="api_key")
    api_key: str = Field(default="")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")
    app_name: str = Field(default="PatientCommSim")
    log_level: str = Field(default="INFO")
    patient_provider: str = Field(default="openai", alias="PATIENT_PROVIDER")
    patient_model: str = Field(default="gpt-4o", alias="PATIENT_MODEL")
    patient_temperature: float = Field(default=0.7, alias="PATIENT_TEMPERATURE")
    patient_max_tokens: int = Field(default=512, alias="PATIENT_MAX_TOKENS")
    patient_seed: int | None = Field(default=42, alias="PATIENT_SEED")
    judge_provider: str = Field(default="openai", alias="JUDGE_PROVIDER")
    judge_model: str = Field(default="gpt-4o", alias="JUDGE_MODEL")
    judge_temperature: float = Field(default=0.1, alias="JUDGE_TEMPERATURE")
    judge_max_tokens: int = Field(default=1024, alias="JUDGE_MAX_TOKENS")
    embedding_provider: str = Field(default="openai", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    azure_foundry_endpoint: str = Field(default="", alias="AZURE_AI_FOUNDRY_PROJECT_ENDPOINT")
    azure_foundry_deployment: str = Field(default="", alias="AZURE_AI_FOUNDRY_DEPLOYMENT")
    azure_foundry_api_key: str = Field(default="", alias="AZURE_AI_FOUNDRY_API_KEY")
    langsmith_api_key: str = Field(default="", alias="LANGSMITH_API_KEY")
    langsmith_tracing: str = Field(default="false", alias="LANGSMITH_TRACING")
    langsmith_project: str = Field(default="patient-sim", alias="LANGSMITH_PROJECT")
    chroma_persist_dir: str = Field(default=".chroma", alias="CHROMA_PERSIST_DIR")
    database_url: str = Field(
        default="postgresql+psycopg://postgres@localhost:5432/patient_sim",
        alias="DATABASE_URL",
    )
    posthog_project_token: str = Field(default="", alias="POSTHOG_PROJECT_TOKEN")
    posthog_host: str = Field(default="https://us.i.posthog.com", alias="POSTHOG_HOST")
    posthog_disabled: bool = Field(default=False, alias="POSTHOG_DISABLED")

    @property
    def _foundry_common(self) -> dict[str, Any]:
        return {
            "endpoint": self.azure_foundry_endpoint,
            "deployment": self.azure_foundry_deployment,
            "credential_type": "api_key",
            "api_key": self.azure_foundry_api_key,
        }

    @property
    def patient_llm(self) -> _ProviderConfig:
        data: dict[str, Any] = dict(
            provider=self.patient_provider,
            model=self.patient_model,
            temperature=self.patient_temperature,
            max_tokens=self.patient_max_tokens,
            seed=self.patient_seed,
        )
        if self.patient_provider == "azure_foundry":
            data.update(self._foundry_common)
        return _ProviderConfig(**data)

    @property
    def judge_llm(self) -> _ProviderConfig:
        data: dict[str, Any] = dict(
            provider=self.judge_provider,
            model=self.judge_model,
            temperature=self.judge_temperature,
            max_tokens=self.judge_max_tokens,
            seed=None,
        )
        if self.judge_provider == "azure_foundry":
            data.update(self._foundry_common)
        return _ProviderConfig(**data)

    @property
    def embedding(self) -> _EmbeddingConfig:
        data: dict[str, Any] = dict(
            provider=self.embedding_provider,
            model=self.embedding_model,
        )
        if self.embedding_provider == "azure_foundry":
            data.update(self._foundry_common)
        return _EmbeddingConfig(**data)


def get_settings() -> Settings:
    return Settings()
