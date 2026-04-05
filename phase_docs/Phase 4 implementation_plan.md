# JobTailor Phase 4: JD Parsing + Resume Tailoring

This phase implements a truth-preserving tailoring engine that produces an ATS-friendly resume from a base profile for a specific job, complete with JD parsing, skill-gap analysis, truth validation, ATS scoring, and DOCX/PDF export.

## Proposed Changes

### Database Models (`apps/backend/src/database/models.py`)

#### [MODIFY] models.py
Add the `ResumeVariant` model:
- `id`, `user_id`, `profile_id`, `job_id`, `base_document_id`
- `status` (`pending`, `processing`, `success`, `failed`, `needs_review`)
- Generated JSON data columns: `jd_summary_json`, `keyword_alignment_json`, `skill_gap_json`, `tailored_resume_json`, `validator_report_json`, `ats_score_json`
- Storage tracking: `export_docx_storage_key`, `export_pdf_storage_key`
- `error_code`, `error_message`, `created_at`, `updated_at`

Add relationships matching these fields to `Job` and `User`.
Generate an alembic migration for this schema.

---
### Backend API & Schemas (`packages/shared-types` and `apps/backend/src/`)

#### [MODIFY] packages/shared-types/index.ts
Add matching Typescript typing for `ResumeVariantResponse` linking all the JSON payloads.

#### [NEW] schemas/resume.py
Pydantic schemas mirroring `ResumeVariant` output and the start request `CreateTailoredResumeRequest(job_id)`.

#### [NEW] routers/resume.py
- `POST /api/resume-variants/generate`: Triggers the Celery task and creates the DB record.
- `GET /api/resume-variants`: List variants.
- `GET /api/resume-variants/{id}`: Returns the variant and its outputs.
- `GET /api/resume-variants/{id}/download/{format}`: Returns binary stream to download DOCX or PDF.

#### [MODIFY] main.py
Include `routers/resume.py`.

---
### Backend Worker Pipeline (`apps/backend/src/worker/`)

This pipeline executes linearly inside Celery for maximum reliability.

#### [NEW] tailoring/jd_parser.py
Uses deterministic extraction (or Gemini/mock) to pull core requirements, nice-to-haves, and domain terminology directly from the `Job.description_text`.

#### [NEW] tailoring/skill_gap.py & tailoring/keyword_alignment.py
Compares the structured JD against `Profile` and explicit experience strings. Emits cleanly separated arrays summarizing strong presence vs total absence.

#### [NEW] tailoring/rewrite_engine.py
Responsible for truth-preserving bullet reordering and summarizing. Will construct an ATS-optimized, factual subset of the user's career prioritizing keywords detected.

#### [NEW] tailoring/validator.py
Acts as a post-rewrite sanity checker ensuring that the vocabulary of the modified resume does not inject unevidenced technologies, years, or titles. Will produce a `pass` or `warn`.

#### [NEW] tailoring/ats_scorer.py
Exposes the score summary, mapping explicit JD MUST HAVE coverage and giving heuristic scoring on keywords.

#### [NEW] tailoring/exporter.py
- Converts the `tailored_resume_json` structure to DOCX utilizing `python-docx`.
- Uses a lightweight python PDF generation strategy (`fpdf2` - will install) to construct an ATS readable PDF from the same structure.

#### [NEW] resume_tasks.py
Defines the celery task tying these sequential module boundaries together.

---
### Frontend (`apps/web/src/app/dashboard/`)

#### [MODIFY] jobs/[sessionId]/[jobId]/page.tsx
Add the trigger: "Use for Targeting (Phase 4)" button which calls `POST /api/resume-variants/generate` and redirects.

#### [NEW] border/tailor/[variantId]/page.tsx
- Polls the backend for active processing.
- Renders the resulting blocks upon success:
  - Validated Tailored Resume sections (Summary, Experience, Skills).
  - Validation output explicitly marking truth-preservation checks.
  - ATS coverage scores.
- Buttons for downloading DOCX / PDF formats.

## Important Constraints
- **PDF Export Tooling:** We will manually install and use `fpdf2` logic for clean deterministic PDFs.
- **Generative Logic:** As requested, we will combine heuristic parsing alongside simulated NLP generative responses to guarantee a consistent truth-validation lifecycle locally without depending on external keys.

## Verification Plan

### Automated Tests
- Unit tests ensuring the validator rejects unevidenced keywords explicitly injected into the AST stream.
- Unit testing checking skill gap array structure outputs.

### Manual Verification
- Navigating to Job Detail -> Click Tailor -> Ensure success payload visually surfaces validations.
- Downloading DOCX from the frontend.
