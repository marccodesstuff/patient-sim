from __future__ import annotations

from pathlib import Path
from typing import Sequence

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from patient_sim.config.settings import get_settings
from patient_sim.personas.schemas import Persona


def load_knowledge_docs(persona: Persona, root: str = "personas") -> list[Document]:
    docs: list[Document] = []
    for rel in persona.knowledge_documents:
        path = f"{root}/knowledge/{rel}"
        try:
            text = Path(path).read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "persona_id": persona.persona_id,
                    "source": rel,
                    "version": str(persona.version),
                },
            )
        )
    return docs


def _get_splitter(chunk_size: int = 300, chunk_overlap: int = 30):
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore[import-untyped]
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    except Exception:
        pass
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore[import-untyped]
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    except Exception:
        pass

    class _SimpleSplitter:
        def __init__(self, chunk_size: int, chunk_overlap: int):
            self.chunk_size = chunk_size
            self.chunk_overlap = max(0, chunk_overlap)

        def split_documents(self, documents):
            out = []
            for doc in documents:
                text = doc.page_content or ""
                n = len(text)
                if n <= self.chunk_size:
                    out.append(Document(page_content=text, metadata=dict(doc.metadata)))
                    continue
                start = 0
                idx = 0
                while start < n:
                    end = min(start + self.chunk_size, n)
                    piece = text[start:end]
                    out.append(Document(page_content=piece, metadata=dict(doc.metadata)))
                    idx += 1
                    if end >= n:
                        break
                    start = end - self.chunk_overlap
            return out

    return _SimpleSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def chunk_docs(docs: Sequence[Document], chunk_size: int = 300, chunk_overlap: int = 30) -> list[Document]:
    splitter = _get_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(list(docs))


def build_vector_store(docs: Sequence[Document], embeddings: Embeddings, persist_directory: str) -> VectorStore:
    from langchain_chroma import Chroma

    return Chroma.from_documents(
        documents=list(docs),
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name="persona_kb",
    )


def get_retriever(vector_store: VectorStore, k: int = 4):
    return vector_store.as_retriever(search_kwargs={"k": k})


def ingest_persona(persona: Persona, embeddings: Embeddings, settings=None) -> VectorStore:
    from patient_sim.config.settings import get_settings as _get_settings

    settings = settings or _get_settings()
    docs = chunk_docs(load_knowledge_docs(persona))
    return build_vector_store(docs, embeddings=embeddings, persist_directory=settings.chroma_persist_dir)
