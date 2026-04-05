# JobTailor Phase 0 Tasks

- `[x]` 1. **Monorepo Setup & Documentation**
  - `[x]` Write `docs/architecture.md` defining module boundaries
  - `[x]` Write `docs/ADR-001-unified-backend.md` explaining unified Python service
  - `[x]` Write `docs/contributing.md` branching, PR, and commit strategies
  - `[x]` Update `README.md` to resolve startup ambiguity

- `[x]` 2. **Shared Contracts**
  - `[x]` Create `packages/shared-types` with `package.json` and `index.ts`
  - `[x]` Create `apps/backend/src/schemas` and standardize Pydantic shapes
  - `[x]` Unify frontend `DocumentList` and `UploadCard` to use shared types
  - `[x]` Write `docs/api_contracts.md`
  
- `[x]` 3. **GitHub Templates & CI**
  - `[x]` Add issue and PR templates mapping to conventions
  - `[x]` Add GitHub Action `.github/workflows/ci.yml`

- `[x]` 4. **Logging Conventions**
  - `[x]` Create `apps/backend/src/utils/logger.py` with structured logging format
  - `[x]` Integrate Logger into `tasks.py` worker flows
  - `[x]` Integrate Logger into `documents.py` router flows
  - `[x]` Write `docs/logging.md`

- `[x]` 5. **Environment Configuration**
  - `[x]` Refactor `.env.example` to distinctly label required vs optional fields
