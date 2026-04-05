# JobTailor Phase 3: Job Intake + Ranking

This phase implements the ingestion of job listings from a search URL, normalization and deduplication of those jobs, and scoring their suitability against the user's canonical profile. 

## Important Constraints
- **Extraction Mechanism**: As requested by the user, we will include complex logic for parsing and scraping the data from the provided URL, instead of just using simple HTTP extraction + fixtures. We'll use robust BeautifulSoup selectors that target standard LinkedIn dynamic and static layouts, and implement thorough error handling.


## Proposed Changes

### Database Models (`apps/backend/src/database/models.py`)

#### [MODIFY] models.py
Add `JobSearchSession` and `Job` models:
- **`JobSearchSession`**: `id`, `user_id`, `source_url`, `source_type` (default "linkedin_search_url"), `status` (pending, processing, success, failed), counts (raw, normalized, deduped), timestamps.
- **`Job`**: `id`, `user_id`, `job_search_session_id`, `source_url`, `source_type`, `canonical_job_url`, `title`, `company`, `location`, `work_mode`, `employment_type`, `seniority`, `posted_at_raw`, `description_text`, `requirements_json`, `metadata_json`, `normalization_confidence`, `dedupe_key`, `fit_score`, `fit_reasons_json`, `fit_gaps_json`, timestamps.

An Alembic migration will be created to apply these changes.

---
### Shared Types (`packages/shared-types/index.ts`)

#### [MODIFY] index.ts
Add matching Typescript interfaces for `JobSearchSessionResponse` and `JobResponse`.

---
### Backend API (`apps/backend/src/routers/jobs.py` and `schemas/jobs.py`)

#### [NEW] schemas/jobs.py
Pydantic schemas: `JobIntakeRequest`, `JobSearchSessionResponse`, `JobResponse`. 

#### [NEW] routers/jobs.py
- `POST /api/jobs/intake`: Validates URL, creates `JobSearchSession` in DB, triggers Celery task.
- `GET /api/jobs/sessions`: Lists sessions for the current user.
- `GET /api/jobs/sessions/{session_id}`: Gets session details.
- `GET /api/jobs/sessions/{session_id}/jobs`: Returns all jobs for this session, ranked descending by `fit_score`.
- `GET /api/jobs/{job_id}`: Retrieves the detailed job.

#### [MODIFY] main.py
Include `jobs.router`.

---
### Worker Pipeline (`apps/backend/src/worker/`)

#### [NEW] Worker Modules
- `job_tasks.py`: Contains the celery task entry point `process_job_session_task(session_id: str)`.
- `job_extractors/mock_extractor.py`: Utility to load live or fixture data.
- `job_normalizer.py`: Standardizes titles, work mode (remote, hybrid, onsite), etc.
- `job_dedupe.py`: Logic to assign `dedupe_key` based on URL or [Title + Company] combinations and collapse them.
- `job_scorer.py`: Loads the user's `Profile` (`canonical_profile_json`). Implements heuristic scoring based on simple keyword/string matches between job description and profile fields (title similarity, skills overlap).

#### [MODIFY] celery_app.py
Ensure it auto-discovers `job_tasks` (or just ensures `tasks.py` pattern is followed if we stick to `tasks.py` - we will add a new file `job_tasks.py`).

---
### Frontend (`apps/web/src/app/dashboard/jobs`)

#### [NEW] app/dashboard/jobs/page.tsx
- Page offering an input for a LinkedIn Search URL.
- Submitting triggers the intake API and navigates to the session detail page.
- Lists previous `JobSearchSessions`.

#### [NEW] app/dashboard/jobs/[sessionId]/page.tsx
- Polls for session status (processing -> success).
- Renders the ranked job list (Ranked Jobs UI) showcasing Job Title, Company, Score, and top Fit Reasons.

#### [NEW] app/dashboard/jobs/[sessionId]/[jobId]/page.tsx
- The Job Detail Screen showing exact match details (reasons, description, extracted requirements) and a link to the original job.

## Verification Plan

### Automated Tests
- Unit tests for:
  - `job_normalizer.py` (ensure work_mode maps correctly).
  - `job_dedupe.py` (ensure duplicates get collapsed).
  - `job_scorer.py` (ensure correct baseline scores from fixtures).
- FastAPI tests for the route endpoints (creating sessions and retrieving jobs).

### Manual Verification
- Run dockerized backend and web UI locally. 
- Ensure pasting the test URL initiates the session.
- Validate that the ranked list updates with scores and duplicates are omitted.
