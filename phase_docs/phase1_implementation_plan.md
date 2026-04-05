# JobTailor Phase 1: Auth + Document Ingestion

This plan outlines the architecture and implementation steps to deliver Phase 1 of JobTailor, satisfying the requirements for authentication, document uploading, parsing, and infrastructure setup.

## User Review Required

> [!WARNING]  
> We need to establish a consistent approach to the Python codebase. Since `apps/api` and `apps/worker` might share many models and dependencies, I propose creating a single Python project under `apps/backend` containing both the API routes and worker tasks. Docker Compose will run two containers from the same image with different commands (`fastapi run` and `celery worker`). This prevents duplicating SQLAlchemy models, configurations, and storage clients. Please advise if this is acceptable, or if you strictly prefer separate `apps/api` and `apps/worker` Python repositories and want me to figure out a `packages/shared-python` local package setup.

## Proposed Architecture

1. **Frontend (`apps/web`)**: Next.js App Router, Tailwind CSS. Axios/Fetch for client-side API requests.
2. **Backend/API (`apps/backend`)**: FastAPI. Validates LinkedIn OIDC tokens, manages sessions, uploads files to MinIO, writes records to PostgreSQL, and pushes parse tasks to Redis. (Will run as its own Docker container).
3. **Worker (`apps/backend`)**: Python Celery worker reading off Redis async. Parsers files via PyMuPDF/docxtx/etc. (Runs as its own Docker container).
4. **Database (`infra/postgres`)**: PostgreSQL. Managed via Alembic migrations.
5. **Storage (`infra/minio`)**: MinIO instance running inside Docker. Buckets created automatically on setup.
6. **Task Queue (`infra/redis`)**: Redis locally.

## Proposed Changes

### 1. Project Initialization & Infrastructure
Set up the infra folder with a robust `docker-compose.yml` to run the stack locally.
- **[NEW]** `infra/docker/docker-compose.yml` (Postgres, Redis, MinIO, API, Worker, Web, MinIO-setup)
- **[NEW]** `.env.example`

### 2. Database Layer
Setup SQLAlchemy models and Alembic. Support User, Session, Document, and DocumentParseEvents.
- **[NEW]** `apps/backend/src/database/models.py`
  - `User`: id, linkedin_sub, email, display_name, created_at, updated_at
  - `Session`: id, user_id, expires_at
  - `Document`: id, user_id, document_type, original_filename, mime_type, file_size, storage_key, upload_status, parse_status, parse_error_code, parse_error_message, extracted_text_path, created_at, updated_at
- **[NEW]** `apps/backend/alembic/` (Migrations)

### 3. Authentication (FastAPI Layer)
Implement session-based authentication utilizing HTTP-Only cookies.
- **[NEW]** `apps/backend/src/routers/auth.py`
  - `/api/auth/login/linkedin` -> Redirects to LinkedIn Auth
  - `/api/auth/callback/linkedin` -> Exchanges code for token, upserts User, creates Session, sets HTTP-only cookie.
  - `/api/auth/me` -> Validate session cookie and return User
  - `/api/auth/logout` -> Delete session

### 4. Upload Flows (FastAPI Layer)
Implement endpoints for secure upload to MinIO.
- **[NEW]** `apps/backend/src/routers/upload.py`
  - `/api/documents/upload` -> Receives file, validates type/size, creates pending DB record, uploads to MinIO, updates DB, queues `parse_document` Celery job.
- **[NEW]** `apps/backend/src/routers/documents.py`
  - `/api/documents` -> List documents for current user
  - `/api/documents/{doc_id}` -> Details and parse output/status

### 5. Raw Text Extraction Service (Worker Layer)
Celery worker consuming tasks from Redis to parse the documents.
- **[NEW]** `apps/backend/src/worker/tasks.py` -> Celery task definitions
- **[NEW]** `apps/backend/src/worker/parsers/pdf_parser.py` -> PyMuPDF extraction
- **[NEW]** `apps/backend/src/worker/parsers/docx_parser.py` -> python-docx extraction
- **[NEW]** `apps/backend/src/worker/parsers/linkedin_export_parser.py` -> ZIP logic
- **[NEW]** `apps/backend/src/worker/services/document_service.py` -> Co-ordinates getting file from MinIO, identifying parser, saving raw text back to MinIO (`extracted_text_path`), and updating PostgreSQL DB statuses.

### 6. Frontend Next.js Screens
Clean Tailwind-powered UI that integrates the backend flow.
- **[NEW]** `apps/web/app/page.tsx` -> Landing and Login Screen.
- **[NEW]** `apps/web/app/dashboard/page.tsx` -> Secure Dashboard showing "Resume" and "LinkedIn Export" upload cards.
- **[NEW]** `apps/web/components/UploadCard.tsx` -> File input, sizes, types validation, and upload progress.
- **[NEW]** `apps/web/components/DocumentList.tsx` -> Fetch documents per user and display processing state.

## Open Questions

1.  **Codebase Structure**: Do you agree with the single `apps/backend` monorepo approach for Python services, instead of duplicated code in `apps/api` and `apps/worker`?
2.  **Mocking LinkedIn Auth**: For local development before you register an actual LinkedIn App with keys, would you like me to build a mock authentication endpoint (`MOCK_LINKEDIN=true`) that logs in a test user to ease local dev?
3.  **Frontend Auth**: I'm proposing standard HTTP-Only session cookies where the Python backend sets the cookie upon `/api/auth/callback/linkedin`. This prevents the need for a separate auth layer like NextAuth.js. Is this acceptable?

## Verification Plan

### Automated Tests
- PyTest test cases inside `apps/backend/tests` to verify parsing accuracy on sample fixtures.
- PyTest for FastAPI endpoints (Mock MinIO).

### Manual Verification
- `docker-compose up` to run the stack.
- Login via UI.
- Upload PDF, ZIP, and DOCX files.
- Ensure status changes to `Processing` and then `Success`, and extracted text is retrievable.
