# Phase 2: Canonical Profile Builder

This plan proposes the architecture and implementation steps to build the Canonical Profile Builder on top of the existing Phase 1 foundations.

## Goal
To convert raw extracted text from resumes and LinkedIn exports into a semantic, canonical JSON profile. This system resolves conflicts, merges data with precedence rules, and allows users to review and manually correct the derived profile.

## User Review Required

> [!IMPORTANT]
> **Semantic Parsers (LLM vs Heuristic)**: The PRD mentions "semantic parser" but does not explicitly specify an LLM dependency. 
> To accurately convert unstructured raw text (like resume PDFs) into structured JSON (`identity`, `experience`, `skills`), an LLM (OpenAI `gpt-4o-mini` or Google `gemini-1.5-flash`) is highly recommended over brittle RegEx/heuristic parsers. 
> **Question**: Should I integrate an LLM client (e.g., `openai` or `google-genai` Python library) for the semantic extraction step, or stick to baseline heuristics (which will be much less accurate)?

> [!CAUTION]
> **Database Migrations:** We will add new models (`Profile`) modifying `alembic/versions`. The process will generate a new migration file. Please let me know if there's a specific pattern for running migrations in this project (e.g., Docker `docker-compose exec ...`).

## Proposed Changes

---

### Database Models (`apps/backend/src/database/models.py`)

Add the following Core models to store the Canonical Profile. We will use JSONB (or SQLAlchemy `JSON`) to store the canonical profile data, as it allows flexible schema evolution.

#### [MODIFY] models.py
- `Profile`: Holds `user_id`, `status` (building, built, failed), `canonical_profile_json` (JSON), `merged_from_document_ids` (JSON Array), `confidence_summary_json` (JSON), `created_at`, `updated_at`.
- Link `Profile` in `User` via `relationship("Profile", back_populates="user", uselist=False)`.

---

### Backend Logic & Parsers (`apps/backend/src/worker/`)

The core extraction and merging pipelines.

#### [NEW] worker/semantic_parser.py
A service to take `extracted_text` and map it to a partial JSON schema (identity, experience, skills, etc.) using structured extraction logic.
Included parsers:
- Resume Semantic Parser
- LinkedIn PDF Semantic Parser
- LinkedIn Zip (CSV) Semantic Parser (this might map CSV directly instead of going through text)

#### [NEW] worker/profile_merger.py
Given 1-N partial profiles (from multiple documents), this service applies normalization and precedence rules to merge them into a single Canonical Profile JSON.
- **Precedence**: LinkedIn Structured Export > Resume PDF > LinkedIn PDF for Experience/Education, etc.
- **Normalization**: Clean whitespace, normalize dates.

#### [NEW] worker/profile_tasks.py
Celery task `build_profile_task(user_id, document_ids)`:
1. Loads extracted text for the documents.
2. Runs semantic parsers on each.
3. Merges the results via `profile_merger.py`.
4. Saves to the `Profile` database record.

---

### API Endpoints (`apps/backend/src/routers/`)

REST API for the frontend to interoperate with profiles.

#### [NEW] routers/profiles.py
- `POST /api/profile/build` -> Triggers Celery task to build.
- `GET /api/profile` -> Retrieve current profile state and JSON.
- `PATCH /api/profile` -> Update sections of the JSON (user corrections).

#### [MODIFY] main.py
Include `routers.profiles`.

---

### Frontend Screens (`apps/web/src/app/dashboard/`)

React components for the canonical profile review screen.

#### [NEW] app/dashboard/profile/page.tsx
Main page holding the profile review UI.

#### [NEW] components/Profile/
- `ProfileSection.tsx`: A card representing one section (e.g., Experience) that can toggle into edit mode.
- `ProfileConflictWarning.tsx`: Alert UI for fields with low confidence or conflicts.
- `EditableField.tsx`: Inline editor for specific fields.

#### [MODIFY] app/dashboard/layout.tsx
Add navigation link to the "Profile" page.

## Open Questions

1. **LLM usage**: As asked above, how should we execute unstructured -> semantic JSON extraction?
2. **Trigger mechanism**: Should the profile automatically be built when a document is fully parsed (after Phase 1 task), or strictly initiated via the `POST /api/profile/build` button?
3. **Database execution**: Are there any special commands I should use to run the Alembic migrations, or just `alembic revision --autogenerate` + `alembic upgrade head` in the backend dir?

## Verification Plan

### Automated Tests
- Create Python unit tests (`tests/test_profile_merger.py`) to verify precedence rules and duplicate handling logic outside the DB.

### Manual Verification
- Upload test resumes via the Phase 1 UI.
- Trigger `POST /api/profile/build`.
- Verify the Celery task completes.
- Load the `/dashboard/profile` UI and verify data populates. Make manual corrections and refresh to assure it persisted.
