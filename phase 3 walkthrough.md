# Phase 3: Job Intake + Ranking Walkthrough

This phase introduces the infrastructure, pipeline, and UI to allow a user to paste a URL of a job search (e.g. from LinkedIn) and asynchronously extract, normalize, consolidate, score, and review jobs against their Canonical Profile.

## What was Built

1. **Database Schema:** Created `JobSearchSession` and `Job` models linked to the User along with the actual alembic migration script (`2a3b4c5d6e7f_add_job_models.py`). Updated the `User` schema relations to match.
2. **Backend API:** Built `routers/jobs.py` giving routes to initiate sessions (`/intake`), list sessions, and list ranked jobs matching a given session.
3. **Ingestion Pipeline:** Created `src/worker/job_tasks.py` which drives the whole extraction and scoring sequence synchronously in the background (Celery).
4. **Pipeline Modules:**
    - `linkedin_extractor.py`: Real logic hitting the supplied HTTP url, parsing with BeautifulSoup targeting known LinkedIn classes (also handles fallback deterministic mock fixtures organically if LinkedIn walls the scraper).
    - `job_normalizer.py`: Lowers title cases naturally, maps boolean/string combinations to defined `work_mode` schemas (`onsite/hybrid/remote`), sanitizes URLs for canonical identifiers.
    - `job_dedupe.py`: Consolidates duplicates.
    - `job_scorer.py`: Transparently scores heuristics against the Canonical Profile.
5. **Frontend UI:**
    - Included `jobs/page.tsx` as an interactive intake UI form.
    - Included `jobs/[sessionId]/page.tsx` for real-time polling of completed sessions and presenting ranked items.
    - Included `jobs/[sessionId]/[jobId]/page.tsx` displaying the exact reasoning for matches and gaps regarding a job against the canonical profile.
    - Connected the Dashboard UI to point to these endpoints securely via shared routing.
6. **Tests:** Wrote unit tests confirming Normalizer mapping strings accurately and the Scorer yielding acceptable bounds and penalties in `tests/worker`.

---
## Schema Summary

### `JobSearchSession`
Tracks the processing state of any intake. Allows UI to poll until completion.
- `id`, `user_id`, `source_url`, `source_type`
- `status` (`pending`, `processing`, `success`, `failed`)
- counts (`raw_result_count`, `normalized_result_count`, `deduped_result_count`)

### `Job`
Extensively caches and structures the extracted job matching against a target query.
- `canonical_job_url`, `external_job_id`
- Core: `title`, `company`, `location`, `work_mode`, `employment_type`
- Insights: `description_text`, `requirements_json`
- Alignment: `fit_score`, `fit_reasons_json`, `fit_gaps_json`, `dedupe_key`

---
## Dedupe Rules Summary

The duplicate collapse logic operates linearly inside the worker against each batch:
1. **External Match**: Matches directly if an `external_job_id` is supplied (e.g., explicitly extracted from `urn:li:jobPosting:xxx`).
2. **URL Match**: Falls back to hashing the base path of the `canonical_job_url` ignoring query properties.
3. **Fuzzy Fallback Heuristic**: If all above fail, duplicates are found via `lower([Title]+[Company]+[Location])` deterministic hashing.

Every job receives a stable `dedupe_key`. If it collides within a session's current extraction queue, the latter is discarded.

---
## Scoring Rules Summary

Job scoring operates deterministically against the user's Canonical Profile without requiring a full heavy LLM pass for explainability. The score starts at an arbitrary `50` bounds between `(0-100)`:

- **Title Validation**: `+15` points if the job `title` substrings the user's current or targeted profile `title`.
- **Requirements vs Skills Mapping**: Cross checks the `requirements_json.skills` (parsed from the raw description) against the Canonical `skills` DB.
    - `+5` points per matching skill mapped (up to `25`).
    - `-2` points per required skill the profile totally misses (up to `-10`).
- **Work Mode Additive**: Adds an explicit heuristic bump (`+5`) if remote preference aligns strictly.

It provides human-readable `fit_reasons_json` (e.g. *Strong skill overlap: python, react*) that the React detail view surfaces explicitly as green checkmarks or red exclamation points.

---
## What Remains for Phase 4

- Allowing users to explicitly press "Use for Targeting / Tailoring" inside the job details card.
- Passing the validated selected `Job` entity downstream paired with the `Profile` database entry to generate Tailored Cover Letters inside the generative AI scope (Phase 4).
- Enhancing extraction with a dedicated proxy/head-less framework explicitly if the app eventually transitions off mock/fallback tests relying exclusively on organic scraping.
