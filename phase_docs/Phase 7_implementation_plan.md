# JobTailor Phase 7: Polish

## Scope
Finalizing the repeatable usage loops minimizing duplicate user inputs across tailoring requests. This phase binds presets, explicit preferences, pinning, historical resume access, and copy-ready snippet text directly into the workflow natively.

## Proposed Changes

### Database Schema Updates (`apps/backend/src/database/models.py`)
#### [MODIFY] models.py
1. **Extend `JobSearchSession`:**
   - Add `is_saved` (Boolean), `saved_label` (String), `archived_at` (DateTime), `last_viewed_at` (DateTime).
2. **Add `ProfilePreference` model:**
   - `user_id`, `locations`, `work_modes`, `employment_types`, `target_seniority`, `salary_notes`, `exclude_keywords`.
3. **Add `RolePreset` model:**
   - `user_id`, `name`, `target_titles_json`, `preference_overrides_json`, `pinned_section_rules_json`.
4. **Add `ResumePin` model:**
   - `user_id`, `source_type` (profile_section, bullet, summary_line), `source_ref`, `label`, `pin_strength`.

Add Alembic migration `7_polish_schema.py`.

---
### Backend Services (`apps/backend/src/services/polish/`)

#### [NEW] titles_engine.py
- Takes the canonical profile JSON strings (e.g. "Software Engineer" experience) and groups standard market terminology mapped against Preferences outputting ranked target titles natively without heavy blackbox LLMs.

#### [NEW] snippets_engine.py
- Analyzes Job context alongside canonical profile producing explicitly deterministic "Copy-Ready" paragraphs: `short_intro`, `why_fit`, `recruiter_note`. Uses the same strict alignment bounds as `KeywordAligner`.

#### [MODIFY] worker/tailoring/resume_tasks.py
- Accept `preset_id` natively and dynamically modify `RewriteEngine` weights enforcing Pinned components never get structurally dropped even if ATS gap parsing scores them low.

---
### Backend API Routes (`apps/backend/src/routers/`)

#### [NEW] profile_prefs.py
- `GET /api/profile/preferences`
- `PATCH /api/profile/preferences`
- `GET /api/profile/suggested-titles`
- `POST /api/resume-variants/{variant_id}/snippets`

#### [NEW] presets_pins.py
- CRUD for `/api/presets`
- CRUD for `/api/pins`

#### [MODIFY] jobs.py & resume.py
- `PATCH /api/jobs/sessions/{session_id}/save`
- `GET /api/resume-variants/history`

---
### Frontend (`apps/web/src/app/dashboard/`)

#### [NEW] history/page.tsx
List explicitly filtered `ResumeVariant` executions, showing Job titles, status, and download links instantly.

#### [NEW] preferences/page.tsx
Simple standardized setting page tracking targeting ranges explicitly feeding the tailoring defaults natively.

#### [MODIFY] tailor/[variantId]/page.tsx
- Add a new explicit card rendering **Cover Note Snippets** yielding 1-click clipboard binds.

## User Review Required
> [!IMPORTANT]
> **Tailoring Engine Pre-emption**: The preset and pinning structure allows the user to explicitly lock content inside the variants natively overriding the ATS scraper's pruning logic. Are there any strict guardrails where the ATS scraper should override user pins (e.g. removing definitively disproved skills instead of keeping them pinned), or should manual pins always maintain maximum priority?

## Verification Plan
### Automated Tests
- Unit testing `snippets_engine.py` explicitly forcing generation of strings without halluincations.
- Mocking Pin injections and verifying the `RewriteEngine` refuses to omit them.

### Manual Application
- Create a preset, open a Job Session and check `Save Session`.
- Apply Preset on new Variant triggering snippets. Check the output text via dashboard.
