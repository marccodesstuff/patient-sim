from __future__ import annotations

from pathlib import Path

from patient_sim.models.factory import ModelProvider
from patient_sim.rag.ingestor import ingest_persona
from patient_sim.personas.schemas import Persona
from patient_sim.personas.schemas import load_persona


def load_persona_from_file(path: str) -> Persona:
    return load_persona(Path(path))


def create_retriever_for_persona(persona: Persona, settings=None):
    provider = ModelProvider(settings)
    embeddings = provider.embeddings()
    return ingest_persona(persona, embeddings=embeddings, settings=settings)


def build_retriever_for_persona(persona: Persona, settings=None):
    from patient_sim.rag.ingestor import get_retriever

    vector_store = create_retriever_for_persona(persona, settings=settings)
    return get_retriever(vector_store)
