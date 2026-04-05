# API Contracts

All routes are served by the unified FastAPI backend at `http://localhost:8000`. Frontend types live in `packages/shared-types/index.ts`; backend schemas in `apps/backend/src/schemas/`.

## Authentication

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/auth/login/linkedin` | Redirect to LinkedIn OIDC |
| GET | `/api/auth/callback/linkedin` | OIDC callback, creates session cookie |
| GET | `/api/auth/me` | Return current user |
| POST | `/api/auth/logout` | Clear session |

**Auth model**: Session cookie. All `/api/*` routes (except auth) require a valid session.

In local dev with `MOCK_LINKEDIN=true`, `/api/auth/login/linkedin` auto-creates a test user and sets the session cookie without external OAuth.

---

## Documents (Phase 1)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| POST | `/api/documents/upload` | Upload PDF/DOCX file | `DocumentResponse` |
| GET | `/api/documents` | List user's documents | `DocumentResponse[]` |
| GET | `/api/documents/{id}` | Document details + parse events | `DocumentDetailsResponse` |

---

## Profile (Phase 2)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| POST | `/api/profile/build` | Trigger canonical profile build | `ProfileResponse` |
| GET | `/api/profile` | Get current profile | `ProfileResponse` |
| PATCH | `/api/profile` | Edit canonical profile fields | `ProfileResponse` |

---

## Jobs (Phase 3)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| POST | `/api/jobs/intake` | Create job session from URL | `JobSearchSessionResponse` |
| GET | `/api/jobs/sessions` | List all job sessions | `JobSearchSessionResponse[]` |
| GET | `/api/jobs/sessions/{id}` | Get single session | `JobSearchSessionResponse` |
| GET | `/api/jobs/sessions/{id}/jobs` | List ranked jobs in session | `JobResponse[]` |
| GET | `/api/jobs/{job_id}` | Get single job | `JobResponse` |

---

## Resume Variants (Phase 4)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| POST | `/api/resume-variants/tailor` | Trigger tailoring for a job | `ResumeVariantResponse` |
| GET | `/api/resume-variants/{id}` | Get variant status + data | `ResumeVariantResponse` |
| GET | `/api/resume-variants/{id}/download/docx` | Download DOCX export | File |
| GET | `/api/resume-variants/{id}/download/pdf` | Download PDF export | File |

---

## Review & Apply (Phase 5)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| GET | `/api/resume-variants/{id}/review` | Diff payload + validator summary | `ReviewPayloadResponse` |
| POST | `/api/resume-variants/{id}/events` | Track user action (download, etc.) | `ApplyEventResponse` |
| POST | `/api/resume-variants/{id}/go-apply` | Log apply event, return job URL | `{ target_url }` |

---

## Admin & Observability (Phase 6)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| GET | `/health` | Shallow health check | `{ status }` |
| GET | `/api/admin/health` | Shallow health | `{ status }` |
| GET | `/api/admin/health/deep` | DB connectivity probe | `{ status, database }` |
| GET | `/api/admin/metrics` | Prometheus text format metrics | text |
| GET | `/api/admin/runs` | List recent agent runs (filterable) | `AgentRunResponse[]` |
| GET | `/api/admin/system-summary` | Aggregate counts | `SystemSummaryResponse` |

---

## Profile Preferences (Phase 7)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| GET | `/api/profile/preferences` | Get user preferences | `ProfilePreferenceResponse` |
| PATCH | `/api/profile/preferences` | Update preferences | `ProfilePreferenceResponse` |
| GET | `/api/profile/suggested-titles` | Suggested job titles | `SuggestedTitle[]` |

---

## Role Presets (Phase 7)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| GET | `/api/presets` | List user's presets | `RolePresetResponse[]` |
| POST | `/api/presets` | Create a preset | `RolePresetResponse` |
| PATCH | `/api/presets/{id}` | Update a preset | `RolePresetResponse` |
| DELETE | `/api/presets/{id}` | Delete a preset | `{ status }` |

---

## Resume Pins (Phase 7)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| GET | `/api/pins` | List user's pins | `ResumePinResponse[]` |
| POST | `/api/pins` | Create a pin | `ResumePinResponse` |
| DELETE | `/api/pins/{id}` | Delete a pin | `{ status }` |

Pin modes: `soft`, `strong`, `locked_if_supported` (default).

---

## Saved Sessions (Phase 7)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| PATCH | `/api/jobs/sessions/{id}/save` | Save/unsave a session | `{ status, is_saved }` |
| PATCH | `/api/jobs/sessions/{id}/archive` | Archive a session | `{ status }` |
| GET | `/api/jobs/sessions/saved` | List saved (non-archived) sessions | Session list |

---

## Resume History (Phase 7)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| GET | `/api/resume-variants/history` | List all user's variants with job info | `ResumeHistoryItem[]` |

---

## Cover Note Snippets (Phase 7)

| Method | Route | Description | Response |
|--------|-------|-------------|----------|
| POST | `/api/resume-variants/{id}/snippets` | Generate snippets for a variant | `SnippetResponse` |
| GET | `/api/resume-variants/{id}/snippets` | Get snippets (re-generates) | `SnippetResponse` |

---

## Shared Type Reference

All TypeScript interfaces are defined in `packages/shared-types/index.ts`. All Pydantic schemas are in `apps/backend/src/schemas/`. The two are kept manually in sync. Key types:

- `UserResponse`, `DocumentResponse`, `DocumentDetailsResponse`
- `ProfileResponse`, `JobSearchSessionResponse`, `JobResponse`
- `ResumeVariantResponse`, `AgentRunResponse`, `SystemSummaryResponse`
- `ProfilePreferenceResponse`, `RolePresetResponse`, `ResumePinResponse`
- `ResumeHistoryItem`, `SuggestedTitle`, `SnippetResponse`
