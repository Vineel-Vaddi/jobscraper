# Phase 4: JD Parsing + Resume Tailoring Walkthrough

This phase implements a complete backend capability suite to produce a clean, ATS-friendly tailored resume. It operates deterministically using validation heuristics to strictly guarantee that no hallucinatory skills or responsibilities are injected over your Canonical Profile.

## What was Built
- **DB & Entities:** Integrated the `ResumeVariant` entity matching jobs to user profiles with heavy JSON storage mapping. 
- **API & Celery Pipeline:** Created the `/api/resume-variants` endpoint suite to construct tailoring payloads concurrently.
- **Frontend Interaction:** Added triggers directly into `Job Detail View` pushing into a dedicated interactive polling result screen.
- **Worker Pipeline:** Engineered structural boundaries passing JSON downwards sequentially (`JDParser` -> `SkillGapAnalyzer` -> `KeywordAligner` -> `RewriteEngine` -> `ResumeValidator` -> `ATSScorer` -> `ResumeExporter`).

---
## Schema Summary
### `ResumeVariant`
Persists the end-to-end evidence pack mapping tailoring logic.
- **Keys:** `user_id`, `job_id`, `profile_id`, `base_document_id`
- **Output Artifacts:** `jd_summary_json`, `keyword_alignment_json`, `skill_gap_json`, `tailored_resume_json`, `validator_report_json`, `ats_score_json`
- **Delivery Paths:** `export_docx_storage_key`, `export_pdf_storage_key`
- **State Machine Options:** `pending`, `processing`, `success`, `needs_review`, `failed`

---
## Truth-Preservation / Validator Summary

> [!CAUTION]  
> **Safety Design Constraint**  
> We inherently restricted the `RewriteEngine` to perform deep-copy re-ordering and verified insertions rather than unstructured blackbox LLM replacements. Prompt-injection or LLM Hallucinations cannot breach the final document.

The `ResumeValidator` module behaves as an autonomous sanity enforcer before allowing the variant status off the line.
1. It compares all mapped output terminology injected back into the `tailored_resume_json` structure against the pristine `Canonical Profile` arrays.
2. If discrepancies (`unsupported_claims`) appear—for instance adding an invented technology directly onto the generated output—the variant is flagged `needs_review`. The UI highlights these rogue injections visibly in bold red for explicit transparency. Every user sees the exact boundary line.

---
## ATS Scoring Summary
A deterministically quantifiable assessment is surfaced to avoid blackbox guess-work on why a tailoring operation was "good" or "bad."
- **Keyword Overlap:** Emits exact numerical fraction `matched_skills / must_have_skills`.
- **Target Distribution Details:** Points precisely to where keywords organically surfaced (e.g., summary matching 3, experience mapping 5).
- **Missing Critical Feedback:** Returns an array of hard required skills absent on the tailored variant to be clearly rendered inside the UI (indicating the canonical profile definitively lacked these strings).

---
## Export Approach Summary
> [!TIP]  
> Kept formatting completely flat ensuring maximal raw-OCR compliance. Multi-column formatting breaks many modern parser implementations.

1. **DOCX Format (`python-docx`):** Built standard paragraph lists and Heading elements iterating straight down the tailored dict utilizing baseline Word style profiles. 
2. **PDF Format (`fpdf2`):** Circumvented complicated headless browsing (like Puppeteer) or unwieldy `WeasyPrint` dependencies by rendering explicit binary byte arrays over the lightweight standard API mapping exactly to the `DOCX` bounds.

---
## Test Coverage Summary
Injected functional unit structures inside `tests/worker/test_tailoring.py`:
- Checks `SkillGapAnalyzer` correctly sorts missing arrays.
- Validates the `KeywordAligner` forces presence priorities matching truth-checks.
- Asserts `ResumeValidator` returns `pass` and `fail` correctly identifying safe vs string-hallucinations explicitly.
- Computes correct ratios iteratively confirming `ATSScorer`.

---
## What Remains for Phase 5 (Feedback and Send)
- **Advanced Diff Editing:** Allowing the user to side-by-side edit the tailored generated components inside the webpage before definitively caching the DOCX.
- **Generative Refinement Feedback Loops:** Sending the Validator's "unsupported claims" payload dynamically back into the generative rewrite engine autonomously instructing it to retry its output and clean out its hallucinated variables before bothering the user explicitly over UI bounds.
- **Cover Letters:** Mapping the `ResumeVariant` bounds cleanly across to generate matched accompanying structured CV text.
