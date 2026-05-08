# Worker Lifecycle

---

## Worker Types

| Worker | Queue | Purpose | Default Count |
|---|---|---|---|
| ParsingWorker | `parsing` | Chunk DDL, generate AST, build dependencies | 2 |
| ConversionWorker | `conversion` | Deterministic + AI conversion | 4 |
| ValidationWorker | `validation` | Execute SQL validation, trigger retries | 2 |
| CleanupWorker | `cleanup` | Orphan detection, heartbeat cleanup | 1 (scheduled) |

---

## Worker Boot Sequence

```
┌──────────────────────────┐
│ 1. Process Start         │
│    (spawned by runner)   │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 2. Load Configuration    │
│    (.env → Settings)     │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 3. Connect PostgreSQL    │───── Retry 3x with backoff
│    (test connection)     │      Fail: exit with error code 1
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 4. Connect Redis         │───── Retry 3x with backoff
│    (test connection)     │      Fail: exit with error code 2
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 5. Register Heartbeat    │
│    INSERT worker_heartbeats│
│    (worker_id, queue,    │
│     pid, hostname)       │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 6. Setup Signal Handlers │
│    SIGTERM → graceful    │
│    SIGINT  → graceful    │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 7. Start Heartbeat Timer │
│    (every 30 seconds)    │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 8. Listen on Queue       │
│    BLPOP on assigned     │
│    queue (blocking)      │
└──────────────────────────┘
```

---

## Worker Execution Loop

```
┌──────────────────────────┐
│ Fetch Task from Queue    │ ← BLPOP (blocking pop)
│ (timeout: 5 seconds)     │
└────────────┬─────────────┘
             │ task received
             ▼
┌──────────────────────────┐
│ Update Heartbeat         │
│ status = 'busy'          │
│ current_task_id = {id}   │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ Load Task from DB        │
│ Check: status valid?     │
│ Check: job not cancelled?│
└────────────┬─────────────┘
             │
      ┌──────┴──────┐
      │             │
   valid         invalid (job cancelled, task already done)
      │             │
      │         ┌───▼───────────────┐
      │         │ Skip + Log        │
      │         │ (return to queue) │
      │         └───────────────────┘
      ▼
┌──────────────────────────┐
│ Load Checkpoint          │
│ (if resuming after crash)│
│ - Last completed step    │
│ - Partial results        │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ Execute Task Logic       │
│ (Parsing / Conversion /  │
│  Validation — depends    │
│  on worker type)         │
│                          │
│ Progress callbacks:      │
│ - Update chunk status    │
│ - Log progress events    │
│ - Save checkpoints       │
└────────────┬─────────────┘
             │
      ┌──────┴──────┐
      │             │
   success       failure
      │             │
      ▼             ▼
┌───────────┐ ┌──────────────────┐
│ Persist   │ │ Handle Error     │
│ Result    │ │ - Persist error  │
│ Update    │ │ - Log traceback  │
│ status =  │ │ - Increment      │
│ completed │ │   retry count    │
│           │ │ - Requeue or     │
│           │ │   mark FAILED    │
└─────┬─────┘ └────────┬─────────┘
      │                │
      └───────┬────────┘
              ▼
┌──────────────────────────┐
│ Update Pipeline Progress │
│ - Increment counters     │
│ - Recalculate progress % │
│ - Check if pipeline done │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ Dispatch Next Task       │
│ (if dependency-ordered   │
│  successor is ready)     │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ Update Heartbeat         │
│ status = 'idle'          │
│ current_task_id = NULL   │
└────────────┬─────────────┘
             ▼
         (back to fetch)
```

---

## Heartbeat System

### Purpose
Detect crashed/hung workers and requeue their orphaned tasks.

### Mechanism
```python
# Every 30 seconds:
UPDATE worker_heartbeats
SET last_heartbeat = now()
WHERE worker_id = '{worker_id}';
```

### Orphan Detection (CleanupWorker)
```python
# Every 60 seconds:
# 1. Find workers with stale heartbeats
stale_workers = SELECT * FROM worker_heartbeats
                WHERE last_heartbeat < now() - INTERVAL '120 seconds'
                AND status != 'stopped';

# 2. Find tasks assigned to stale workers
orphaned_tasks = SELECT * FROM chunk_tasks
                 WHERE worker_id IN (stale_worker_ids)
                 AND status = 'processing';

# 3. Requeue orphaned tasks
UPDATE chunk_tasks
SET status = 'queued', worker_id = NULL
WHERE id IN (orphaned_task_ids);

# 4. Remove stale worker records
DELETE FROM worker_heartbeats
WHERE worker_id IN (stale_worker_ids);
```

---

## Graceful Shutdown

```
SIGTERM / SIGINT received
         │
         ▼
┌──────────────────────────┐
│ Set shutdown_flag = true │
│ Stop accepting new tasks │
└────────────┬─────────────┘
         │
         ├── Currently processing a task?
         │        │
         │     ┌──┴──┐
         │    YES    NO
         │     │      │
         │     ▼      ▼
         │  ┌─────────────────┐  ┌─────────────────┐
         │  │ Wait for task   │  │ Proceed to       │
         │  │ to complete     │  │ cleanup          │
         │  │ (timeout: 60s)  │  │                  │
         │  └────────┬────────┘  └────────┬─────────┘
         │           │                    │
         │      ┌────┴────┐               │
         │   completed  timeout            │
         │      │         │               │
         │      │    ┌────▼─────────┐     │
         │      │    │ Save progress│     │
         │      │    │ Requeue task │     │
         │      │    └──────┬───────┘     │
         │      │           │             │
         └──────┴───────────┴─────────────┘
                            │
                            ▼
               ┌──────────────────────────┐
               │ Update heartbeat:        │
               │ status = 'stopped'       │
               │ Close DB connection      │
               │ Close Redis connection   │
               │ Exit process cleanly     │
               └──────────────────────────┘
```

---

## Failure Recovery Matrix

| Failure Type | Detection | Recovery Action | SLA |
|---|---|---|---|
| Worker crash (OOM, segfault) | Heartbeat timeout (120s) | Requeue orphaned tasks | < 3 min |
| Redis connection lost | Connection error in BLPOP | Retry with backoff, exit if persistent | < 30s |
| PostgreSQL connection lost | Query error | Retry with backoff, exit if persistent | < 30s |
| Task timeout (hung processing) | Heartbeat shows 'busy' > 10 min | Kill worker, requeue task | < 12 min |
| Application restart (reboot) | Workers not running | Service manager restarts workers | < 60s |

---

## Concurrency & Scaling

### Desktop (Tier 1)
- **Fixed worker pool**: 4-8 workers total (configurable)
- **Queue assignment**: 2 parsing, 4 conversion, 2 validation
- **No auto-scaling** — manual configuration

### Server (Tier 2)
- **Docker replicas**: scale via `docker compose scale workers=8`
- **Queue priority**: conversion queue gets 2x workers vs others

### Cloud (Tier 3 — Future)
- **Auto-scaling rules**:
  - Scale up: queue depth > 50 for > 2 minutes
  - Scale down: queue depth = 0 for > 5 minutes
  - Min: 2 workers, Max: 20 workers

---

## Worker Configuration

```python
WORKER_CONFIG = {
    "heartbeat_interval_seconds": 30,
    "orphan_timeout_seconds": 120,
    "task_timeout_seconds": 600,      # 10 minutes max per task
    "graceful_shutdown_timeout": 60,   # 60 seconds to finish current task
    "queue_poll_timeout": 5,           # BLPOP timeout
    "max_consecutive_failures": 5,     # Worker exits after 5 consecutive failures
    "retry_backoff_base": 1,           # Exponential backoff: 1s, 2s, 4s
    "retry_backoff_max": 30,           # Max backoff: 30 seconds
}
```
