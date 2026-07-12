<wizard-report>
# PostHog post-wizard report

The wizard has completed a deep integration of PostHog analytics into the Patient Communication Simulator. PostHog is initialised in the FastAPI lifespan context manager and flushed gracefully on shutdown. Every simulation session is tracked via a `session_id` distinct ID so events can be correlated per learner session. Key business events cover the full simulation lifecycle — session creation, every student turn, safety red-line violations, session completion, and session replay — plus two lower-level performance signals from inside the LangGraph execution pipeline: patient LLM latency and RAG retrieval.

| Event name | Description | File |
|---|---|---|
| `session_started` | A new simulation session was created with a scenario and persona. | `src/patient_sim/api/main.py` |
| `session_turn_completed` | A student sent a message and received a patient response. | `src/patient_sim/api/main.py` |
| `red_line_triggered` | The student crossed a red-line topic during the simulation. | `src/patient_sim/api/main.py` |
| `session_max_turns_reached` | A session reached its maximum number of allowed turns. | `src/patient_sim/api/main.py` |
| `session_not_found` | A turn request referenced a session ID that does not exist. | `src/patient_sim/api/main.py` |
| `session_replayed` | A user requested the replay of a completed simulation session. | `src/patient_sim/api/main.py` |
| `patient_model_invoked` | The patient LLM was called; includes latency_ms for performance tracking. | `src/patient_sim/graph/nodes.py` |
| `rag_retrieved` | Document chunks were retrieved from the vector store during a turn. | `src/patient_sim/graph/nodes.py` |

## Next steps

We've built a dashboard and five insights to keep an eye on key metrics:

- [Analytics basics (wizard) — dashboard](https://us.posthog.com/project/474814/dashboard/1834708)
- [Sessions started over time (wizard)](https://us.posthog.com/project/474814/insights/0IFKpWkC)
- [Session engagement funnel (wizard)](https://us.posthog.com/project/474814/insights/317alygP)
- [Red line triggers over time (wizard)](https://us.posthog.com/project/474814/insights/qJEidzNJ)
- [Sessions by difficulty (wizard)](https://us.posthog.com/project/474814/insights/B7zlxwHT)
- [Patient model avg latency (wizard)](https://us.posthog.com/project/474814/insights/aqvSZ6zd)

## Verify before merging

- [ ] Run a full production build (the wizard only verified the files it touched) and fix any lint or type errors introduced by the generated code.
- [ ] Run the test suite — call sites that were rewritten or instrumented may need updated mocks or fixtures.
- [ ] Add `POSTHOG_PROJECT_TOKEN`, `POSTHOG_HOST`, and `POSTHOG_DISABLED` to `.env.example` and any bootstrap scripts so collaborators know what to set.

### Agent skill

We've left an agent skill folder in your project. You can use this context for further agent development when using Claude Code. This will help ensure the model provides the most up-to-date approaches for integrating PostHog.

</wizard-report>
