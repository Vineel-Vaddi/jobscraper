# Architecture

JobTailor is a monorepo with a unified Python backend, a Next.js frontend, and three infrastructure services. This document reflects the system as built through Phase 7.

## High-Level Architecture

```
                        ┌─────────────────────┐
                        │    Next.js 14 UI     │
                        │    apps/web          │
                        └────────┬────────────┘
                                 │ HTTP (session cookie)
                        ┌────────▼────────────┐
                        │  FastAPI API Server  │
                        │  apps/backend/src/   │
                        │  main.py             │
                        └──┬──────────┬────────┘
                           │enqueue   │query
                    ┌──────▼──┐   ┌───▼──────┐   ┌──────────┐
                    │  Redis  │   │PostgreSQL│   │  MinIO   │
                    │ (broker)│   │  (data)  │   │ (files)  │
                    └──┬──────┘   └──────────┘   └──────────┘
                       │consume
                    ┌──▼──────────────────────┐
                    │   Celery Workers         │
                    │   apps/backend/src/      │
                    │   worker/                │
                    └─────────────────────────┘
```

The API server and Celery workers share a single Python codebase (`apps/backend`). See [ADR-001](ADR-001-unified-backend.md) for the rationale.

## Directory Layout

```
jobscraper/
  apps/
    web/                    # Next.js 14 frontend (App Router)
    backend/                # Unified FastAPI + Celery backend
      src/
        main.py             # FastAPI application entry
        config.py           # Settings from environment
        database/           # SQLAlchemy models, engine, session
        routers/            # API route modules
          auth.py           # LinkedIn OIDC, session management
          documents.py      # Upload, parse status
          profiles.py       # Profile CRUD, build trigger
          jobs.py           # Job intake, sessions, ranking
          resume.py         # Tailoring trigger, review, downloads, apply
          admin.py          # Health, metrics, system summary, agent runs
          profile_prefs.py  # Preferences, suggested titles
          polish.py         # Presets, pins, saved sessions, history, snippets
        schemas/            # Pydantic request/response models
        worker/             # Celery tasks and pipeline modules
          tasks.py          # Document parse tasks
          profile_tasks.py  # Profile build tasks
          job_tasks.py      # Job ingestion pipeline
          resume_tasks.py   # Resume tailoring pipeline
          tailoring/        # Rewrite engine, validator, ATS scorer, exporters
          parsers/          # PDF, DOCX, LinkedIn export parsers
          job_extractors/   # HTML/URL extraction modules
        services/
          review/           # Diff engine, why-changed generator
          polish/           # Titles engine, snippets engine
        telemetry/          # Prometheus metrics, middleware, retry wrappers
      alembic/              # Database migrations
  packages/
    shared-types/           # TypeScript interfaces mirroring Pydantic schemas
  infra/
    docker/                 # docker-compose.yml, Dockerfiles
  docs/                     # Engineering documentation
  phase_docs/               # Per-phase plans, tasks, walkthroughs
  tests/                    # Unit and integration tests
```

## Infrastructure Dependencies

| Service | Purpose | Local Tool |
|---------|---------|------------|
| PostgreSQL | All relational data | Docker container |
| Redis | Celery task broker + result backend | Docker container |
| MinIO | S3-compatible object storage for uploads and exports | Docker container |

## Core Entities (Database Models)

All models live in `apps/backend/src/database/models.py`.

| Model | Table | Purpose |
|-------|-------|---------|
| `User` | `users` | Authenticated user |
| `Session` | `sessions` | Browser session (cookie-based) |
| `Document` | `documents` | Uploaded file metadata + parse status |
| `DocumentParseEvent` | `document_parse_events` | Parse lifecycle events |
| `Profile` | `profiles` | Canonical merged profile (JSON) |
| `JobSearchSession` | `job_search_sessions` | Job intake session (with save/archive) |
| `Job` | `jobs` | Individual job listing with fit score |
| `ResumeVariant` | `resume_variants` | Tailored resume output + pipeline artifacts |
| `ApplyEvent` | `apply_events` | User action tracking (download, apply click) |
| `AgentRun` | `agent_runs` | Pipeline execution telemetry |
| `ProfilePreference` | `profile_preferences` | User targeting preferences |
| `RolePreset` | `role_presets` | Reusable tailoring presets |
| `ResumePin` | `resume_pins` | Pinned sections/bullets with mode control |

## Async Pipelines

### 1. Document Parse Pipeline (Phase 1)
`POST /api/documents/upload` → MinIO write → `parse_document_task` (Celery) → text extraction → MinIO `.extracted.txt`

### 2. Profile Build Pipeline (Phase 2)
`POST /api/profile/build` → `build_profile_task` (Celery) → semantic extraction → merge → `Profile.canonical_profile_json`

### 3. Job Ingestion Pipeline (Phase 3)
`POST /api/jobs/intake` → `process_job_session_task` (Celery) → URL extraction → normalisation → deduplication → fit scoring

### 4. Resume Tailoring Pipeline (Phase 4)
`POST /api/resume-variants/tailor` → `tailoring_pipeline_task` (Celery) → JD parse → keyword alignment → skill gap → rewrite → validate → ATS score → DOCX/PDF export

### 5. Review + Apply (Phase 5)
`GET /api/resume-variants/{id}/review` (synchronous diff engine) → `POST /go-apply` (event tracking + URL return)

## Observability Stack (Phase 6)

- **Structured logging**: JSON logs with correlation fields (`request_id`, `user_id`, `task_id`, `phase`, etc.)
- **Prometheus metrics**: HTTP request counters/histograms, agent run counters, exposed at `/api/admin/metrics`
- **Retry handling**: `@with_db_retry` decorator with exponential backoff, `NonRetryableException` for terminal errors
- **Health endpoints**: `/health` (shallow), `/api/admin/health/deep` (DB connectivity probe)
- **Agent runs**: `AgentRun` table tracking pipeline execution lifecycle
- **Admin panel**: `/dashboard/admin` showing system summary and recent pipeline runs

## Phase 7 Polish Features

Phase 7 adds repeat-usage improvements without changing the core flow:

- **Saved sessions**: Save/label/archive `JobSearchSession`s for quick revisiting
- **Profile preferences**: Persistent targeting prefs (locations, work modes, seniority, emphasis)
- **Role presets**: Named reusable bundles of target titles, priority skills, and summary focus
- **Resume history**: `/dashboard/history` listing all prior variants with status and downloads
- **Suggested titles**: Deterministic title suggestions from experience + skills + preferences
- **Manual pinning**: Pin sections/bullets with modes (`soft`, `strong`, `locked_if_supported`)
- **Cover-note snippets**: Copy-ready text blocks (intro, why-fit, why-role, recruiter note) on review page

### Pin Guardrail Hierarchy
```
1. Truthfulness / Validator   (absolute — never overridden)
2. Source-supported evidence  (required)
3. User pins / presets        (strong influence)
4. ATS optimisation           (flexible)
```

## Authentication

LinkedIn OIDC flow with session-cookie auth. Set `MOCK_LINKEDIN=true` in `.env` to bypass OAuth for local development (auto-creates a test user).
