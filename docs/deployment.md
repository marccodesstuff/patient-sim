# Deployment Guide

## Prerequisites

- Python 3.11+
- OpenAI API key and/or Anthropic API key
- Optional: Azure AI Foundry project endpoint, deployment name, and API key
- Optional: LangSmith API key for tracing

## Setup

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
cp .env.example .env
```

If using Azure AI Foundry, also install the optional extra:

```bash
python -m pip install -e ".[azure]"
```

Edit `.env` to set at least one provider API key and the embedding key if using OpenAI embeddings.

## Providers

This simulator supports three provider backends via config:

- `openai`
- `anthropic`
- `azure_foundry`

Each slot—patient model, judge model, and embedding model—can independently use any supported provider.

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

## Azure AI Foundry setup

1. Create an Azure AI Foundry project in the Azure portal.
2. Deploy a model in your Foundry project and note the endpoint URL and deployment name.
3. Add the endpoint, deployment name, and API key to `.env` under `AZURE_AI_FOUNDRY_*`.
4. Set `PATIENT_PROVIDER=azure_foundry` and/or `JUDGE_PROVIDER=azure_foundry` in `.env`.

## Production notes

- Replace Chroma with Qdrant/pgvector by implementing the retriever factory in `retriever_factory.py`.
- Use persistent Franz/Redis-backed LangGraph checkpointer for session resume at scale.
- Rotate API keys via a secrets manager; do not commit `.env`.
