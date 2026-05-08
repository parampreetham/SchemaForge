# Observability & Monitoring

---

## Observability Goals

| Goal | Metric | Why |
|---|---|---|
| Worker health | Heartbeat age, status | Detect crashed/hung workers |
| Queue health | Queue depth per queue | Detect bottlenecks |
| Pipeline progress | Completion %, duration | Track migration progress |
| Retry rates | Retry count per pipeline | Detect systematic conversion issues |
| AI cost tracking | Tokens used, cost USD | Budget management |
| Failure hotspots | Failed chunks by object type | Target improvement areas |

---

## Logging

### Framework
- **structlog** with JSON output
- All logs are JSON-formatted
- Logs written to: stdout + database (`log_entries` table)

### Required Fields (Every Log Entry)

```json
{
  "timestamp": "2026-01-15T10:30:00.123Z",
  "level": "info",
  "correlation_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "service": "worker",
  "worker_id": "conversion-worker-2",
  "job_id": "job-101",
  "task_id": "task-88",
  "stage": "validation",
  "message": "Chunk validation completed",
  "duration_ms": 450,
  "metadata": {
    "object_name": "SP_CALCULATE_INTEREST",
    "object_type": "PROCEDURE",
    "attempt": 2
  }
}
```

### Log Levels

| Level | Usage | Examples | Persist to DB |
|---|---|---|---|
| `debug` | Detailed diagnostics | SQL being processed, AST nodes | No (dev only) |
| `info` | Normal operations | Task started, task completed, pipeline created | Yes |
| `warning` | Recoverable issues | Retry triggered, slow AI response, high queue depth | Yes |
| `error` | Operation failures | Validation failed, AI timeout, DB connection error | Yes |
| `critical` | System failures | Worker crash, disk full, all connections exhausted | Yes + Alert |

### Correlation ID Propagation
```
API Request → correlation_id generated in middleware
    ↓
Service call → correlation_id in context
    ↓
Queue message → correlation_id in job metadata
    ↓
Worker execution → correlation_id bound to structlog context
    ↓
All logs from this request/task share the same correlation_id
```

---

## Health Check Endpoints

### `GET /health` — Liveness Check
```json
{
  "status": "ok",
  "timestamp": "2026-01-15T10:30:00Z"
}
```
Returns `200` if API process is running. No dependency checks.

### `GET /health/ready` — Readiness Check
```json
{
  "status": "ready",
  "checks": {
    "database": { "status": "ok", "latency_ms": 5 },
    "redis": { "status": "ok", "latency_ms": 2 },
    "workers": {
      "status": "degraded",
      "active": 3,
      "expected": 4,
      "stale": ["conversion-worker-4"]
    }
  },
  "timestamp": "2026-01-15T10:30:00Z"
}
```
Returns `200` if all critical dependencies are healthy, `503` if degraded.

### `GET /health/workers` — Worker Detail
```json
{
  "workers": [
    {
      "worker_id": "parsing-worker-1",
      "queue": "parsing",
      "status": "idle",
      "last_heartbeat": "2026-01-15T10:29:45Z",
      "uptime_seconds": 3600,
      "tasks_completed": 42,
      "current_task": null
    }
  ]
}
```

---

## Metrics (Tier 2+ — Prometheus)

### System Metrics

| Metric | Type | Description |
|---|---|---|
| `schemaforge_worker_count` | Gauge | Number of active workers by queue |
| `schemaforge_queue_depth` | Gauge | Number of pending tasks per queue |
| `schemaforge_queue_latency_seconds` | Histogram | Time tasks spend waiting in queue |
| `schemaforge_worker_task_duration_seconds` | Histogram | Task processing duration |
| `schemaforge_db_connection_pool_size` | Gauge | Active DB connections |
| `schemaforge_db_query_duration_seconds` | Histogram | Database query latency |

### Business Metrics

| Metric | Type | Description |
|---|---|---|
| `schemaforge_pipeline_total` | Counter | Total pipelines created (by status) |
| `schemaforge_chunk_total` | Counter | Total chunks processed (by status, type) |
| `schemaforge_conversion_success_rate` | Gauge | % of chunks passing validation |
| `schemaforge_retry_total` | Counter | Total retries (by object type) |
| `schemaforge_ai_tokens_total` | Counter | Total AI tokens consumed |
| `schemaforge_ai_cost_usd_total` | Counter | Cumulative AI cost |
| `schemaforge_ai_latency_seconds` | Histogram | AI API call duration |
| `schemaforge_validation_pass_rate` | Gauge | Validation pass % (first attempt vs retries) |

---

## Dashboard Metrics (Built-in MVP)

Since Prometheus is future scope, the MVP dashboard uses **database-driven metrics**:

### Dashboard Cards
| Card | Query | Refresh |
|---|---|---|
| Active Pipelines | `SELECT COUNT(*) FROM pipeline_jobs WHERE status = 'running'` | 5s |
| Queue Depth | `SELECT queue_name, COUNT(*) FROM chunk_tasks WHERE status = 'queued' GROUP BY queue_name` | 5s |
| Worker Health | `SELECT * FROM worker_heartbeats WHERE last_heartbeat > now() - interval '120s'` | 10s |
| Today's Completions | `SELECT COUNT(*) FROM pipeline_jobs WHERE status = 'completed' AND completed_at > CURRENT_DATE` | 30s |
| Failure Rate | `SELECT ROUND(100.0 * failed / total, 1) FROM (...)` | 30s |
| AI Cost (Today) | `SELECT SUM(ai_cost_usd) FROM pipeline_jobs WHERE created_at > CURRENT_DATE` | 60s |

---

## Alerting Rules (Future — Tier 2+)

| Alert | Condition | Severity | Action |
|---|---|---|---|
| Worker Down | Heartbeat stale > 2 min | Critical | Restart worker, requeue tasks |
| Queue Backlog | Queue depth > 100 for > 5 min | Warning | Scale workers |
| High Retry Rate | Retry rate > 30% in last hour | Warning | Check AI prompts, review failing objects |
| AI Cost Spike | Cost > $10/hour | Warning | Pause pipeline, review token usage |
| Pipeline Stuck | Running > 6 hours with no progress | Error | Investigate hung workers |
| Disk Space Low | < 5GB free | Critical | Clean old artifacts |
| DB Connection Exhausted | Pool utilization > 90% | Error | Increase pool size |

---

## Audit Trail

### What Is Audited

| Event | Data Captured |
|---|---|
| User login/logout | user_id, timestamp, IP |
| Pipeline created | user_id, project_id, pipeline_id, file details |
| Pipeline started/paused/cancelled | user_id, pipeline_id, action, timestamp |
| Settings changed | user_id, setting_key, old_value, new_value |
| AI provider configured | user_id, provider, model (not API key) |

### Audit Log Format
```json
{
  "event": "pipeline.started",
  "user_id": "user-123",
  "resource_type": "pipeline",
  "resource_id": "pipeline-456",
  "action": "start",
  "details": {
    "total_chunks": 200,
    "ai_provider": "openai"
  },
  "timestamp": "2026-01-15T10:30:00Z"
}
```

---

## Log Retention

| Tier | Retention | Strategy |
|---|---|---|
| Desktop (Tier 1) | 90 days | Automatic cleanup via CleanupWorker |
| Server (Tier 2) | 1 year | Partition by month, archive old partitions |
| Cloud (Tier 3) | 2 years | Move to cold storage after 90 days |
