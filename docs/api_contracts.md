# API Contracts

This document explains the standard REST API boundaries between the Next.js frontend and the FastAPI backend.

## Contract Architecture (Unified Typings)
Because JobTailor utilizes a multi-language microservices architecture (TypeScript and Python), we strictly enforce mapping standard responses utilizing:
1. **Frontend:** Types statically defined in `packages/shared-types`.
2. **Backend:** Pydantic serializers bounded within `apps/backend/src/schemas`.

## Standard Types

### `DocumentResponse`
```json
{
  "id": 1024,
  "document_type": "resume",
  "original_filename": "CV_Latest.pdf",
  "file_size": 1500000,
  "upload_status": "success",
  "parse_status": "success",
  "parse_error_code": null,
  "parse_error_message": null,
  "created_at": "2026-04-05T20:25:00Z"
}
```

### `UserResponse`
```json
{
  "id": 2048,
  "display_name": "Tyler Doe",
  "email": "tyler@example.com"
}
```
