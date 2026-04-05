# ADR 001: Unified Python Backend Source

**Status:** Accepted
**Date:** 2026-04-05

## Context

JobTailor requires a synchronous API (to manage user sessions, file uploads, and status queries) and an asynchronous background worker computing intensive text extractions (PDFs, DOCX, ZIPs). Traditionally, these two domain boundaries can map to completely discrete code repositories.

## Decision

We have decided to combine the FastAPI service (`apps/backend/src/main.py`) and the Celery workers (`apps/backend/src/worker/`) into a single localized python repository housed within `/apps/backend`.

## Consequences

### Positive
- **DRY Data Models**: We are able to define the SQLAlchemy models, PyDantic schemas, and Alembic migrations exactly once without writing a separate Python Package distribution pipeline to connect them.
- **Shared Infrastructure Clients**: Both FastAPI and Celery directly load the exact same `src.database.database` connections and generic `src.utils.storage` MinIO abstractions. 
- **Tooling Consolidation**: We rely on a single `requirements.txt` environment and `pytest` suite for the bulk of backend functionality.

### Negative
- **Docker Image Bloat**: The FastAPI container and Celery container mount the exact same `Dockerfile` containing dependencies mutually exclusive to each context (e.g. `fastapi` vs `PyMuPDF`).
- **Separation of Concerns Risk**: Developers must be trained to cleanly separate synchronous Web logic from asynchronous Worker logic, to prevent HTTP controllers from directly calling worker subroutines synchronously.
