# JobTailor

JobTailor is a platform that allows users to seamlessly ingest resumes and LinkedIn Profiles, structuring that data for downstream semantic analysis and job-description tailoring.

## Developer Onboarding

### Primary Workflow (Docker Backend + Native Frontend)
This is the recommended workflow for developing features, keeping the backend encapsulated while allowing hot-reloading for the Next.js frontend.

1. **Environment Config**:  
   Copy the example environment securely.
   ```bash
   cp .env.example .env
   ```
2. **Boot Infrastructure & Backend Services**:  
   Run Postgres, Redis, MinIO, the FastAPI Backend, and the Celery Worker inside Docker.
   ```bash
   docker-compose -f infra/docker/docker-compose.yml up --build -d
   ```
   *(Wait 10 seconds for databases to accept connections)*
3. **Database Migrations** (First run only):
   ```bash
   docker-compose -f infra/docker/docker-compose.yml exec api alembic upgrade head
   ```
4. **Boot Frontend Native**:
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```
5. **Access Nodes**:
   - Web App UI: `http://localhost:3000`
   - FastAPI Backend: `http://localhost:8000/docs`
   - MinIO Object UI: `http://localhost:9001` (Creds: `minioadmin`/`minioadmin`)

### Secondary Workflow 
Alternatively, to run the frontend strictly through Docker, add a `web` service to `docker-compose.yml`.

## Healthchecks
The backend exports a simple availability endpoint at `http://localhost:8000/health`.
The docker-compose file inherently binds `pg_isready`, `redis-cli ping`, and `minio` healthchecks. Statuses can be reviewed via `docker ps`.

## System Documentation
Please see the `/docs` directory for detailed architecture constraints and contribution guidelines.
- [Architecture](docs/architecture.md)
- [Unified Backend ADR](docs/ADR-001-unified-backend.md)
- [Contributing](docs/contributing.md)
