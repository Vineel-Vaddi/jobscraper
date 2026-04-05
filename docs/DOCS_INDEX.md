# Documentation Index

Quick reference for all project documentation. See the [README](../README.md) for setup instructions.

## Engineering Docs (`docs/`)

| Document | Description |
|----------|-------------|
| [architecture.md](architecture.md) | System design, entity model, async pipelines, observability stack |
| [api_contracts.md](api_contracts.md) | Complete REST API route reference grouped by feature area |
| [logging.md](logging.md) | Structured log schema, metrics, retries, health checks, admin panel |
| [contributing.md](contributing.md) | Branch naming, PR conventions, development workflow |
| [ADR-001-unified-backend.md](ADR-001-unified-backend.md) | Decision record: why API + worker share one Python codebase |

## Product Docs

| Document | Description |
|----------|-------------|
| [PRD.md](../PRD.md) | Product requirements, user flow, phase plan, scope |

## Phase Docs (`phase_docs/`)

Each phase has up to three documents: an implementation plan, a task checklist, and a completion walkthrough.

| Phase | Plan | Tasks | Walkthrough |
|-------|------|-------|-------------|
| 0 — Foundation | [Plan](../phase_docs/Phase_0_Foundation%20Retrofit%20Plan.md) | [Tasks](../phase_docs/JobTailor%20Phase%200%20Tasks.md) | [Walkthrough](../phase_docs/phase0%20walkthrough.md) |
| 1 — Auth + Ingestion | [Plan](../phase_docs/phase1_implementation_plan.md) | [Tasks](../phase_docs/Phase%201%20tasks.md) | [Walkthrough](../phase_docs/JobTailor%20Phase%201%20Completion%20Walkthrough.md) |
| 2 — Profile Builder | [Plan](../phase_docs/Phase%202%20Canonical%20Profile%20Builder.md) | [Tasks](../phase_docs/Phase%202%20Tasks.md) | [Walkthrough](../phase_docs/Phase%202%20Canonical%20Profile%20Builder%20Walkthrough.md) |
| 3 — Job Intake + Ranking | [Plan](../phase_docs/phase%203%20implementation_plan.md) | [Tasks](../phase_docs/phase%203%20tasks.md) | [Walkthrough](../phase_docs/phase%203%20walkthrough.md) |
| 4 — JD Parsing + Tailoring | [Plan](../phase_docs/Phase%204%20implementation_plan.md) | [Tasks](../phase_docs/Phase%204%20tasks.md) | [Walkthrough](../phase_docs/Phase%204%20walkthrough.md) |
| 5 — Review + Apply | [Plan](../phase_docs/Phase%205%20implementation_plan.md) | [Tasks](../phase_docs/Phase%205%20tasks.md) | [Walkthrough](../phase_docs/Phase%205%20walkthrough.md) |
| 6 — Hardening + Observability | [Plan](../phase_docs/Phase%206%20implementation_plan.md) | [Tasks](../phase_docs/Phase%206%20tasks.md) | [Walkthrough](../phase_docs/Phase%206%20walkthrough.md) |
| 7 — Polish | [Plan](../phase_docs/Phase%207_implementation_plan.md) | [Tasks](../phase_docs/Phase%207_task.md) | [Walkthrough](../phase_docs/Phase%207_walkthrough.md) |

All phases (0–7) are **complete**.
