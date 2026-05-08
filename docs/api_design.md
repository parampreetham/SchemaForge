# API Design

---

## Design Principles

| Principle | Implementation |
|---|---|
| RESTful | Resources as nouns, HTTP verbs for actions |
| Versioned | `/api/v1/` prefix on all endpoints |
| Consistent | Uniform response structure across all endpoints |
| Paginated | All list endpoints return paginated responses |
| Documented | Auto-generated OpenAPI spec via FastAPI |
| Authenticated | JWT Bearer token on all endpoints (except health) |

---

## Base URL

```
http://localhost:8000/api/v1
```

---

## Authentication

### `POST /api/v1/auth/register`

Register a new user.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "operator",
  "created_at": "2026-01-15T10:30:00Z"
}
```

### `POST /api/v1/auth/login`

Authenticate and receive JWT token.

**Request:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "role": "operator"
  }
}
```

### `POST /api/v1/auth/logout`

Invalidate current session.

**Response (200):**
```json
{ "message": "Logged out successfully" }
```

---

## Projects

### `GET /api/v1/projects`

List all projects for current user.

**Query Parameters:**
| Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |
| `sort` | string | `-created_at` | Sort field (prefix `-` for desc) |
| `archived` | bool | false | Include archived projects |

**Response (200):**
```json
{
  "data": [
    {
      "id": "proj-123",
      "name": "Legacy Banking DB2 Migration",
      "source_db_type": "db2",
      "target_db_type": "azure_sql",
      "pipeline_count": 3,
      "created_at": "2026-01-10T08:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 5,
    "total_pages": 1
  }
}
```

### `POST /api/v1/projects`

Create a new project.

**Request:**
```json
{
  "name": "Legacy Banking DB2 Migration",
  "description": "Migrating core banking schema from DB2 11.5 to Azure SQL",
  "source_db_type": "db2",
  "target_db_type": "azure_sql",
  "source_db_version": "DB2 for LUW 11.5"
}
```

**Response (201):** Full project object.

### `GET /api/v1/projects/{project_id}`

Get project details.

### `PATCH /api/v1/projects/{project_id}`

Update project metadata.

### `POST /api/v1/projects/{project_id}/archive`

Archive a project (soft delete).

---

## Pipelines

### `POST /api/v1/projects/{project_id}/pipelines`

Create and start a new migration pipeline.

**Request:** `multipart/form-data`
| Field | Type | Description |
|---|---|---|
| `schema_file` | File | DB2 DDL file (.sql, .ddl) |
| `ai_provider` | string | `"openai"` or `"anthropic"` |
| `max_retries` | int | Max retries per chunk (default: 3) |
| `budget_usd` | float | Max AI cost budget (default: 50.0) |

**Response (201):**
```json
{
  "id": "pipe-456",
  "project_id": "proj-123",
  "status": "queued",
  "total_chunks": 0,
  "completed_chunks": 0,
  "progress_pct": 0.0,
  "original_file_size": 52428800,
  "created_by": "user-123",
  "created_at": "2026-01-15T10:30:00Z"
}
```

### `GET /api/v1/projects/{project_id}/pipelines`

List pipelines for a project.

### `GET /api/v1/pipelines/{pipeline_id}`

Get pipeline details with full progress.

**Response (200):**
```json
{
  "id": "pipe-456",
  "status": "running",
  "total_chunks": 200,
  "completed_chunks": 142,
  "failed_chunks": 3,
  "progress_pct": 71.0,
  "ai_tokens_used": 450000,
  "ai_cost_usd": 12.50,
  "stages": {
    "parsing": { "total": 200, "completed": 200, "status": "completed" },
    "conversion": { "total": 200, "completed": 155, "status": "running" },
    "validation": { "total": 155, "completed": 142, "status": "running" }
  },
  "started_at": "2026-01-15T10:31:00Z",
  "elapsed_seconds": 3600,
  "estimated_remaining_seconds": 1440
}
```

### `POST /api/v1/pipelines/{pipeline_id}/pause`

Pause a running pipeline.

**Response (200):** `{ "status": "paused" }`

### `POST /api/v1/pipelines/{pipeline_id}/resume`

Resume a paused pipeline.

**Response (200):** `{ "status": "running" }`

### `POST /api/v1/pipelines/{pipeline_id}/cancel`

Cancel a running/paused pipeline.

**Response (200):** `{ "status": "cancelling" }`

---

## Chunks

### `GET /api/v1/pipelines/{pipeline_id}/chunks`

List chunks for a pipeline with filtering.

**Query Parameters:**
| Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `page_size` | int | 50 | Items per page (max 200) |
| `status` | string | — | Filter by status |
| `object_type` | string | — | Filter by type (TABLE, PROCEDURE, etc.) |
| `sort` | string | `dependency_order` | Sort field |

### `POST /api/v1/chunks/{chunk_id}/retry`

Retry a failed chunk.

**Response (200):**
```json
{
  "id": "chunk-88",
  "status": "queued",
  "retry_count": 2,
  "max_retries": 3,
  "message": "Chunk requeued for retry"
}
```

---

## Logs

### `GET /api/v1/logs`

Query logs with filtering.

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| `job_id` | UUID | Filter by pipeline |
| `task_id` | UUID | Filter by chunk |
| `level` | string | `info`, `warning`, `error`, `critical` |
| `stage` | string | `parsing`, `conversion`, `validation`, `retry` |
| `since` | datetime | Logs after this timestamp |
| `page` | int | Page number |
| `page_size` | int | Items per page |

---

## Artifacts

### `GET /api/v1/artifacts/{artifact_id}`

Get artifact metadata.

### `GET /api/v1/artifacts/{artifact_id}/download`

Download artifact file.

**Response:** File stream with `Content-Disposition: attachment`.

### `GET /api/v1/pipelines/{pipeline_id}/artifacts/download`

Download all artifacts for a pipeline as ZIP.

---

## Workers

### `GET /api/v1/workers`

Get worker health status.

**Response (200):**
```json
{
  "workers": [
    {
      "worker_id": "parsing-worker-1",
      "queue": "parsing",
      "status": "idle",
      "last_heartbeat": "2026-01-15T10:29:45Z",
      "current_task": null
    }
  ],
  "summary": {
    "total": 8,
    "idle": 5,
    "busy": 3,
    "stale": 0
  }
}
```

---

## Error Response Format

All errors follow a consistent structure:

```json
{
  "error": {
    "code": "PIPELINE_NOT_FOUND",
    "message": "Pipeline with ID pipe-999 not found",
    "detail": "The requested pipeline does not exist or you don't have access",
    "correlation_id": "abc-123-def-456"
  }
}
```

### HTTP Status Codes

| Code | Usage |
|---|---|
| 200 | Success |
| 201 | Created |
| 400 | Invalid request body / parameters |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient role) |
| 404 | Resource not found |
| 409 | Conflict (e.g., pipeline already running) |
| 422 | Validation error (Pydantic) |
| 429 | Rate limited |
| 500 | Internal server error |

### Error Codes

| Code | Description |
|---|---|
| `AUTH_INVALID_CREDENTIALS` | Wrong username or password |
| `AUTH_TOKEN_EXPIRED` | JWT token expired |
| `PROJECT_NOT_FOUND` | Project doesn't exist |
| `PIPELINE_NOT_FOUND` | Pipeline doesn't exist |
| `PIPELINE_INVALID_STATE` | Action not valid for current pipeline state |
| `CHUNK_RETRY_EXHAUSTED` | Chunk has exceeded max retries |
| `FILE_TOO_LARGE` | Uploaded file exceeds 500MB limit |
| `AI_BUDGET_EXCEEDED` | Pipeline AI cost budget exceeded |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

---

## Rate Limiting

| Endpoint Group | Limit |
|---|---|
| Auth endpoints | 10 req/min |
| Pipeline create | 5 req/min |
| Read endpoints | 200 req/min |
| Write endpoints | 100 req/min |

---

## WebSocket API (Future — v2.0)

### `WS /api/v1/ws/pipelines/{pipeline_id}`

Real-time pipeline progress updates.

```json
// Server → Client messages
{ "type": "progress", "data": { "completed_chunks": 143, "progress_pct": 71.5 } }
{ "type": "chunk_completed", "data": { "chunk_id": "chunk-89", "status": "completed" } }
{ "type": "chunk_failed", "data": { "chunk_id": "chunk-90", "error": "..." } }
{ "type": "pipeline_completed", "data": { "status": "completed" } }
```
