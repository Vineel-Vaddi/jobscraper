# Logging Conventions

To maintain queryability and observability throughout Phase 2, all backend logs must be structured as JSON.

## Standard Fields
When calling the structured logger natively via `src.utils.logger.log`, you can inject context parameters using the `extra={}` dictionary:

- `request_id`: A UUID created via middleware for synchronous HTTP calls.
- `user_id`: ID of the user performing the upload/action.
- `document_id`: The database Document ID actively being processed.
- `task_id`: The Celery background task ID matching Redis signatures.
- `phase`: A string specifying logical pipeline block (e.g. `upload`, `download`, `extraction`, `db_sync`).
- `status`: Typically `start`, `success`, or `failed`.
- `duration_ms`: Execution boundaries when finishing a phase block.
- `error_code`: High-level category standard mapping for observability (e.g., `UNSUPPORTED_FORMAT`, `CORRUPT_ARCHIVE`).

## Example Usage
```python
from src.utils.logger import log

log.info(
    "Uploading document payload", 
    extra={
        "user_id": 4, 
        "phase": "upload", 
        "status": "start"
    }
)
```
