# Application Flow

---

## User Flow

```
┌──────────────────┐
│  Launch Desktop   │
│  Application      │
└────────┬─────────┘
         ▼
┌──────────────────┐     ┌──────────────────┐
│  Login / Register │────▶│  Dashboard        │
└──────────────────┘     │  (Active Jobs,    │
                         │   Queue Health)   │
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │  Create Project   │
                         │  (Name, Source,   │
                         │   Target DB)      │
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │  Upload DB2       │
                         │  Schema (.sql)    │
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │  Create Pipeline  │
                         │  (Configure opts) │
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │  Start Pipeline   │─────────────────┐
                         └────────┬─────────┘                 │
                                  ▼                           ▼
                         ┌──────────────────┐      ┌──────────────────┐
                         │  Monitor Progress │      │  Pause / Cancel  │
                         │  (Live Dashboard) │      │  (If needed)     │
                         └────────┬─────────┘      └──────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │  Review Results   │
                         │  - Artifacts      │
                         │  - Diff View      │
                         │  - Failed Chunks  │
                         └────────┬─────────┘
                                  ▼
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
          ┌──────────────────┐       ┌──────────────────┐
          │  Retry Failed     │       │  Download Output  │
          │  Chunks           │       │  (ZIP of T-SQL)   │
          └──────────────────┘       └──────────────────┘
```

---

## Processing Pipeline (Backend)

```
┌─────────────┐   ┌──────────────┐   ┌─────────────────┐
│   UPLOAD    │──▶│   CHUNKING   │──▶│   PARSING       │
│             │   │              │   │   (AST + Deps)  │
│ Accept .sql │   │ Split into   │   │   sqlglot       │
│ Store orig  │   │ objects      │   │   analysis      │
└─────────────┘   └──────────────┘   └────────┬────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │  DEPENDENCY     │
                                    │  ORDERING       │
                                    │  (Topological   │
                                    │   sort)         │
                                    └────────┬────────┘
                                              │
            ┌─────────────────────────────────┤
            ▼                                 ▼
  ┌─────────────────┐              ┌─────────────────┐
  │  DETERMINISTIC  │              │  AI CONVERSION  │
  │  CONVERSION     │              │                 │
  │                 │              │  Procedures,    │
  │  Tables, Views, │              │  Triggers,      │
  │  Sequences,     │              │  Complex Logic  │
  │  Constraints    │              │                 │
  └────────┬────────┘              └────────┬────────┘
           │                                │
           └────────────────┬───────────────┘
                            ▼
                  ┌─────────────────┐
                  │   VALIDATION    │
                  │                 │
                  │  Execute against│
                  │  Azure SQL      │
                  └────────┬────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌─────────────────┐      ┌─────────────────┐
    │   PASS ✅       │      │   FAIL ❌        │
    │   Store artifact│      │   Parse error    │
    │   Mark complete │      │   Feed to AI     │
    └─────────────────┘      │   Retry (≤ 3x)  │
                             └────────┬────────┘
                                      │
                            ┌─────────┴─────────┐
                            ▼                   ▼
                  ┌──────────────┐    ┌──────────────┐
                  │ Retry Pass ✅│    │ Manual Review │
                  │              │    │ Queue 🔍     │
                  └──────────────┘    └──────────────┘
```

---

## Pipeline Job State Machine

```
                    ┌──────────┐
                    │ CREATED  │
                    └────┬─────┘
                         │ user clicks "Start"
                         ▼
                    ┌──────────┐
             ┌─────│ QUEUED   │
             │     └────┬─────┘
             │          │ worker picks up
             │          ▼
             │     ┌──────────┐
             │  ┌──│ RUNNING  │──┐
             │  │  └────┬─────┘  │
             │  │       │        │ user cancels
             │  │       │        ▼
             │  │       │   ┌───────────┐
             │  │       │   │CANCELLING │
             │  │       │   └─────┬─────┘
             │  │       │         │ in-flight chunks complete
             │  │       │         ▼
             │  │       │   ┌───────────┐
             │  │       │   │ CANCELLED │
             │  │       │   └───────────┘
             │  │       │
             │  │  user pauses
             │  │       │
             │  │       ▼
             │  │  ┌──────────┐
             │  │  │  PAUSED  │
             │  │  └────┬─────┘
             │  │       │ user resumes
             │  │       │
             │  │       ▼
             │  │  (back to RUNNING)
             │  │
             │  │ crash / error
             │  │
             │  ▼
             │  ┌──────────┐
             │  │  FAILED  │
             │  └────┬─────┘
             │       │ user retries
             │       ▼
             │  ┌──────────┐
             │  │ RETRYING │──→ (back to RUNNING)
             │  └──────────┘
             │
             │ all chunks complete
             │
             ▼
        ┌───────────┐
        │ COMPLETED │
        └───────────┘
```

### Valid State Transitions

| From | To | Trigger |
|---|---|---|
| CREATED | QUEUED | User starts pipeline |
| QUEUED | RUNNING | Worker picks up first chunk |
| RUNNING | PAUSED | User pauses |
| RUNNING | CANCELLING | User cancels |
| RUNNING | FAILED | Unrecoverable error |
| RUNNING | COMPLETED | All chunks processed |
| PAUSED | RUNNING | User resumes |
| CANCELLING | CANCELLED | In-flight chunks finish |
| FAILED | RETRYING | User retries |
| RETRYING | RUNNING | Worker restarts processing |

---

## Chunk Task State Machine

```
PENDING → QUEUED → PROCESSING → VALIDATING → COMPLETED
                       │              │
                       ▼              ▼
                    FAILED ←── RETRY_PENDING
                       │
                       ▼
                MANUAL_REVIEW
```

| From | To | Trigger |
|---|---|---|
| PENDING | QUEUED | Pipeline started, chunk dispatched |
| QUEUED | PROCESSING | Worker picks up chunk |
| PROCESSING | VALIDATING | Conversion complete, sent to validation |
| VALIDATING | COMPLETED | Validation passed |
| VALIDATING | RETRY_PENDING | Validation failed, retries remaining |
| RETRY_PENDING | PROCESSING | Retry dispatched |
| PROCESSING | FAILED | Conversion error |
| VALIDATING | FAILED | Retries exhausted |
| FAILED | MANUAL_REVIEW | Flagged for human review |

---

## Error Handling Flow

```
Error Occurs
     │
     ├── Transient Error (network, timeout)
     │         │
     │         ▼
     │    Auto-retry with exponential backoff
     │    (max 3 attempts, 1s → 2s → 4s)
     │
     ├── Validation Error (SQL syntax)
     │         │
     │         ▼
     │    Parse error → Feed to AI → Retry conversion
     │    (max 3 AI retries per chunk)
     │
     ├── Permanent Error (unsupported construct)
     │         │
     │         ▼
     │    Mark chunk FAILED → Add to manual review queue
     │
     └── System Error (worker crash, OOM)
              │
              ▼
         Worker heartbeat timeout detected
         → Requeue orphaned tasks
         → Restart worker
```
