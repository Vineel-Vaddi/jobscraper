# Phase 6: Hardening + Observability

This phase completes the fundamental reliability layers of JobTailor, protecting our background pipelines and instrumenting observability into both the structured DB schemas and live metrics arrays.

## 1. What was Built
- **`AgentRun` Telemetry Bound**: Attached an explicit `AgentRun` model inside `models.py` natively mapping all major Celery tasks back to their targets. 
- **Decoupled Retry Wrapper Layer**: Brought in `with_db_retry` abstracting timeout traps against 3rd party LLMs and explicit hard-fail exceptions like `NonRetryableException` (e.g. invalid document models).
- **Metric Scrapes via Prometheus**: Appended runtime execution hooks generating latency, frequency, and error histograms across `/metrics`. 
- **Admin Dashboard**: Assembled React's `/dashboard/admin` summarizing top-level runs alongside explicit API status markers and an automated payload dumping view.

---
## 2. Observability Stack Summary
### `Prometheus Middleware` Layer
Rather than inventing complex vendor-locked tooling, exposed `/metrics` inside FastAPI `main.py` pushing directly mapped endpoints. 
- `http_requests_total`: Checks response counts explicitly grouped by `status_code` preventing undocumented 500 loops.
- `http_request_duration_seconds`: Monitors average lag across our main application logic identifying bottleneck targets.

### Deep Health Probing
Added `/api/admin/health/deep` preventing 'Zombie' nodes by explicitly hitting `Postgres` asserting `SELECT 1` responses successfully evaluate natively before permitting traffic.

---
## 3. Retry / Timeout Policy Summary
> [!TIP]
> The `@with_db_retry` decorator automatically wraps the Celery function queue context. Transient Exceptions like `ConnectionError` and `Timeout` natively backoff up to 3 times before failing definitively, avoiding un-bounded lockups without mutating state immediately.

Non-network exceptions (such as custom logic blocks or internal validation failure limits) return a `NonRetryableException` which natively sets the `AgentRun` into a deterministic terminal state, releasing thread locking resources instantly.

---
## 4. Admin/Debug Capabilities Summary
Exposed `/dashboard/admin` natively inside `apps/web`:
- Maps live Database Connectivity checks visually using top-level colored badges preserving UI trust.
- Fetches explicit `system-summary` queries dynamically scaling total Resume Variant builds vs active processing volumes.
- Maps `AgentRuns` horizontally explicitly printing error traces directly inside the array resolving deep nested logs visibly inside staging boundaries.

---
## 5. Test Coverage Summary
Introduced `test_observability.py` covering:
- Simulating `Timeout` against dummy Celery objects affirming exponential backing calls invoke properly against `self.retry()`.
- Validating explicit hard-raises immediately trigger `.update_state(state='FAILURE')` locking out recursive execution dynamically protecting runtime instances.

---
## 6. What Remains for Phase 7 (Final Polish)
- Deployment Docker-Compose hooks cleanly pulling the exported Prom metrics into local mounted Grafana.
- Final user application stage trackers and global polishing blocks.
