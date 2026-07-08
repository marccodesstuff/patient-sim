# Patient Communication Simulator

Production-grade patient-conversation simulator built on **LangGraph** + **LangChain** for clinical-communication training.

## Platform

- Python 3.11+
- macOS, Linux, Windows (WSL recommended on Windows)

## Setup

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
cp .env.example .env
# put real keys into .env (never commit)
python -m patient_sim
```

## Run tests

```bash
pytest -q
```

## Branches

Branch `phase0` is for scaffold/config/provider-factory baseline.

## Safety

This is a training simulator only. All personas are synthetic. No real medical advice is emitted.
