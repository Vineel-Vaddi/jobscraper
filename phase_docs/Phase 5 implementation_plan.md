# JobTailor Phase 5: Review, Diff, and Apply Launcher

## Scope
Introduce the Review and Decision Layer where users can transparently diff the generated subset of their canonical profile against their master profile before explicitly locking in the apply step. This tracks the entire application lifecycle event loop.

## Proposed Changes

### Database Models (`apps/backend/src/database/models.py`)
#### [MODIFY] models.py
Add the `ApplyEvent` model:
- `id`, `user_id`, `job_id`, `resume_variant_id`
- `event_type` (`review_opened`, `download_docx`, `download_pdf`, `go_apply_clicked`, `returned_from_apply`, `marked_applied`, `marked_skipped`)
- `target_url`
- `metadata_json`
- `created_at`

Add relationships to `User`, `Job`, and `ResumeVariant`.
Create an Alembic migration for apply_events.

---
### Shared Types & Schemas (`packages/shared-types`, `apps/backend/src/schemas/`)

#### [MODIFY] packages/shared-types/index.ts
Add `ApplyEventResponse`, `DiffSummary`, `BulletDiff`, `SectionDiff`, `ReviewPayloadResponse`.

#### [MODIFY] schemas/resume.py
Add equivalent Pydantic models to serve structured API responses for the diff endpoints.

---
### Backend Services (`apps/backend/src/services/review/`)

#### [NEW] diff_engine.py
A deterministic engine passing `base (Canonical Profile JSON)` and `tailored (Variant JSON)` blocks.
- **Section Diff**: Compares top-level presence (skills, summary). Identifies unchanged, added, removed.
- **Bullet Diff**: Runs string matching heuristics on the experience bullet arrays, identifying exact matches or changes.

#### [NEW] why_changed.py
Reads the artifacts (`keyword_alignment_json`, `skill_gap_json`, `ats_score_json`) and generates deterministic explanations.

---
### Backend API Routes (`apps/backend/src/routers/resume.py`)

#### [MODIFY] routers/resume.py
Add routes:
- `GET /api/resume-variants/{variant_id}/review`: Computes/Returns base profile + tailored profile alongside structured `DiffEngine` details and `WhyChanged` notes, merging ATS/Validator datasets natively.
- `POST /api/resume-variants/{variant_id}/events`: Accepts logging structures (e.g. `download_docx`, `review_opened`).
- `POST /api/resume-variants/{variant_id}/go-apply`: Verifies variant ownership, logs the `go_apply_clicked` event dynamically, and returns the original job `source_job_url`.

---
### Frontend (`apps/web/src/app/dashboard/`)

#### [MODIFY] tailor/[variantId]/page.tsx
Evolve the existing results page into the comprehensive **Review Page**:
- **Master vs Tailored Diff Layout**: Render original components compared to the newly structured variants using clean badges (Added/Rewritten).
- **Warnings & Transparency**: Renders bold flags derived from Validator API endpoints.
- **Go Apply Launcher Bar**: Sticky bottom/top bar incorporating:
  - Download triggers (hooked to event posts).
  - Main "Go Apply Externally" action which fetches the URL, records state, and safely opens the external boundary via `_blank`.

## Verification Plan
### Automated Tests
- `tests/services/test_diff_engine.py`: Unit test verifying diff arrays and boolean comparisons.
- `tests/services/test_why_changed.py`: Unit test mapping justifications.

### Manual Application
- Open Tailoring View, ensure diffing displays accurately over prior phase baseline outputs.
- Click 'Go Apply' and confirm opening of valid Job Source URL with logged POST.
