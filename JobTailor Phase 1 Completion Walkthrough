# JobTailor Phase 1 Completion Walkthrough

## What Was Built 

Phase 1 establishes the full end-to-end flow for user onboarding and document ingestion as described in the PRD.

### Architecture Highlights
*   **Next.js Frontend**: Simple clean web interface featuring a Landing Page (Login) and a Dashboard to upload/view documents. Uses modern Tailwind CSS.
*   **FastAPI Backend**: Uses SQLAlchemy to manage standard PostgreSQL persistent data, implements LinkedIn OAuth, handles document ingest, uses MinIO/S3 for Object Storage, and pushes jobs to Redis.
*   **Celery Workers**: Consumes Redis events asynchronously. Extracts text cleanly out of Resumes (PDF, DOCX) and LinkedIn native data exports (ZIP with nested CSVs).
*   **Infrastructure Layout**: Everything is tightly integrated via `docker-compose.yml`.

> [!TIP]
> Use `docker-compose -f infra/docker/docker-compose.yml up --build -d` to launch the persistent datastores, backend API, worker node, and object storage all concurrently!

## User Flow Visualized

1.  **Authentication**: Visiting `http://localhost:3000` prompts you to Sign In with LinkedIn. Currently, `MOCK_LINKEDIN=true` is enabled allowing seamless local developer testing without requiring internet transit or keys. This automatically securely binds a persistent `jobtailor_session` cookie pointing to the User.
2.  **Dashboard Upload**: Navigate to Dashboard. You are presented with two options. "Upload Resume" and "Upload LinkedIn Export".
3.  **Storage Engine**: On submission, chunk arrays get pushed from Next.js -> FastAPI. FastAPI instantly relays to MinIO's localized S3 bucket asynchronously creating a pending DB record.
4.  **Parsing Framework**: Once `Upload_Status="Success"`, FastAPI queues a job matching the MinIO object key into Redis. Our Celery `docker-worker` polls Redis, downloads the object to memory, dynamically triggers `PyMuPDF` or `python-docx` depending on the file, extracts string tokens, re-uploads `[original].extracted.txt` into S3, and finally updates Postgres `Parse_Status="Success"`.
5.  **Status Badges**: The frontend gracefully polls changes, displaying Real-time Badges rendering `Processing`, `Success`, or any Actionable Error Strings returned to the end-user.

## Testing Setup Complete

A test suite verifying parser integrity (`parse_pdf`, `parse_docx`, and `parse_linkedin_export`) is implemented under `tests/worker/test_parsers.py`.

## Follow-on Next Steps for Phase 2

1. **Semantic Chunking:** Transition raw text string into robust structured vectors or dictionaries containing specific experiences.
2. **LLM Evaluation Engine:** Apply generation APIs onto the text payload.
3. **AWS Staging Migration:** Exchanging local `MINIO` for AWS `S3`.
