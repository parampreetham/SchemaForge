# Database Schema

---

## Entity Relationship Diagram

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐
│  users   │────▶│   projects   │────▶│pipeline_jobs│
└──────────┘     └──────────────┘     └──────┬──────┘
                                             │
                       ┌─────────────────────┼─────────────────┐
                       ▼                     ▼                 ▼
                ┌─────────────┐      ┌──────────────┐  ┌──────────────┐
                │ chunk_tasks │      │  log_entries  │  │  ai_interactions│
                └──────┬──────┘      └──────────────┘  └──────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
       ┌─────────────┐  ┌──────────────────┐
       │  artifacts  │  │validation_results│
       └─────────────┘  └──────────────────┘

       ┌───────────────────┐
       │ worker_heartbeats │  (independent)
       └───────────────────┘
```

---

## Table Definitions

### users

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Unique user identifier |
| `username` | `VARCHAR(100)` | UNIQUE, NOT NULL | Login username |
| `email` | `VARCHAR(255)` | UNIQUE, NOT NULL | User email |
| `password_hash` | `VARCHAR(255)` | NOT NULL | bcrypt hashed password |
| `role` | `VARCHAR(20)` | NOT NULL, DEFAULT 'operator' | 'admin', 'operator', 'viewer' |
| `is_active` | `BOOLEAN` | NOT NULL, DEFAULT true | Soft delete flag |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Account creation time |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Last update time |

**Indexes**: `ix_users_email`, `ix_users_username`

---

### projects

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Unique project identifier |
| `name` | `VARCHAR(200)` | NOT NULL | Project display name |
| `description` | `TEXT` | NULLABLE | Optional description |
| `source_db_type` | `VARCHAR(50)` | NOT NULL, DEFAULT 'db2' | Source database type |
| `target_db_type` | `VARCHAR(50)` | NOT NULL, DEFAULT 'azure_sql' | Target database type |
| `source_db_version` | `VARCHAR(50)` | NULLABLE | e.g., 'DB2 for LUW 11.5' |
| `created_by` | `UUID` | FK → users.id, NOT NULL | Owner user |
| `is_archived` | `BOOLEAN` | NOT NULL, DEFAULT false | Archive flag |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | |

**Indexes**: `ix_projects_created_by`, `ix_projects_created_at`

---

### pipeline_jobs

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Unique job identifier |
| `project_id` | `UUID` | FK → projects.id, NOT NULL | Parent project |
| `status` | `VARCHAR(20)` | NOT NULL, DEFAULT 'created' | See state machine below |
| `total_chunks` | `INTEGER` | NOT NULL, DEFAULT 0 | Total chunks in pipeline |
| `completed_chunks` | `INTEGER` | NOT NULL, DEFAULT 0 | Completed chunk count |
| `failed_chunks` | `INTEGER` | NOT NULL, DEFAULT 0 | Failed chunk count |
| `progress_pct` | `DECIMAL(5,2)` | NOT NULL, DEFAULT 0.00 | 0.00 – 100.00 |
| `original_file_path` | `VARCHAR(500)` | NOT NULL | Path to uploaded schema |
| `original_file_size` | `BIGINT` | NOT NULL | File size in bytes |
| `cancel_requested` | `BOOLEAN` | NOT NULL, DEFAULT false | Cancel signal |
| `error_message` | `TEXT` | NULLABLE | Pipeline-level error |
| `ai_tokens_used` | `INTEGER` | NOT NULL, DEFAULT 0 | Total AI tokens consumed |
| `ai_cost_usd` | `DECIMAL(10,4)` | NOT NULL, DEFAULT 0 | Total AI cost |
| `created_by` | `UUID` | FK → users.id, NOT NULL | User who started |
| `started_at` | `TIMESTAMPTZ` | NULLABLE | When processing began |
| `completed_at` | `TIMESTAMPTZ` | NULLABLE | When pipeline finished |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | |

**Valid statuses**: `created`, `queued`, `running`, `paused`, `cancelling`, `cancelled`, `failed`, `retrying`, `completed`

**Indexes**: `ix_pipeline_jobs_project_id`, `ix_pipeline_jobs_status`, `ix_pipeline_jobs_created_by`

---

### chunk_tasks

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Unique task identifier |
| `job_id` | `UUID` | FK → pipeline_jobs.id, NOT NULL | Parent pipeline |
| `object_name` | `VARCHAR(255)` | NOT NULL | DB object name (e.g., 'EMPLOYEE_TABLE') |
| `object_type` | `VARCHAR(50)` | NOT NULL | 'TABLE', 'VIEW', 'PROCEDURE', 'TRIGGER', etc. |
| `status` | `VARCHAR(20)` | NOT NULL, DEFAULT 'pending' | See state machine |
| `conversion_method` | `VARCHAR(20)` | NULLABLE | 'deterministic', 'ai', 'hybrid' |
| `confidence_score` | `DECIMAL(3,2)` | NULLABLE | 0.00 – 1.00 |
| `retry_count` | `INTEGER` | NOT NULL, DEFAULT 0 | Current retry attempt |
| `max_retries` | `INTEGER` | NOT NULL, DEFAULT 3 | Maximum allowed retries |
| `execution_time_ms` | `INTEGER` | NULLABLE | Processing duration |
| `original_sql` | `TEXT` | NOT NULL | Original DB2 SQL |
| `converted_sql` | `TEXT` | NULLABLE | Converted T-SQL |
| `error_message` | `TEXT` | NULLABLE | Last error message |
| `dependency_order` | `INTEGER` | NOT NULL, DEFAULT 0 | Topological sort order |
| `dependencies` | `JSONB` | NOT NULL, DEFAULT '[]' | List of dependent object names |
| `worker_id` | `VARCHAR(100)` | NULLABLE | Worker processing this task |
| `started_at` | `TIMESTAMPTZ` | NULLABLE | |
| `completed_at` | `TIMESTAMPTZ` | NULLABLE | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | |

**Valid statuses**: `pending`, `queued`, `processing`, `validating`, `completed`, `retry_pending`, `failed`, `manual_review`

**Indexes**: `ix_chunk_tasks_job_id`, `ix_chunk_tasks_status`, `ix_chunk_tasks_object_type`, `ix_chunk_tasks_job_id_status` (composite)

---

### artifacts

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | |
| `task_id` | `UUID` | FK → chunk_tasks.id, NOT NULL | Parent task |
| `artifact_type` | `VARCHAR(50)` | NOT NULL | 'original', 'parsed_ast', 'converted', 'validated', 'retry_N' |
| `version` | `INTEGER` | NOT NULL, DEFAULT 1 | Artifact version (increments on retry) |
| `storage_path` | `VARCHAR(500)` | NOT NULL | Relative file path |
| `file_size` | `BIGINT` | NULLABLE | Size in bytes |
| `checksum` | `VARCHAR(64)` | NULLABLE | SHA-256 hash |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | |

**Indexes**: `ix_artifacts_task_id`, `ix_artifacts_artifact_type`

---

### log_entries

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | Auto-incrementing ID |
| `correlation_id` | `UUID` | NOT NULL | Request/task correlation ID |
| `job_id` | `UUID` | FK → pipeline_jobs.id, NULLABLE | Parent job (if applicable) |
| `task_id` | `UUID` | FK → chunk_tasks.id, NULLABLE | Parent task (if applicable) |
| `log_level` | `VARCHAR(10)` | NOT NULL | 'debug', 'info', 'warning', 'error', 'critical' |
| `stage` | `VARCHAR(50)` | NOT NULL | 'parsing', 'conversion', 'validation', 'retry', 'system' |
| `worker_id` | `VARCHAR(100)` | NULLABLE | Worker that produced log |
| `message` | `TEXT` | NOT NULL | Log message |
| `metadata` | `JSONB` | NOT NULL, DEFAULT '{}' | Additional structured data |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | |

**Indexes**: `ix_log_entries_job_id`, `ix_log_entries_task_id`, `ix_log_entries_stage`, `ix_log_entries_created_at`, `ix_log_entries_log_level`

> **Note**: Consider partitioning by `created_at` for large deployments.

---

### ai_interactions

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | |
| `task_id` | `UUID` | FK → chunk_tasks.id, NOT NULL | Parent task |
| `attempt_number` | `INTEGER` | NOT NULL | 1, 2, 3... |
| `model` | `VARCHAR(100)` | NOT NULL | e.g., 'gpt-4o', 'claude-sonnet-4' |
| `prompt_version` | `VARCHAR(20)` | NOT NULL | e.g., 'procedure_v1' |
| `system_prompt` | `TEXT` | NOT NULL | System prompt sent |
| `user_prompt` | `TEXT` | NOT NULL | User prompt sent |
| `response` | `TEXT` | NOT NULL | Full AI response |
| `input_tokens` | `INTEGER` | NOT NULL | |
| `output_tokens` | `INTEGER` | NOT NULL | |
| `cost_usd` | `DECIMAL(10,6)` | NOT NULL | Calculated cost |
| `latency_ms` | `INTEGER` | NOT NULL | API call duration |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | |

**Indexes**: `ix_ai_interactions_task_id`

---

### validation_results

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | |
| `task_id` | `UUID` | FK → chunk_tasks.id, NOT NULL | Parent task |
| `attempt_number` | `INTEGER` | NOT NULL | Validation attempt |
| `passed` | `BOOLEAN` | NOT NULL | Pass/fail |
| `error_code` | `VARCHAR(20)` | NULLABLE | SQL Server error code |
| `error_message` | `TEXT` | NULLABLE | Full error text |
| `error_line` | `INTEGER` | NULLABLE | Line number of error |
| `validated_sql` | `TEXT` | NOT NULL | SQL that was validated |
| `execution_time_ms` | `INTEGER` | NULLABLE | Validation duration |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | |

**Indexes**: `ix_validation_results_task_id`

---

### worker_heartbeats

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | |
| `worker_id` | `VARCHAR(100)` | UNIQUE, NOT NULL | Worker identifier |
| `queue_name` | `VARCHAR(50)` | NOT NULL | Queue this worker serves |
| `status` | `VARCHAR(20)` | NOT NULL, DEFAULT 'idle' | 'idle', 'busy', 'stopped' |
| `current_task_id` | `UUID` | NULLABLE | Task currently processing |
| `pid` | `INTEGER` | NOT NULL | OS process ID |
| `hostname` | `VARCHAR(255)` | NOT NULL | Machine hostname |
| `last_heartbeat` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Last ping time |
| `started_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT now() | Worker start time |

**Indexes**: `ix_worker_heartbeats_last_heartbeat`

---

## Migration Strategy

- All migrations managed via **Alembic**
- Migrations are **forward-only** in production (rollback via new migration)
- Migration naming: `{revision}_{description}.py` (e.g., `0001_initial_schema.py`)
- Every migration includes both `upgrade()` and `downgrade()` functions
- Run `alembic upgrade head` on application startup
