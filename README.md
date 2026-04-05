# JobTailor

JobTailor is a truth-preserving resume tailoring platform. It ingests resumes and LinkedIn profile data, builds a canonical candidate profile, ranks jobs by suitability, generates ATS-optimised resume variants for specific roles, and launches the user to the original application page — all without inventing unsupported claims.

## Current Status

| Phase | Name | Status |
|-------|------|--------|
| 0 | Foundation & Repo Standards | ✅ Complete |
| 1 | Auth + Document Ingestion | ✅ Complete |
| 2 | Canonical Profile Builder | ✅ Complete |
| 3 | Job Intake + Ranking | ✅ Complete |
| 4 | JD Parsing + Resume Tailoring | ✅ Complete |
| 5 | Review, Diff, and Apply Launcher | ✅ Complete |
| 6 | Hardening + Observability | ✅ Complete |
| 7 | Polish (Repeat-Usage Improvements) | ✅ Complete |

## End-to-End User Flow

1. **Sign in** via LinkedIn OIDC (or mock auth for local dev).
2. **Upload** resume PDF/DOCX and/or LinkedIn profile export.
3. **Review** the merged canonical profile (editable).
4. **Paste** a LinkedIn jobs search URL to ingest and rank jobs.
5. **Select** a target job to generate a tailored resume.
6. **Review** section-by-section diff, validator results, ATS score, and cover-note snippets.
7. **Download** DOCX/PDF and click **Go Apply** to open the original job page.

## Architecture Overview

```
┌──────────────┐      ┌──────────────────────────────┐
│  Next.js UI  │◄────►│  FastAPI + Celery  (unified)  │
│  apps/web    │      │  apps/backend                 │
└──────────────┘      └───────┬──────────┬────────────┘
                              │          │
                     ┌────────▼─┐   ┌────▼────┐   ┌─────────┐
                     │PostgreSQL│   │  Redis  │   │  MinIO  │
                     └──────────┘   └─────────┘   └─────────┘
```

- **Frontend**: Next.js 14 App Router (`apps/web`)
- **Backend**: Unified FastAPI API + Celery workers (`apps/backend`)
- **Storage**: PostgreSQL (relational), Redis (task broker), MinIO (object/file storage)
- **Auth**: LinkedIn OIDC with session cookies (mock mode available)
- **Contracts**: `packages/shared-types` (TypeScript) ↔ `apps/backend/src/schemas` (Pydantic)

See [docs/architecture.md](docs/architecture.md) for full details.

## Local Development

### Prerequisites
- Docker & Docker Compose
- Node.js ≥ 18 / npm
- Python 3.11+ (for running tests outside Docker)

### Primary Workflow (Docker Backend + Native Frontend)

```bash
# 1. Configure environment
cp .env.example .env

# 2. Boot infrastructure + backend
docker-compose -f infra/docker/docker-compose.yml up --build -d
# Wait ~10s for databases to accept connections

# 3. Run migrations (first time only)
docker-compose -f infra/docker/docker-compose.yml exec api alembic upgrade head

# 4. Boot frontend
cd apps/web
npm install
npm run dev
```

### Access Points

| Service | URL |
|---------|-----|
| Web UI | http://localhost:3000 |
| FastAPI Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| Deep Health | http://localhost:8000/api/admin/health/deep |
| Prometheus Metrics | http://localhost:8000/api/admin/metrics |
| Admin Debug Panel | http://localhost:3000/dashboard/admin |
| MinIO Console | http://localhost:9001 (`minioadmin` / `minioadmin`) |

### Key Dashboard Pages

| Page | Path |
|------|------|
| Document Upload | `/dashboard` |
| Profile Review | `/dashboard/profile` |
| Job Sessions | `/dashboard/jobs` |
| Tailored Resume Review | `/dashboard/tailor/[variantId]` |
| Resume History | `/dashboard/history` |
| Preferences & Presets | `/dashboard/preferences` |
| Admin Diagnostics | `/dashboard/admin` |

## Core Entities

| Entity | Table | Phase |
|--------|-------|-------|
| `User` | `users` | 0 |
| `Session` | `sessions` | 0 |
| `Document` | `documents` | 1 |
| `DocumentParseEvent` | `document_parse_events` | 1 |
| `Profile` | `profiles` | 2 |
| `JobSearchSession` | `job_search_sessions` | 3 (+7: saved/archive) |
| `Job` | `jobs` | 3 |
| `ResumeVariant` | `resume_variants` | 4 |
| `ApplyEvent` | `apply_events` | 5 |
| `AgentRun` | `agent_runs` | 6 |
| `ProfilePreference` | `profile_preferences` | 7 |
| `RolePreset` | `role_presets` | 7 |
| `ResumePin` | `resume_pins` | 7 |

## Documentation Index

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design, entity relationships, async pipelines |
| [API Contracts](docs/api_contracts.md) | All REST routes grouped by feature area |
| [Logging & Observability](docs/logging.md) | Structured logging schema, metrics, admin tools |
| [Contributing](docs/contributing.md) | Branch naming, PR conventions, commit style |
| [Unified Backend ADR](docs/ADR-001-unified-backend.md) | Why FastAPI + Celery share one codebase |
| [Phase Docs](phase_docs/) | Per-phase plans, tasks, and walkthroughs |
| [PRD](PRD.md) | Product requirements and phase plan |

## Known Constraints

- LinkedIn OIDC requires a real app registration for production; use `MOCK_LINKEDIN=true` for local dev.
- Job extraction relies on HTML scraping which may break with LinkedIn layout changes.
- LLM-based operations (profile merge, tailoring) require Gemini API access or fall back to deterministic logic.
- Observability uses in-process Prometheus counters; no external Grafana stack is bundled yet.
- Pin guardrail priority: Truthfulness → Evidence → User Pins → ATS optimisation.
