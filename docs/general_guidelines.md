# General Engineering Guidelines

---

## Core Principles

| Principle | Explanation |
|---|---|
| **Reliability over speed** | A correct migration matters infinitely more than a fast one |
| **Deterministic before AI** | Handle known patterns with rules; reserve AI for ambiguity |
| **Every task is resumable** | Crash at any point and pick up where you left off |
| **Never trust AI blindly** | All generated SQL must pass validation |
| **Persist everything important** | Job state, prompts, responses, results — all in the database |
| **Chunk everything** | Never process a giant schema as a monolith |

---

## Architecture Guidelines

### Separation of Concerns
- **Backend is headless** — no UI logic, no HTML rendering, pure API
- **UI is replaceable** — frontend could be swapped for CLI or web without backend changes
- **Workers are stateless** — all state lives in PostgreSQL, workers are disposable
- **Queue-driven only** — no synchronous long-running API requests; everything through Redis queues

### Layered Architecture
```
Routes → Services → Repositories → Models
                ↓
           Workers (consume from queue, use Services)
```

- **Routes**: HTTP layer only — parse request, call service, return response
- **Services**: All business logic — orchestration, validation, rules
- **Repositories**: Data access only — queries, transactions, no logic
- **Models**: Database schema definitions
- **Workers**: Queue consumers — fetch task, call service, update state

### No Shortcuts
- No direct database queries from route handlers
- No business logic in workers (delegate to services)
- No service-to-service circular dependencies
- No shared mutable state between workers

---

## AI Guidelines

### When to Use AI
- **YES**: Stored procedure translation, trigger rewriting, cursor conversion, complex procedural logic
- **NO**: Datatype mapping, constraint conversion, identity columns, syntax normalization

### AI Safety Rules
1. AI should handle ambiguity only — deterministic rules first
2. **Always validate** generated SQL against Azure SQL
3. **Store everything** — every prompt and response persisted in `ai_interactions` table
4. **Retry with feedback** — validation errors fed back into correction prompts
5. **Separate prompts by object type** — procedure prompt ≠ trigger prompt
6. **Version all prompts** — prompt changes tracked in code
7. **Budget tokens** — max token limit per chunk, alert on overspend
8. **Never deploy directly** — AI output goes through validation, never to production

### Prompt Design Rules
- Provide explicit conversion rules in system prompt
- Include DB2-specific context (dialect, version)
- Show example input/output pairs
- Request structured output (SQL only, no explanations in output)
- Keep prompts deterministic — same input should produce similar output

---

## Logging Guidelines

### Standards
- **Always use structlog** — never `print()`, never `logging.info()` without structlog
- **JSON format only** — all logs are structured JSON
- **Correlation IDs** — every request/task gets a correlation ID, propagated through all logs
- **Persist in database** — critical logs stored in `logs` table, not just files

### Required Log Fields
```json
{
  "timestamp": "2026-01-15T10:30:00Z",
  "level": "info",
  "correlation_id": "abc-123",
  "job_id": 101,
  "task_id": 88,
  "stage": "validation",
  "worker_id": "worker-1",
  "message": "Chunk validation completed",
  "duration_ms": 450
}
```

### Log Levels
| Level | Usage |
|---|---|
| `debug` | Detailed diagnostic info (not in production) |
| `info` | Normal operation events (task started, completed) |
| `warning` | Recoverable issues (retry triggered, slow response) |
| `error` | Failed operations requiring attention |
| `critical` | System-level failures (worker crash, DB connection lost) |

---

## Security Guidelines

### Credential Management
- **Never hardcode secrets** — all secrets via environment variables
- **Encrypt at rest** — database credentials, API keys encrypted with AES-256
- **Rotate regularly** — JWT secrets, API keys on quarterly schedule
- **`.env` never committed** — only `.env.example` in repository

### Access Control
- **RBAC enforced on all endpoints** — Admin, Operator, Viewer roles
- **Project isolation** — users only see their own projects
- **Audit sensitive actions** — login, pipeline start/cancel, settings changes logged

### API Security
- **JWT tokens** — short-lived (24h), refresh via re-login
- **Rate limiting** — 100 req/min per user on API endpoints
- **Input validation** — Pydantic schemas validate all input
- **CORS restricted** — only allowed origins

---

## Performance Guidelines

### Processing
- Process chunks independently — never batch entire schemas
- Use parallel workers carefully — respect database connection limits
- Cache repeated mappings — datatype rules cached in memory
- Avoid giant prompts — chunk procedures over 500 lines

### Database
- Use connection pooling (SQLAlchemy pool_size=10, max_overflow=20)
- Index commonly queried columns (job_id, status, created_at)
- Paginate all list endpoints (default 50, max 200)
- Use SELECT only needed columns — no SELECT *

### API
- p95 response time < 200ms for non-pipeline endpoints
- Streaming responses for large log queries
- Gzip compression for artifact downloads

---

## Error Handling Guidelines

### Categories
| Category | Strategy | Example |
|---|---|---|
| Transient | Auto-retry with backoff | Network timeout, Redis connection drop |
| Validation | AI correction loop | SQL syntax error from conversion |
| Permanent | Fail and flag for review | Unsupported DB2 construct |
| System | Alert and restart | Worker OOM, disk full |

### Rules
- Never swallow exceptions silently
- Always log the full exception traceback
- Include context in error messages (job_id, task_id, object_name)
- Distinguish between user errors (4xx) and system errors (5xx)
- All API errors return structured JSON: `{"error": "...", "detail": "...", "correlation_id": "..."}`

---

## Git & Branching Strategy

### Branches
- `main` — stable, tested, release-ready
- `develop` — integration branch
- `feature/*` — feature development
- `fix/*` — bug fixes
- `release/*` — release preparation

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(parser): add DB2 sequence detection
fix(worker): handle Redis connection timeout
docs(api): update pipeline endpoint schemas
refactor(converter): extract rule registry
test(validation): add SQL Server syntax tests
```

### Pull Request Rules
- All PRs require at least 1 review
- All tests must pass
- Linting must pass (Ruff + ESLint)
- No direct commits to `main` or `develop`
