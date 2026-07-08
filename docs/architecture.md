# Architecture

## Overview

`patient-sim` is a LangGraph/LangChain state machine for simulating patient conversations in clinical communication training.

## Flow

1. Student input enters `input_guard`.
2. `retrieve` fetches persona/scenario chunks from a vector store.
3. `respond` asks the patient LLM for an in-persona response.
4. `parse_structured` extracts `PatientTurn`.
5. `update_state` appends history, updates rolling summary and turn count.
6. `evaluate_turn` optionally scores the student's communication.
7. `log_turn` records structured telemetry.

## Provider abstraction

Model providers are selected via config; providers are isolated behind `ModelProvider`.

## Interfaces

- Python library: `patient_sim.graph.graph.build_graph`
- REST: `patient_sim.api.main.app`
- CLI: `patient_sim.cli.main:app`

## Observability

Every turn is logged to a JSONL session log. Replay is available via `SessionReplayer`. Optional LangSmith hook is provided.
