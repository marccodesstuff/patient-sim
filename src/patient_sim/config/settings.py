from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class _ProviderConfig(BaseModel):
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, gt=0)
    seed: int | None = Field(default=42)


class _EmbeddingConfig(BaseModel):
    provider: str = Field(default="openai")
    model: str = Field(default="text-embedding-3-small")


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
    langsmith_api_key: str = Field(default="", alias="LANGSMITH_API_KEY")
    langsmith_tracing: str = Field(default="false", alias="LANGSMITH_TRACING")
    langsmith_project: str = Field(default="patient-sim", alias="LANGSMITH_PROJECT")
    chroma_persist_dir: str = Field(default=".chroma", alias="CHROMA_PERSIST_DIR")

    @property
    def patient_llm(self) -> _ProviderConfig:
        return _ProviderConfig(
            provider=self.patient_provider,
            model=self.patient_model,
            temperature=self.patient_temperature,
            max_tokens=self.patient_max_tokens,
            seed=self.patient_seed,
        )

    @property
    def judge_llm(self) -> _ProviderConfig:
        return _ProviderConfig(
            provider=self.judge_provider,
            model=self.judge_model,
            temperature=self.judge_temperature,
            max_tokens=self.judge_max_tokens,
            seed=None,
        )

    @property
    def embedding(self) -> _EmbeddingConfig:
        return _EmbeddingConfig(
            provider=self.embedding_provider,
            model=self.embedding_model,
        )


def get_settings() -> Settings:
    return Settings()
