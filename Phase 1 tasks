# JobTailor Phase 1 Tasks

- `[/]` 1. **Project Initialization & Infrastructure**
  - `[ ]` Create root directory structure (`apps`, `infra`)
  - `[ ]` Write `docker-compose.yml` (Postgres, Redis, MinIO)
  - `[ ]` Write MinIO bucket creation script (`create-buckets.sh`)
  - `[ ]` Create root `.env.example` file
  - `[ ]` Set up basic `Makefile` or README instructions

- `[x]` 2. **Backend Setup (`apps/backend`)**
  - `[x]` Initialize poetry/requirements.txt with FastAPI, Celery, SQLAlchemy, Alembic, MinIO SDK, PyMuPDF, python-docx
  - `[x]` Create `database` module with SQLAlchemy setup
  - `[x]` Create SQLAlchemy models (`User`, `Session`, `Document`, `DocumentParseEvent`)
  - `[x]` Initialize Alembic and create initial migration

- `[x]` 3. **Authentication API**
  - `[x]` Implement `/api/auth/login/linkedin` with Mock support
  - `[x]` Implement `/api/auth/callback/linkedin` + session creation
  - `[x]` Implement `/api/auth/me` and logout

- `[x]` 4. **Upload and Storage API**
  - `[x]` Create MinIO storage utility
  - `[x]` Implement `/api/documents/upload` endpoint
  - `[x]` Queue Celery tasks on upload
  - `[x]` Implement GET `/api/documents` endpoints

- `[x]` 5. **Worker Setup**
  - `[x]` Create Celery app configuration (`apps/backend/src/worker/celery_app.py`)
  - `[x]` Implement PDF Text Extractor (`pdf_parser.py`)
  - `[x]` Implement DOCX Text Extractor (`docx_parser.py`)
  - `[x]` Implement LinkedIn Export Extractor (`linkedin_export_parser.py`)
  - `[x]` Write text back to MinIO and update DB status

- `[x]` 6. **Frontend (`apps/web`)**
  - `[x]` Initialize Next.js project
  - `[x]` Setup Tailwind CSS nicely
  - `[x]` Build Login page with LinkedIn button
  - `[x]` Build Auth callback integration
  - `[x]` Build Dashboard page
  - `[x]` Create Upload Components with progress/state
  - `[x]` Display list of parsed documents and their statuses

- `[x]` 7. **Testing & Verification**
  - `[x]` Ensure it runs in docker-compose
  - `[x]` Run basic parse quality testing on test fixtures
