# Phase 2: Canonical Profile Builder Walkthrough

The Canonical Profile Builder MVP is now fully documented, tested, and implemented across the stack! 

> [!IMPORTANT]
> To utilize the semantic parsing feature with Gemini, make sure your `.env` contains `GEMINI_API_KEY` (I mapped the demo key you provided inside `config.py` for immediate startup convenience).

## What Was Built

1. **Database Additions**
   * Added the `Profile` model containing `canonical_profile_json`, `confidence_summary_json`, and a `status` field.
   * Created a manual Alembic DB migration script in `alembic/versions/1a2b3c4d5e6f_add_profile_model.py`.

2. **Semantic Extraction via Gemini**
   * Extended Celery worker parser logic using a direct `httpx` query to `gemini-1.5-flash` (`src/utils/gemini_client.py`).
   * Used structured prompting asking Gemini to emit JSON conforming exactly to the desired Schema mapping.

3. **Normalization & Merging**
   * Built `profile_merger.py` evaluating `profiles_input` sourced from parsed PDF, DOCX, and ZIP documents.
   * Wrote precedence rules dynamically prioritizing structured inputs over heuristics.

4. **REST API endpoints**
   * Added `GET /api/profile`, `POST /api/profile/build`, and `PATCH /api/profile`.

5. **Canonical Profile Next.js UI**
   * Built the `/dashboard/profile/page.tsx` view displaying Identity, Experience, Skills, and Headline data iteratively.
   * Provided an "Edit Profile" interaction permitting user adjustments mapped directly to the `PATCH API`.
   * Added Conflict Alerts parsing the `confidence_summary_json` from the merger algorithm to warn users if arbitrary duplicate reductions occurred.

## Precedence Rules Explained

The merging array establishes the truth of data relying on Source precarity:
1. **LinkedIn JSON/ZIP (`linkedin_export`): ** Level `3` (highest structural integrity)
2. **LinkedIn PDF (`linkedin_pdf`):** Level `2` 
3. **Resume PDF (`resume`):** Level `1`

The pipeline uses **Precedence Ordering**. For single-set fields (like `name` or `headline`), the value present in the highest precedence document wins, and lower precedence fields are blocked from overwriting. Waitlists like `skills` are **Unioned** natively (unique check), and array structures like `experience` execute a basic collision assessment comparing `company` + `title`, favoring the higher precedence document to retain data coherence. 

## Profile Schema
```json
{
  "identity": { "name": "", "email": "", "phone": "", "location": "" },
  "headline": "",
  "summary": "",
  "skills": ["Python", "Docker"],
  "experience": [{
     "title": "", "company": "", "start_date": "", "end_date": "", "bullets": [], "source_refs": [1] 
  }],
  "education": [],
  "metadata": {"profile_confidence": 0.9, "source_documents": [1, 2]}
}
```

## Known Limitations & Phase 3 Context
1. *Experience Merging Deep Strategy*: The conflict detector resolves matching duplicate Jobs currently by retaining the higher precedence Job wholesale. Merging individual *Bullets* inside heavily overlapping Job elements remains an improvement vector.
2. *Real-Time Sub-Field Provenance*: The DB stores `confidence_summary_json` marking where root schema nodes were derived from. Real-time mapping per Bullet inside the UI remains complex but theoretically supported by the schema.
3. *Error Handling in Production*: We gracefully exit LLM crashes retaining `unsupported JSON` metrics, but long-term parsing reliability depends on robust LLM retries (handled automatically by Celery currently but lacking backoff context within Gemini parameters).

**Next Step**: Phase 3 (Tailoring & Cover Letter generation using the Candidate Profile against a Target JD).
