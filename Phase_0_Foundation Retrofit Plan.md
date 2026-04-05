# Phase 0: Foundation Retrofit Plan

This plan retrofits the necessary organizational conventions, module architectures, CI workflows, and documentation standard to our existing Phase 1 architecture without breaking any backend logic or front-end integrations. 

## User Review Required

> [!WARNING]
> Please review the strategy for the **Shared Contracts** layer. Since the backend is Python and the frontend is TypeScript, I intend to define the frontend data contracts in a new local npm package called `packages/shared-types`, and export Pydantic models for the backend under `apps/backend/src/schemas/`. They will mechanically align, and I will document their API mapping in `docs/api_contracts.md`. Does this multi-language contract approach satisfy the requirements, or would you prefer automated generation like `openapi-typescript`? I recommend manuall typed boundaries for MVP.

## Proposed Changes

### 1. Monorepo Setup & Docs
- **[NEW]** `docs/architecture.md` (Explaining module boundaries)
- **[NEW]** `docs/ADR-001-unified-backend.md` (Documenting the single Python `apps/backend` decision)
- **[NEW]** `docs/contributing.md` (Branch, PR, and commit strategies)
- **[MODIFY]** `README.md` (Streamlined developer onboarding & healthcheck instructions)

### 2. GitHub Templates & CI Pipeline
- **[NEW]** `.github/ISSUE_TEMPLATE/feature_request.md`
- **[NEW]** `.github/ISSUE_TEMPLATE/bug_report.md`
- **[NEW]** `.github/ISSUE_TEMPLATE/chore.md`
- **[NEW]** `.github/pull_request_template.md`
- **[NEW]** `.github/workflows/ci.yml` (GitHub Actions: Lint, Backend pytest execution, Next.js build)

### 3. Environment & Configuration
- **[MODIFY]** `.env.example` (Clear separation of Required vs Optional fields with standardized naming)

### 4. Code Architecture - Shared Contracts
- **[NEW]** `packages/shared-types/package.json`
- **[NEW]** `packages/shared-types/index.ts` (TS endpoints, enums for Parse Statuses)
- **[NEW]** `apps/backend/src/schemas/` (Pydantic shared models from current routers)
- **[NEW]** `docs/api_contracts.md`
- **[MODIFY]** `apps/web/tsconfig.json` (Link `@jobtailor/shared-types`)
- **[MODIFY]** `apps/web` components to use the shared types instead of dynamic objects.

### 5. Code Architecture - Standardized Logging
- **[NEW]** `apps/backend/src/utils/logger.py` (Structured Logging formatter with generic `request_id`, `user_id`, `document_id`)
- **[NEW]** `docs/logging.md` (Documentation of fields and phases)
- **[MODIFY]** `apps/backend/src/worker/tasks.py` (Refit the current logging to use the centralized framework)
- **[MODIFY]** `apps/backend/src/routers/documents.py` (Include structured logging to trace file uploads)

## Open Questions

- Should we strictly mandate conventional commits (e.g. `feat: `, `fix: `) inside the CI pipeline itself? (I'll propose adding a simple branch/commit naming convention document, but omit a strict GitHook barrier to maintain MVP speed unless otherwise asked).

## Verification Plan
1. `docker-compose up` cleanly launches DB, Redis, MinIO, Backend, Backend-Worker.
2. Ensure Frontend (`apps/web`) still allows Upload functionality and statuses map identically.
3. Observe localized backend logs to verify structured `user_id` & `document_id` JSON structure.
4. CI checks via GitHub simulate a successful `fastapi` style type check/pytest execution.
