# Persona Authoring Guide

This guide explains how to add a new patient persona and scenario without changing core code.

## 1. Create persona file

Create YAML under `personas/` matching `personas/schemas.py:Persona`. Required fields:

- `persona_id`: unique slug
- `version`: integer
- `demographics`: name/age/gender/occupation/background
- `condition`: primary/relevant_history/medications
- `emotional_profile`: baseline_mood/triggers/reassurance_response
- `communication_style`: verbosity/jargon_comfort/openness
- `hidden_concerns`: list of facts to reveal gradually
- `disclosure_rules`: natural-language rules for progressive disclosure
- `red_lines`: topic/safe_response/flag triples
- `knowledge_documents`: list of markdown files under `personas/knowledge/`
- `difficulty`: cooperative|guarded|distressed

## 2. Add knowledge docs

Add one or more markdown docs under `personas/knowledge/` summarizing background, condition, emotional triggers, and communication style. These are the grounding corpus for RAG retrieval.

## 3. Create scenario file

Create YAML under `personas/` matching `personas/schemas.py:Scenario`. Required fields:

- `scenario_id`
- `title`
- `learning_objectives[]`
- `persona_ref`: must match persona `persona_id`
- `opening_situation`
- `success_criteria[]`
- `max_turns`
- `rubric_ref`

## 4. Create rubric file

Create YAML under `personas/` matching `personas/schemas.py:Rubric`.

- `rubric_id`
- `version`
- `criteria[]`: each with `name`, `description`, `scale`, `weight`

## 5. Validate

Run tests:

```bash
PYTHONPATH=src python -m pytest -q
```
