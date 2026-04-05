# JobTailor Phase 3 Tasks

- [x] Add `JobSearchSession` and `Job` models to `models.py`
- [x] Run Alembic migration for models
- [x] Update `shared-types/index.ts` with Phase 3 types
- [x] Create `schemas/jobs.py`
- [x] Create `routers/jobs.py` and register in `main.py`
- [x] Create `celery` worker modules: `job_extractors`
- [x] Create `job_normalizer.py`, `job_dedupe.py`, `job_scorer.py`
- [x] Create Celery task in `job_tasks.py`
- [x] Implement `jobs/page.tsx` (Intake Form)
- [x] Implement `jobs/[sessionId]/page.tsx` (Ranked List UI)
- [x] Implement `jobs/[sessionId]/[jobId]/page.tsx` (Job Detail Screen)
- [x] End-to-end local testing & bug fixes
- [x] Write integration and unit tests
