# JobTailor Phase 6: Hardening + Observability

## Scope
Make the JobTailor ecosystem observable, resilient to external failure states, and diagnosable. This phase introduces system-wide metric observation, explicitly decoupled retries, timeout boundaries, structured metric exports, and a live internal admin dashboard.

## Proposed Changes

### 1. Database Schema (`apps/backend/src/database/models.py`)
#### [MODIFY] models.py
Add `AgentRun` tracking model:
- `id`, `user_id`
- `run_type` (document_parse, profile_build, job_ingest, resume_tailor)
- `target_entity_type` (e.g. 'resume_variant', 'job')
- `target_entity_id`
- `status` (pending, processing, success, failed, retried, timed_out)
- `started_at`, `finished_at`, `duration_ms`
- `retry_count`, `error_code`, `error_message`, `metadata_json`

Create an Alembic migration (`add_agent_runs_model.py`).

---
### 2. Instrumentation and Middlewares (`apps/backend/src/telemetry/`)
#### [NEW] metrics.py & middleware.py
- Use `prometheus_client` to expose counter/histogram primitives tracking route hit counts, error rates, and durations.
- Add FastAPI middleware appending `request_id` explicitly resolving down to logger globals pushing structured `JSON` metrics.

#### [NEW] retries.py (Celery wrappers)
- Expose `@with_retry(max_retries=3, exponential_backoff=True)` wrapper handling `requests.exceptions.Timeout` or network closures safely returning tasks to the queue without poisoning DB states recursively.
- Classify `NonRetryableException` (e.g., File format corruption, Truth Validator hard stops).

---
### 3. Backend Observability Routes (`apps/backend/src/routers/admin.py` & `main.py`)
#### [NEW] routers/admin.py
- `GET /health` and `GET /health/deep` (pinging DB and Redis).
- `GET /metrics` (Prometheus text exporter).
- `GET /api/admin/system-summary` (Daily counters on Job Intake failures, Profiler Success rates).
- `GET /api/admin/runs` (Filtered fetching against `AgentRun` logs mapped visually on frontend).

#### [MODIFY] main.py
Mount the routers and initialize base startup routines verifying MinIO, PG, and Redis cleanly.

---
### 4. Admin Diagnostic Dashboard (`apps/web/src/app/dashboard/admin/`)
#### [NEW] admin/page.tsx
- Internal protected screen grouping system health statuses (Up/Down indicators).
- Table view dynamically pulling `AgentRuns` filtered by failure states offering 1-click JSON expanding payloads indicating explicitly why parsing or LLM calls crashed.
- Metric cards summarizing volume.

## Verification Plan
### Automated Tests
- Unit testing `@with_retry` capturing simulated HTTP timeout exceptions securely recovering state without destroying underlying entity bounds.
- Testing mapping parameters resolving nested `AgentRun` persistence calls efficiently.

### Manual Verification
- Boot staging simulation and forcibly drop backend Redis connectivity during a `Tailoring` background job confirming the wrapper traps the error rather than hard-killing the master thread. Review the `/dashboard/admin` panel validating the failure code registers structurally.
