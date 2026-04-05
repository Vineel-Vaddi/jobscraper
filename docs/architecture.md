# Architecture

JobTailor utilizes a modular monorepo structure designed to balance MVP delivery speed with future scalability.

## High-Level Architecture

The system is separated into three logical planes:
1. **Frontend / Presentational Layer**: Next.js React application.
2. **Backend API Layer**: FastAPI servicing synchronous user requests.
3. **Background Worker Layer**: Celery processing asynchronous document extraction queues from Redis.

## Directory Layout

- `/apps/web`: The Next.js 14 frontend application.
- `/apps/backend`: The unified Python backend. It hosts both the FastAPI server (`src/main.py`) and the Celery workers (`src/worker/`).
- `/packages/shared-types`: (WIP) A unified contract library synchronizing TypeScript interfaces with Python Pydantic responses.
- `/docs`: Markdown documentation describing the engineering philosophy and system layout.
- `/infra/docker`: `docker-compose.yml` and related shell scripts establishing the local cluster footprint.

## Infrastructure Dependencies

- **PostgreSQL**: Used for all persistent relational data (Users, Sessions, Documents).
- **Redis**: Functions strictly as the Message Broker and Celery state backend.
- **MinIO**: S3-compatible local object storage. Stores raw user uploads and extracted string payloads. Matches exact AWS S3 APIs for seamless production migration.

## Execution Flows

### The Ingestion Flow
1. User uploads a file via the Next.js frontend (`/apps/web`).
2. Request hits FastAPI at `POST /api/documents/upload`.
3. FastAPI immediately pipes the file chunks to MinIO/S3 to avoid memory saturation.
4. FastAPI creates a `Document` record in PostgreSQL with status `pending`.
5. FastAPI enqueues a `parse_document_task` onto Redis.
6. Celery (`/apps/backend/src/worker`) picks up the task from Redis, streams the object from MinIO to memory, parses it, updates PostgreSQL, and saves the `.extracted.txt` string payload back to MinIO recursively.
