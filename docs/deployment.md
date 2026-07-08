# Deployment Guide

## Prerequisites

- Python 3.11+
- OpenAI API key and/or Anthropic API key
- Optional: LangSmith API key for tracing

## Setup

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env` to set at least one provider API key and the embedding key if using OpenAI embeddings.

## Run API

```bash
uvicorn patient_sim.api.main:app --host 0.0.0.0 --port 8000
```

## Run CLI

```bash
python -m patient_sim
```

## Web UI

The minimal web harness is not included in v1 by default; use the REST API or CLI.

## Production notes

- Replace Chroma with Qdrant/pgvector by implementing the retriever factory in `retriever_factory.py`.
- Use persistent Franz/Redis-backed LangGraph checkpointer for session resume at scale.
- Rotate API keys via a secrets manager; do not commit `.env`.
