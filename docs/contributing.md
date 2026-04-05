# Contributing to JobTailor

## Project Structure

This is a monorepo with two application directories and one shared package:

- `apps/web` — Next.js 14 frontend
- `apps/backend` — Unified Python backend (FastAPI + Celery)
- `packages/shared-types` — TypeScript interfaces mirroring Pydantic schemas

See [architecture.md](architecture.md) for full system design.

## Branch Naming Convention

```
[type]/[issue-number]-[short-description]
```

Valid `[type]` prefixes:
- `feat/` — new features
- `fix/` — bug fixes
- `chore/` — maintenance, dependency updates, docs

Example: `feat/12-add-resume-pinning`

## Pull Request Convention

- Reference the issue ID in the PR body (e.g. `Resolves #15`)
- Ensure all CI tests pass
- Prefix PR titles: `[Feat] Add pinning`, `[Fix] Resolve PDF parse timeout`

## Commit Style

We encourage [Conventional Commits](https://www.conventionalcommits.org/):
- `feat: add role presets CRUD`
- `fix: resolve auth session expiry`
- `chore: update Next.js template`

## Development Workflow

1. **Backend** runs inside Docker. See the README for `docker-compose` commands.
2. **Frontend** runs natively via `npm run dev` in `apps/web`.
3. **Shared types** are updated manually when Pydantic schemas change.

## Adding a New API Route

1. Create or extend a router in `apps/backend/src/routers/`
2. Add Pydantic schemas in `apps/backend/src/schemas/`
3. Register the router in `apps/backend/src/main.py`
4. Mirror the response type in `packages/shared-types/index.ts`
5. Add tests in `tests/`

## Adding a New Database Model

1. Add the SQLAlchemy model in `apps/backend/src/database/models.py`
2. Create an Alembic migration in `apps/backend/alembic/versions/`
3. Run migrations: `docker-compose exec api alembic upgrade head`

## Testing

```bash
# From apps/backend (or via Docker)
pytest tests/
```

Tests are organized by feature area under `tests/`. Use deterministic fixtures; avoid live scraping in tests.
