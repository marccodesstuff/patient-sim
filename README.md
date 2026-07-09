# Patient Communication Simulator

Production-grade patient-conversation simulator built on **LangGraph** + **LangChain** for clinical-communication training.

## Features

- Config-driven LLM providers: `openai`, `anthropic`, `azure_foundry`
- Pluggable per-slot provider selection for patient, judge, and embeddings
- Structured patient turns with automatic parsing and retry
- Chroma-backed retrieval-augmented generation
- Rolling conversation summary and progressive disclosure
- Difficulty modulation and red-line safe-branch handling
- LLM-as-judge rubric evaluation with optional Foundry-native evaluation pass
- FastAPI session API + Typer CLI harness
- Structured JSONL session logs

## Platform

- Python 3.11+
- macOS, Linux, Windows (WSL recommended on Windows)

## Setup

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
cp .env.example .env
# put real keys into .env (never commit)
```

If using **Azure AI Foundry**, install the optional extra:

```bash
python -m pip install -e ".[azure]"
```

## Providers

Set the following in `.env` to control which backend is used:

- `PATIENT_PROVIDER=openai | anthropic | azure_foundry`
- `JUDGE_PROVIDER=openai | anthropic | azure_foundry`
- `EMBEDDING_PROVIDER=openai | anthropic | azure_foundry`

See `.env.example` for the full list of supported variables.

## Run tests

```bash
PYTHONPATH=src python -m pytest -q
```

## Run API

```bash
uvicorn patient_sim.api.main:app --host 0.0.0.0 --port 8000
```

## Run CLI

```bash
python -m patient_sim
```

## Docs

- `docs/deployment.md` — setup, providers, Azure AI Foundry configuration
- `docs/architecture.md` — system design and data flow
- `docs/persona_authoring.md` — how to add new personas/scenarios

## Safety

This is a training simulator only. All personas are synthetic. No real medical advice is emitted.
