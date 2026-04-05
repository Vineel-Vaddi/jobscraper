# Phase 7: Polish — Walkthrough

## 1. What was Built

| Deliverable | Location |
|---|---|
| Schema: saved sessions, preferences, presets, pins | [models.py](file:///c:/Users/Welcome/jobscraper/apps/backend/src/database/models.py) |
| Alembic migration | [6e7f8a9b0c1d](file:///c:/Users/Welcome/jobscraper/apps/backend/alembic/versions/6e7f8a9b0c1d_phase7_polish_schema.py) |
| Titles engine | [titles_engine.py](file:///c:/Users/Welcome/jobscraper/apps/backend/src/services/polish/titles_engine.py) |
| Snippets engine | [snippets_engine.py](file:///c:/Users/Welcome/jobscraper/apps/backend/src/services/polish/snippets_engine.py) |
| Pydantic schemas | [schemas/polish.py](file:///c:/Users/Welcome/jobscraper/apps/backend/src/schemas/polish.py) |
| Preferences + titles API | [profile_prefs.py](file:///c:/Users/Welcome/jobscraper/apps/backend/src/routers/profile_prefs.py) |
| Presets, pins, sessions, history, snippets API | [polish.py](file:///c:/Users/Welcome/jobscraper/apps/backend/src/routers/polish.py) |
| Shared types | [index.ts](file:///c:/Users/Welcome/jobscraper/packages/shared-types/index.ts) |
| Resume History page | [history/page.tsx](file:///c:/Users/Welcome/jobscraper/apps/web/src/app/dashboard/history/page.tsx) |
| Preferences / Presets / Pins page | [preferences/page.tsx](file:///c:/Users/Welcome/jobscraper/apps/web/src/app/dashboard/preferences/page.tsx) |
| Snippets on review page | [tailor/variantId/page.tsx](file:///c:/Users/Welcome/jobscraper/apps/web/src/app/dashboard/tailor/%5BvariantId%5D/page.tsx) |
| Unit tests | [test_polish.py](file:///c:/Users/Welcome/jobscraper/tests/services/test_polish.py) |

---

## 2. Schema Summary

### Extended: `JobSearchSession`
- `is_saved` (Boolean) — mark a session as saved/favorite
- `saved_label` (String) — optional human name
- `archived_at` (DateTime) — soft-archive timestamp
- `last_viewed_at` (DateTime) — tracks recency

### New: `ProfilePreference`
One per user. JSON-backed columns for locations, work modes, employment types, industries, exclude keywords. Plus flat `target_seniority`, `salary_notes`, `resume_emphasis` strings.

### New: `RolePreset`
Many per user. Named preset bundles with `target_titles_json`, `priority_skills_json`, `summary_focus`, and optional override/pin-rule JSON dicts.

### New: `ResumePin`
Many per user. Each pin has:
- `source_type` — what is pinned (section, bullet, skill cluster, etc.)
- `source_ref` — text content or key identifying the pinned item
- `pin_mode` — one of `soft`, `strong`, `locked_if_supported`

---

## 3. Preferences / Presets / Pins Behavior Summary

### Guardrail Priority Order (per user directive)
```
1. Truthfulness / Validator — absolute
2. Source-supported evidence — required
3. User pins / presets — strong influence
4. ATS optimization — flexible
```

### Pin Modes
| Mode | Behavior |
|---|---|
| `soft` | Bias upward when relevant, allow lower prominence if weakly relevant |
| `strong` | Keep and emphasize when supported; flag if unsupported |
| `locked_if_supported` **(default)** | Lock position if evidence supports it; refuse and explain if unsupported |

> [!IMPORTANT]
> **No pin mode overrides the truth validator.** If a pinned item is unsupported, contradicted, or fabricated, the system will not force it into the tailored resume. Instead, it flags the pin as not honored and explains why.

### How Preferences Flow Into Existing Pipelines
- **Job ranking**: preference locations/work modes/seniority can boost/penalize fit scores
- **Tailoring defaults**: `resume_emphasis` and preset `priority_skills` bias the `RewriteEngine` ordering
- **Suggested titles**: preferences weight the domain-vote scoring
- **Snippets**: supported keywords from alignment are used, never invented claims

---

## 4. Suggested Titles Logic Summary

The `TitlesEngine` uses three signal layers:

1. **Experience titles** — direct past titles get `high` confidence
2. **Skills → domain mapping** — a static, auditable `SKILL_DOMAIN_MAP` votes for domains, then `TITLE_FAMILIES` expands to market-standard titles
3. **Preference boost** — `resume_emphasis` adds +3 votes to the matching domain

All suggestions include a human-readable `rationale` explaining why. Capped at 8 results. No black-box ML.

---

## 5. Snippet Generation Summary

The `SnippetsEngine` produces four copy-ready text blocks:

| Type | Purpose |
|---|---|
| `short_intro` | 2-line intro using real name + top skills |
| `why_fit` | Evidence-backed fit statement citing experience count + aligned keywords |
| `why_role` | Role-specific connection statement |
| `recruiter_note` | LinkedIn/email outreach message |

All snippets use **only** canonical profile data and keyword alignment from the variant. No claims are invented. The UI provides one-click clipboard copy for each snippet.

---

## 6. Test Coverage Summary

`tests/services/test_polish.py` covers:

- **Titles**: experience-based suggestions, skill-based suggestions, preference boosting, 8-item cap
- **Snippets**: all 4 types present, name/company interpolation, no hallucinated ML claims when skills don't support it
- **Pin modes**: enum validation

---

## 7. Final Product Polish Summary

Phase 7 reduces repeat friction across the core flow:

| Before | After |
|---|---|
| No way to revisit old tailored resumes | `/dashboard/history` with filter/download/review |
| Re-enter preferences every time | Persistent preferences auto-inform ranking + tailoring |
| Manual skill prioritization each run | Role presets save reusable targeting configs |
| No job session memory | Save/label/archive sessions from the dashboard |
| Blank application form boxes | Copy-ready snippets on the review page |
| No title guidance | Transparent suggested titles from profile evidence |
| No way to protect key content | Pin sections/bullets with clear mode semantics |
