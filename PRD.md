Below is a build-ready **PRD + phase-wise delivery plan** for your tool, structured so you can execute it with coding agents. The product assumptions use LinkedIn’s current official support for **OpenID Connect sign-in** and **user-controlled data export / profile PDF download** as the input side of the workflow. ([Microsoft Learn][1])

## PRD

### Product name

**JobTailor**

### Product goal

Help a user turn their resume plus LinkedIn profile data into a stronger, job-specific, ATS-friendlier resume, then launch the original job application page with minimal friction.

### Problem

Job seekers usually have:

* one generic resume,
* incomplete self-positioning,
* poor keyword alignment to the JD,
* too much manual effort in finding and tailoring for relevant roles.

This product reduces that effort by creating a unified candidate profile, ranking jobs by fit, and generating a reviewed resume variant for each target role.

### Target user

An individual job seeker who:

* already has a resume,
* has a LinkedIn account,
* wants faster shortlisting,
* wants help tailoring resumes without inventing false claims.

### Primary workflow

1. User signs in.
2. User uploads resume.
3. User uploads LinkedIn profile PDF or LinkedIn data export.
4. System builds a canonical profile.
5. User pastes a LinkedIn jobs search URL.
6. System ingests jobs from that source, normalizes them, and ranks suitability.
7. User selects a target job.
8. System parses the JD and generates an ATS-friendly tailored resume.
9. User reviews changes in a diff screen.
10. User clicks **Go Apply** to open the original job page.

### Product principles

* Truth-preserving tailoring only.
* One immutable master resume.
* Every tailored resume is versioned.
* User approval required before application launch.
* Strong logging and reproducibility for every agent action.

### Scope for v1 (Phases 0–7 — all complete)

In scope:

* LinkedIn sign-in
* Resume upload
* LinkedIn PDF/data export upload
* Profile merge
* Job intake from pasted search URL
* Job ranking
* JD parsing
* Resume tailoring
* Diff view
* Apply launcher
* Structured logging and observability
* Retry handling and timeout guards
* Admin debug panel
* Saved job sessions
* Profile preferences and role presets
* Resume history and manual section pinning
* Copy-ready cover note snippets

Out of scope:

* one-click auto-apply
* full cover-letter generator
* auto-filling third-party portals
* outreach message automation
* recruiter CRM
* external Grafana dashboards (metrics are served via Prometheus endpoint)

### Success metrics

* Profile build success rate
* Parse quality score
* Job ingestion success rate
* % of jobs with usable JD extracted
* Time from URL paste to ranked jobs
* Time from job selection to tailored resume
* User acceptance rate of tailored resume
* % of users clicking Go Apply
* Resume revision satisfaction score

### Functional requirements

**FR1: Authentication**
Use LinkedIn OpenID Connect for sign-in and local app session creation. LinkedIn’s current consumer docs support Sign In with LinkedIn via OIDC. ([Microsoft Learn][1])

**FR2: Resume ingestion**
Accept PDF and DOCX. Extract structured sections: summary, experience, skills, education, projects, certifications.

**FR3: LinkedIn import ingestion**
Accept:

* LinkedIn account data export
* LinkedIn profile PDF / resume-format PDF
  LinkedIn currently documents account data download, and LinkedIn help also documents profile-to-PDF / resume download paths, though availability can vary by profile language and member access. ([LinkedIn][2])

**FR4: Canonical profile builder**
Merge uploaded resume and LinkedIn import into a unified profile.

**FR5: Job intake**
Accept pasted job search URL and create a job ingestion session.

**FR6: Job suitability ranking**
Rank jobs by title, skills, seniority, location, work mode, and evidence match from the user profile.

**FR7: JD parsing**
Extract keywords, required skills, responsibilities, must-haves, good-to-haves, seniority, location, and employment type.

**FR8: Resume tailoring**
Generate a tailored variant that:

* reorders strongest evidence,
* aligns wording with JD,
* improves ATS keyword coverage,
* never invents experience.

**FR9: Review + diff**
Show original vs tailored changes by section and bullet.

**FR10: Apply launcher**
Open original job page in browser with tailored resume download/view available.

### Non-functional requirements

* Response time under 10 seconds for normal parsing operations
* Background jobs for heavy tasks
* Full audit logs
* Versioned outputs
* Retry-safe queues
* Clean failure messages
* PII-aware storage and deletion controls

### Risks / assumptions

The product is straightforward on the **sign-in** and **user-supplied profile import** side because LinkedIn officially supports those pieces. The profile-PDF flow may not be uniformly available to every member, so the larger account data archive should be treated as the fallback import path. ([Microsoft Learn][1])

---

## System architecture

### Frontend

* Next.js
* Tailwind
* App Router
* Auth session layer
* Upload UI
* Job list and detail screens
* Resume diff viewer
* Apply launcher

### Backend

* FastAPI
* PostgreSQL
* Redis
* Celery or RQ
* S3-compatible object storage

### AI / parsing layer

* Resume parser
* LinkedIn export parser
* Canonical profile builder
* JD parser
* Match scorer
* Resume tailoring engine
* Diff generator
* ATS checker

### Core entities

* `users`
* `sessions`
* `documents`
* `document_parse_events`
* `profiles`
* `job_search_sessions` (with saved/archive fields)
* `jobs`
* `resume_variants`
* `apply_events`
* `agent_runs`
* `profile_preferences`
* `role_presets`
* `resume_pins`

---

## Coding-agent operating model

Use specialized coding agents instead of one general agent.

### Agent 1: Product Architect

Owns:

* repo layout
* system design
* interface contracts
* schema definitions
* cross-agent standards

Deliverables:

* architecture.md
* api_contracts.md
* shared types
* coding standards

### Agent 2: Frontend Agent

Owns:

* Next.js app
* upload flows
* auth screens
* profile review
* job list UI
* diff view
* apply page launcher

Deliverables:

* UI routes
* components
* form validation
* loading/error states

### Agent 3: Backend Agent

Owns:

* FastAPI routes
* DB models
* queue orchestration
* auth callback handling
* session logic
* storage integration

Deliverables:

* API endpoints
* migrations
* background task runners
* service layer

### Agent 4: Parsing Agent

Owns:

* resume parsing
* LinkedIn PDF/data export parsing
* canonical profile merging
* data normalization

Deliverables:

* parser modules
* quality checks
* section extractors
* structured JSON schemas

### Agent 5: Job Intelligence Agent

Owns:

* job ingestion pipeline
* normalization
* deduplication
* fit scoring
* JD extraction

Deliverables:

* ingestion workers
* scoring rules
* ranking endpoints
* test fixtures

### Agent 6: Resume Tailoring Agent

Owns:

* JD-to-resume alignment
* ATS optimization
* safe rewrite rules
* diff outputs
* resume export

Deliverables:

* prompts
* rewriting policies
* ATS scoring logic
* PDF/DOCX generation

### Agent 7: QA / Eval Agent

Owns:

* integration tests
* parse benchmarks
* regression suite
* sample resumes/jobs
* acceptance test reports

Deliverables:

* test matrix
* CI checks
* evaluation dataset
* release checklist

### Agent 8: DevOps Agent

Owns:

* Docker
* env setup
* CI/CD
* secrets
* observability
* staging deployment

Deliverables:

* docker-compose
* deployment manifests
* GitHub Actions
* logging dashboards

---

## Repo structure (as implemented)

```text
jobscraper/
  apps/
    web/                  # Next.js 14 frontend
    backend/              # Unified FastAPI + Celery backend
      src/
        main.py
        routers/          # auth, documents, profiles, jobs, resume, admin, polish, profile_prefs
        schemas/          # Pydantic models
        database/         # SQLAlchemy models, engine
        worker/           # Celery tasks, parsers, tailoring pipeline
        services/         # review/, polish/
        telemetry/        # metrics, middleware, retries
      alembic/
  packages/
    shared-types/         # TypeScript interfaces
  infra/
    docker/               # docker-compose.yml
  docs/                   # Engineering docs
  phase_docs/             # Per-phase plans, tasks, walkthroughs
  tests/                  # Unit + integration tests
```

> **Note**: The original PRD proposed separate `api/` and `worker/` apps. The actual implementation uses a unified backend in `apps/backend` (see [ADR-001](docs/ADR-001-unified-backend.md)).

---

## Phase-wise build plan

## Phase 0: Foundation

Goal: establish repo, standards, and agent workflow.

Build:

* monorepo setup
* shared types
* branch strategy
* issue templates
* logging conventions
* environment config
* CI skeleton

Agents:

* Product Architect
* DevOps Agent

Exit criteria:

* app boots locally
* CI passes on lint/test
* local postgres/redis/storage up
* shared contracts frozen for v1

---

## Phase 1: Auth + document ingestion

Goal: get the user into the system and ingest source documents.

Build:

* LinkedIn OIDC sign-in
* session creation
* resume upload
* LinkedIn PDF/data export upload
* object storage
* document metadata DB records
* raw text extraction service

Agents:

* Backend Agent
* Frontend Agent
* Parsing Agent
* DevOps Agent

Exit criteria:

* user can sign in
* user can upload files
* backend stores files and metadata
* parser extracts text from at least 90% of test files
* failed parses produce actionable error states

Note: this phase relies on LinkedIn’s documented sign-in flow and account-data/profile export features. ([Microsoft Learn][1])

---

## Phase 2: Canonical profile builder

Goal: create one reliable, structured candidate profile.

Build:

* section extraction
* normalization rules
* merge logic
* conflict resolution
* profile review screen
* editable fields for corrections

Agents:

* Parsing Agent
* Backend Agent
* Frontend Agent
* QA Agent

Exit criteria:

* profile JSON generated
* user can review/edit merged profile
* experience/skills/education sections preserved
* parser confidence shown in logs

---

## Phase 3: Job intake + ranking

Goal: accept a pasted search URL, ingest jobs, and rank suitability.

Build:

* job search session model
* job list extraction pipeline
* job normalization
* dedupe
* suitability scoring
* ranked jobs UI
* job detail screen

Agents:

* Job Intelligence Agent
* Backend Agent
* Frontend Agent
* QA Agent

Exit criteria:

* pasted URL creates a job session
* jobs appear in ranked list
* each job has normalized core fields
* scoring reasons are visible
* duplicate jobs collapse correctly

---

## Phase 4: JD parsing + resume tailoring

Goal: produce a truthful ATS-friendly resume for a selected job.

Build:

* JD parser
* skill-gap detection
* keyword alignment
* resume rewrite engine
* output validator
* tailored resume export
* ATS scoring module

Agents:

* Resume Tailoring Agent
* Parsing Agent
* Backend Agent
* QA Agent

Exit criteria:

* user selects a job
* tailored resume generated
* no unsupported claims added
* ATS coverage summary generated
* export works to PDF and DOCX

---

## Phase 5: Review, diff, and apply launcher

Goal: give the user confidence before applying.

Build:

* section diff view
* bullet diff view
* “why changed” notes
* master-vs-variant comparison
* Go Apply launcher
* apply event tracking

Agents:

* Frontend Agent
* Resume Tailoring Agent
* Backend Agent

Exit criteria:

* user sees all changes clearly
* user can download tailored resume
* Go Apply opens original page
* apply action logged

---

## Phase 6: Hardening + observability

Goal: make the tool reliable.

Build:

* structured logs
* retry handling
* timeout guards
* metrics dashboard
* parse failure analytics
* agent run tracking
* admin debug panel

Agents:

* DevOps Agent
* Backend Agent
* QA Agent

Exit criteria:

* dashboards live
* error rates measurable
* all core jobs retry safely
* staging environment stable

---

## Phase 7: Polish

Goal: improve usefulness without changing the core flow.

Build:

* saved job sessions
* profile preferences
* role presets
* resume history
* suggested target titles
* manual resume section pinning
* copy-ready cover note snippets

Agents:

* Frontend Agent
* Backend Agent
* Resume Tailoring Agent

Exit criteria:

* smoother repeat usage
* higher approval rate on tailored resumes
* reduced time to apply

---

## Delivery sequence for coding agents

### Sprint 1

* repo setup
* auth flow
* upload pipeline
* raw parser scaffold

### Sprint 2

* profile builder
* profile review UI
* structured profile persistence

### Sprint 3

* job session creation
* ranked jobs list
* job detail extraction

### Sprint 4

* JD parser
* resume tailoring engine
* ATS checker

### Sprint 5

* diff view
* PDF/DOCX export
* apply launcher

### Sprint 6

* tests
* observability
* hardening
* release candidate

---

## Agent prompts you can use

### Product Architect prompt

“Design the repo, service boundaries, DB schema, event flow, and API contracts for a web app that signs in users with LinkedIn OIDC, accepts resume plus LinkedIn data export/profile PDF, builds a canonical profile, ingests jobs from a pasted LinkedIn jobs search URL, ranks job fit, tailors a resume to a selected JD, shows a diff, and opens the original apply page. Produce architecture docs, shared types, and acceptance criteria.”

### Frontend Agent prompt

“Build the Next.js frontend for JobTailor with screens for sign-in, resume upload, LinkedIn import upload, profile review, pasted search URL intake, ranked jobs list, job detail, tailored resume review, diff view, and apply launcher. Use clean loading/error states and typed API clients.”

### Backend Agent prompt

“Build the FastAPI backend for JobTailor with routes for auth callback, document upload, profile build, job session creation, ranked jobs retrieval, JD parse, resume tailoring, resume export, and apply event tracking. Use PostgreSQL, Redis, background jobs, and structured logging.”

### Parsing Agent prompt

“Implement parsers for resume PDF/DOCX and LinkedIn PDF/data export. Normalize experience, skills, education, projects, certifications, and summary into a canonical profile JSON. Add parser confidence signals and failure reasons.”

### Job Intelligence Agent prompt

“Implement the job ingestion and ranking pipeline. Accept a pasted search URL, extract job list items and detail fields, normalize them, deduplicate them, and compute a transparent fit score against the canonical profile. Expose ranked jobs through typed backend services.”

### Resume Tailoring Agent prompt

“Implement a truth-preserving resume tailoring engine that rewrites a master resume for a chosen JD, improves ATS alignment, reorders relevant evidence, surfaces matching keywords already supported by the user profile, generates a section/bullet diff, and exports final PDF/DOCX.”

### QA Agent prompt

“Create a test matrix for auth, upload, parsing, profile merge, job ingestion, ranking, tailoring, diff generation, and apply launch. Build unit, integration, and regression tests using fixed fixtures.”

### DevOps Agent prompt

“Set up Docker, local development, CI/CD, secrets handling, migrations, structured logs, metrics, dashboards, and staging deployment for JobTailor.”

---

## MVP acceptance checklist

* User can sign in
* User can upload resume
* User can upload LinkedIn export/PDF
* Canonical profile builds successfully
* User can paste search URL
* Jobs appear in ranked order
* User can inspect one job
* Tailored resume is generated
* Diff is readable
* Final resume is exportable
* Go Apply opens original page

If you want, I’ll convert this next into a **task board with epics, stories, and agent-by-agent tickets**.
