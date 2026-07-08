from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from patient_sim.personas.schemas import Persona, load_persona, load_scenario
from patient_sim.rag.ingestor import chunk_docs, load_knowledge_docs
from patient_sim.retriever_factory import load_persona_from_file
import patient_sim.rag.ingestor as ingestor


class FakeEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[0.0] * 4 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 4


def test_sample_persona_loads():
    p = load_persona_from_file("personas/anxious_newly_diagnosed_diabetic.yaml")
    assert p.persona_id == "anxious_newly_diagnosed_diabetic"
    assert p.difficulty == "distressed"
    assert "fears going blind like her mother" in p.hidden_concerns
    assert len(p.knowledge_documents) > 0
    assert len(p.red_lines) == 2


def test_sample_scenario_loads():
    s = load_scenario(Path("personas/first_visit_new_diagnosis.yaml"))
    assert s.scenario_id == "first_visit_new_diagnosis"
    assert s.persona_ref == "anxious_newly_diagnosed_diabetic"
    assert s.max_turns >= 1
    assert len(s.learning_objectives) > 0


def test_knowledge_docs_loaded():
    p = load_persona_from_file("personas/anxious_newly_diagnosed_diabetic.yaml")
    docs = load_knowledge_docs(p)
    assert len(docs) == len(p.knowledge_documents)
    assert all(d.metadata["persona_id"] == p.persona_id for d in docs)


def test_chunk_docs_produces_chunks():
    docs = [Document(page_content="word " * 500)]
    chunks = chunk_docs(docs, chunk_size=50, chunk_overlap=10)
    assert len(chunks) >= 1


def test_rag_ingestor_importable():
    from patient_sim.rag import chunk_docs, get_retriever


def test_build_vector_store_tmp(tmp_path):
    persona = load_persona_from_file("personas/anxious_newly_diagnosed_diabetic.yaml")
    docs = chunk_docs(load_knowledge_docs(persona))
    store = ingestor.build_vector_store(
        docs,
        embeddings=FakeEmbeddings(),
        persist_directory=str(tmp_path),
    )
    assert isinstance(store, VectorStore)
    retriever = ingestor.get_retriever(store, k=2)
    results = retriever.invoke("diabetes")
    assert isinstance(results, list)
    assert len(results) <= 2
    assert all(isinstance(doc, Document) for doc in results)
