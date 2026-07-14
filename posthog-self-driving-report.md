# PostHog Self-driving setup report

## Summary

PostHog Self-driving has been configured for the Patient Communication Simulator. Five native signal sources (error tracking × 3, session replay, and support) plus a GitHub Issues warehouse source are now live; the scout coordinator will pick up the new configs within ~30 minutes and findings will start appearing in the inbox at https://us.posthog.com/project/474814/inbox.

---

## AI data processing

**Approved.** Organization-level AI data processing approval was confirmed before this run began.

---

## GitHub

**Connected during this run.**

| Field | Value |
|---|---|
| Integration | `marccodesstuff` (ID 184357) |
| Connected by | Marc Victor |
| Connected at | 2026-07-12 |

---

## Products enabled

This is a pure FastAPI/Python backend — there is no `posthog-js` client. The server-side product toggles are recorded below; they are inert until the Python SDK is configured to capture that signal.

| Product | Status | Notes |
|---|---|---|
| Session Replay | Enabled but inert | Pure backend — no browser client. Replay requires a browser SDK. No code change needed unless a frontend is added later. |
| Error Tracking | Enabled but inert | Python SDK doesn't autocapture exceptions by default. See follow-up. |
| Support (Conversations) | Enabled but inert | No inbound channel connected. See follow-up. |

> **Note:** `products-enable` was not available via the current API key scope. The products are listed here for completeness; the native signal sources were created regardless (they start emitting once the products are properly configured).

---

## Signal sources

| source_product | source_type | Action | Notes |
|---|---|---|---|
| `signals_scout` | `cross_source_issue` | **Already on (default)** | Scout gate is ON by default — no config row needed. |
| `error_tracking` | `issue_created` | **Enabled** (ID `019f544d-be96…`) | |
| `error_tracking` | `issue_reopened` | **Enabled** (ID `019f544d-c13c…`) | |
| `error_tracking` | `issue_spiking` | **Enabled** (ID `019f544d-c44d…`) | |
| `session_replay` | `session_analysis_cluster` | **Enabled** (ID `019f544d-c7ff…`) | Sample rate 0.1 (server default). Armed for when replay is configured. |
| `conversations` | `ticket` | **Enabled** (ID `019f544d-caff…`) | Dormant until an inbound channel is connected. |
| `llm_analytics` | — | **Skipped** | Internal-only — not a v1 responder. |
| `logs` | — | **Skipped** | Not a v1 responder. |

---

## Connected tools

| Tool | Status |
|---|---|
| **GitHub Issues** | **Connected by this setup.** Warehouse source ID `019f5451-3fb1…`; repo `marccodesstuff/patient-sim`; `issues` table syncing (incremental on `updated_at`). First sync started automatically. Additional tables (pull_requests, etc.) can be enabled in the PostHog data warehouse UI. Inbox responder enabled (ID `019f5451-536a…`). |
| Linear | Not used (not selected). |
| Zendesk | Not used (not selected). |
| pganalyze | Not used (not selected). |

---

## Scout troop

**5 active scouts** out of 28 total.

### Enabled

| Scout | Reason |
|---|---|
| `signals-scout-general` | Always on — covers cross-product correlations and surfaces no specialist owns. |
| `signals-scout-ai-observability` | Primary product surface — LLM providers (OpenAI, Anthropic, Azure Foundry) are the core of this app; `patient_model_invoked` latency is the main reliability signal. |
| `signals-scout-product-analytics` | Secondary product surface — simulation session funnel (`session_started → turns → completion`) is tracked via custom events; a saved funnel insight exists. |
| `signals-scout-redline-safety` *(custom)* | See Custom scouts section. |
| `signals-scout-sim-pipeline` *(custom)* | See Custom scouts section. |

### Disabled

| Scout | Reason |
|---|---|
| `signals-scout-error-tracking` | **Covered by the native source** — error tracking is wired as a signal source in step 4; a scout would duplicate it. |
| `signals-scout-session-replay` | **Covered by the native source** — session replay is wired as a signal source; a scout would duplicate it. |
| `signals-scout-web-analytics` | No web/browser traffic in this project — pure API backend. Enable if a frontend is added. |
| `signals-scout-feature-flags` | No feature flags in active use detected. Enable via PostHog if flags are adopted. |
| `signals-scout-surveys` | No surveys configured (0 found). Enable via PostHog if surveys are added. |
| `signals-scout-revenue-analytics` | No payment SDK or revenue events detected. |
| `signals-scout-experiments` | No A/B experiments configured. Enable if experiments are started. |
| `signals-scout-logs` | PostHog logs product not in use. Enable via PostHog if logs are adopted. |
| `signals-scout-csp-violations` | No CSP reporting configured (pure backend, no browser context). |
| `signals-scout-customer-analytics` | No group/accounts analytics detected. |
| `signals-scout-data-pipelines` | No CDP destinations or batch exports configured. |
| `signals-scout-apm` | No OpenTelemetry spans instrumented. |
| `signals-scout-anomaly-detection` | Slot occupied by more specific specialists. Enable via PostHog if anomaly sweeps are wanted. |
| `signals-scout-observability-gaps` | Slot occupied by more specific specialists. |
| `signals-scout-health-checks` | Slot occupied by more specific specialists. |
| `signals-scout-web-vitals` | No web vitals events (`$web_vitals`) captured. |
| `signals-scout-replay-vision` | No Replay Vision scanners configured. |
| `signals-scout-mcp-tool-calls` | No `$mcp_tool_call` telemetry detected. |
| `signals-scout-data-warehouse` | No warehouse import sources beyond GitHub Issues. |
| `signals-scout-ingestion-warnings` | Disabled to keep the troop small; enable via PostHog if ingestion issues arise. |
| `signals-scout-insight-alerts` | No insight alerts configured. |
| `signals-scout-inbox-validation` | Not appropriate on first setup — no shipped fixes to validate yet. |
| `signals-scout-skills-store` | Not relevant to this project's current stage. |

---

## Custom scouts

### `signals-scout-redline-safety`
**What it watches:** `red_line_triggered` events — fired when a student crosses a safety topic boundary during a simulation.

**Discriminator:** Red-line rate (`red_line_triggered` ÷ `session_turn_completed`) spiking above 1.5× the 14-day rolling average, or a single scenario/persona accounting for >60% of triggers.

**Why no built-in covers it:** `signals-scout-product-analytics` watches conversion/retention funnels, not domain-safety rates. `signals-scout-general` lacks the domain context to know this ratio is meaningful. No native source covers it.

**Explore patterns:** overall rate trend (28-day daily), per-scenario breakdown, per-persona breakdown, time-in-session distribution.

### `signals-scout-sim-pipeline`
**What it watches:** The coupling between `rag_retrieved` and `patient_model_invoked` events — representing the RAG + LLM pipeline that must complete cleanly on every simulation turn.

**Discriminator:** Retrieval-to-invocation ratio falling below 0.7 for ≥2 days (silent RAG failure), or p95 `latency_ms` on `patient_model_invoked` rising ≥50% vs the prior 7-day baseline.

**Why no built-in covers it:** `signals-scout-ai-observability` watches `$ai_*` SDK events; this project uses custom `rag_retrieved` and `patient_model_invoked` events via `posthog-python`. No built-in scout knows to correlate them.

**Explore patterns:** retrieval:invocation ratio trend (14-day daily), latency percentiles (p50/p95), session-level failure co-occurrence, `$exception` co-occurrence by session ID.

### Surfaces considered and ruled out

| Surface | Filter that ruled it out |
|---|---|
| Session completion funnel | Already covered — `signals-scout-product-analytics` watches the saved "Session engagement funnel" insight. |

### Noise escape hatch
If either custom scout turns out noisy, set `emit: false` on its config in PostHog (Settings → Self-driving → Scouts) to switch it to dry-run — it will keep running and logging without writing to the inbox.

---

## Follow-ups

- [ ] **Error tracking (Python SDK):** Add exception capture to the FastAPI app. Use `posthog.capture_exception(e)` in exception handlers, or configure the `posthog-python` SDK's error tracking integration. Until this is done, the error tracking signal sources are armed but silent.
- [ ] **Support channel:** Connect an inbound channel (email, inbox, or Slack) at https://us.posthog.com/project/474814/settings/environment-integrations so the Conversations source starts receiving tickets.
- [ ] **Session replay:** Not applicable to the current pure-backend architecture. If a browser frontend is added, initialise `posthog-js` with session recording enabled and the replay source will start receiving data automatically.
- [ ] **GitHub Issues — additional tables:** Only the `issues` table is syncing. To also sync pull requests or other tables, visit https://us.posthog.com/project/474814/data-management/sources and edit the GitHub source.
- [ ] **Re-enable disabled scouts as needed:** If you later add feature flags, experiments, surveys, or logs, enable the corresponding scout (`signals-scout-feature-flags`, `signals-scout-experiments`, `signals-scout-surveys`, `signals-scout-logs`) in PostHog → Self-driving → Scouts.

---

## What happens next

The scout coordinator picks up the new configs within ~30 minutes. Scouts run on a 24-hour interval; the first scans fire on the next coordinator tick. Findings from scouts, error tracking, session replay, GitHub Issues, and support tickets all route to the same inbox:

**https://us.posthog.com/project/474814/inbox**

Immediately-actionable findings will surface as inbox reports — each one includes a suggested fix and links to the relevant PostHog data. The two custom scouts (`redline-safety` and `sim-pipeline`) are tuned specifically to this project's event taxonomy and will speak up only when something is genuinely off.
