# Logging & Observability

This document covers structured logging, metrics, health checks, retry handling, agent run tracking, and the admin debug panel as implemented through Phase 6.

## Structured Logging

All backend logs are emitted as **machine-parsable JSON**. The logging pattern was introduced in Phase 0 and extended in Phase 6.

### Standard Fields

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | UUID | Correlation ID for HTTP requests (set by middleware) |
| `user_id` | int | Authenticated user performing the action |
| `session_id` | str | Browser session ID |
| `document_id` | int | Document being processed |
| `profile_id` | int | Profile being built/used |
| `job_search_session_id` | int | Job session in context |
| `job_id` | int | Individual job in context |
| `resume_variant_id` | int | Variant being generated |
| `apply_event_id` | int | Apply event being recorded |
| `task_name` | str | Celery task function name |
| `task_id` | str | Celery task UUID |
| `phase` | str | Pipeline stage (`upload`, `extraction`, `profile_build`, etc.) |
| `status` | str | `start`, `success`, `failed` |
| `duration_ms` | int | Execution time for the logged operation |
| `error_code` | str | Categorised error identifier |
| `retry_count` | int | Current retry attempt number |
| `source_type` | str | Document or source type context |

### Usage

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Processing document", extra={
    "user_id": 4,
    "document_id": 12,
    "phase": "extraction",
    "status": "start"
})
```

### Log Event Naming

Use present-tense verb phrases: `"Processing document"`, `"Profile build completed"`, `"Retry exhausted for tailoring task"`.

---

## Prometheus Metrics

Metrics are collected using `prometheus_client` and exposed at `GET /api/admin/metrics` in Prometheus text format.

### HTTP Metrics (via `PrometheusMiddleware`)

| Metric | Type | Labels |
|--------|------|--------|
| `http_requests_total` | Counter | `method`, `endpoint`, `status_code` |
| `http_request_duration_seconds` | Histogram | `method`, `endpoint` |

URL path IDs are masked (e.g. `/api/resume-variants/{id}`) to prevent label cardinality explosion.

### Pipeline Metrics

| Metric | Type | Labels |
|--------|------|--------|
| `agent_run_total` | Counter | `run_type`, `status` |
| `agent_run_duration_seconds` | Histogram | `run_type` |

---

## Health Endpoints

| Endpoint | What it checks |
|----------|---------------|
| `GET /health` | Always returns `{"status": "ok"}` if the process is alive |
| `GET /api/admin/health` | Same shallow check |
| `GET /api/admin/health/deep` | Executes `SELECT 1` against PostgreSQL, reports `ok` or `degraded` with failure details |

---

## Retry Handling

Implemented in `apps/backend/src/telemetry/retries.py`.

### `@with_db_retry(max_retries=3)`

A decorator for Celery tasks that classifies errors:

| Error Type | Behaviour |
|-----------|-----------|
| `requests.exceptions.Timeout` | Retry with exponential backoff (`2^attempt` seconds) |
| `requests.exceptions.ConnectionError` | Retry with exponential backoff |
| `NonRetryableException` | Immediate `FAILURE` state, no retry |
| Other `Exception` | One safe retry at 60s delay |

### Retryable vs Non-Retryable

**Retryable**: transient HTTP failures, temporary DB/Redis/MinIO connectivity, LLM provider timeouts, network hiccups.

**Non-retryable**: unsupported file types, corrupted files, invalid URLs, structurally impossible parser input, validator hard-stops.

---

## Agent Run Tracking

The `AgentRun` model (`agent_runs` table) tracks pipeline execution lifecycle.

| Field | Description |
|-------|-------------|
| `run_type` | `document_parse`, `profile_build`, `job_ingest`, `resume_tailor` |
| `target_entity_type` | e.g. `document`, `profile`, `job_search_session`, `resume_variant` |
| `target_entity_id` | ID of the entity being processed |
| `status` | `pending`, `processing`, `success`, `failed`, `retried`, `timed_out` |
| `duration_ms` | Wall-clock execution time |
| `retry_count` | Number of retries attempted |
| `error_code` / `error_message` | Final error details after retries exhausted |

### Querying Runs

- `GET /api/admin/runs` — list recent runs, filterable by `run_type` and `status`
- `GET /api/admin/system-summary` — aggregate success/failure counts

---

## Admin Debug Panel

Located at `/dashboard/admin` in the frontend. Provides:

- **System health indicators**: API status and database connectivity badges
- **Aggregate metrics**: Total jobs ranked, resumes tailored, successful runs, failed runs
- **Pipeline run table**: Recent `AgentRun` entries with status, duration, error output
- **Prometheus link**: Direct link to raw metrics endpoint

### Access Control

Currently open to any authenticated user in local/staging. In production, this should be gated to admin roles.

---

## Failure Analytics Approach

When something fails, use this diagnostic path:

1. **Structured logs**: grep for `"status": "failed"` combined with `error_code` and the relevant entity ID field
2. **Agent runs**: query `/api/admin/runs?status=failed` to find failed pipeline executions
3. **Admin panel**: browse `/dashboard/admin` for recent failures with expandable error details
4. **Metrics**: check `agent_run_total{status="failed"}` counters at `/api/admin/metrics` to spot trends
