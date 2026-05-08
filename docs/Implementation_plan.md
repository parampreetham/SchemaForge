# Implementation Plan

---

## Phase 0 — Project Bootstrap (Week 1)

### Objective
Set up development environment, CI/CD, and project scaffolding.

### Tasks
- [ ] Initialize monorepo structure (`backend/`, `frontend/`, `docs/`)
- [ ] Setup Python virtual environment + pyproject.toml
- [ ] Setup Node.js project (Next.js + TypeScript)
- [ ] Configure linting: Ruff (Python), ESLint + Prettier (TypeScript)
- [ ] Configure pre-commit hooks
- [ ] Setup Git branching strategy (main → develop → feature/*)
- [ ] Create docker-compose.yml for PostgreSQL + Redis
- [ ] Create `.env.example` with all required variables
- [ ] Setup basic CI pipeline (lint + test on PR)

### Definition of Done
- `docker compose up` starts PostgreSQL + Redis
- Backend starts with `uvicorn` and returns health check
- Frontend starts with `npm run dev`
- All linters pass on empty project

### Dependencies: None
### Estimated Duration: 3-5 days

---

## Phase 1 — Foundation Infrastructure (Weeks 2-4)

### Objective
Build resilient long-running job infrastructure with persistent state.

### Tasks

#### Backend Core
- [ ] Initialize FastAPI application with structured layout
- [ ] Configure PostgreSQL connection (SQLAlchemy 2.x async)
- [ ] Configure Redis connection pool
- [ ] Setup Alembic for migrations
- [ ] Implement health check endpoints (`/health`, `/health/ready`)
- [ ] Configure structlog with JSON output
- [ ] Setup CORS middleware

#### Authentication
- [ ] Implement user model + registration endpoint
- [ ] Implement JWT login/logout
- [ ] Implement role-based middleware (Admin, Operator, Viewer)
- [ ] Password hashing with bcrypt

#### Queue Infrastructure
- [ ] Setup RQ worker configuration
- [ ] Define queue topology: `parsing`, `conversion`, `validation`, `retry`
- [ ] Implement worker heartbeat system
- [ ] Implement dead letter queue for poison messages
- [ ] Configure retry policies per queue
- [ ] Implement graceful shutdown handling

#### Database Schema
- [ ] Create `users` table + migration
- [ ] Create `projects` table + migration
- [ ] Create `pipeline_jobs` table + migration
- [ ] Create `chunk_tasks` table + migration
- [ ] Create `artifacts` table + migration
- [ ] Create `logs` table + migration
- [ ] Create `worker_heartbeats` table + migration
- [ ] Add indexes for common query patterns

#### Windows Runtime
- [ ] Research NSSM for service management
- [ ] Create service wrapper scripts
- [ ] Test auto-restart behavior

### Risks
- SQLAlchemy async configuration complexity
- Redis connection stability on Windows

### Definition of Done
- Workers register heartbeats in database
- Job can be created, queued, and processed by worker
- Worker survives restart and picks up pending tasks
- All tables created via Alembic migrations

### Dependencies: Phase 0
### Estimated Duration: 2-3 weeks

---

## Phase 2 — Schema Parsing Engine (Weeks 5-6)

### Objective
Build deterministic SQL parsing and intelligent chunking.

### Tasks
- [ ] Integrate sqlglot library
- [ ] Build DDL chunker (split schema file into individual objects)
- [ ] Build AST generator per chunk
- [ ] Build object classifier (TABLE, VIEW, PROCEDURE, TRIGGER, FUNCTION, SEQUENCE, INDEX)
- [ ] Build dependency graph engine (FK references, procedure calls)
- [ ] Implement topological sort for dependency ordering
- [ ] Handle circular dependency detection
- [ ] Build chunk metadata extractor (object name, type, size, complexity)
- [ ] Write parsing workers that consume from `parsing` queue
- [ ] Integration tests with real DB2 DDL samples

### Risks
- sqlglot may not support all DB2 dialects
- Malformed SQL may break parser

### Definition of Done
- 500MB DB2 schema file splits into individual objects
- Dependency graph correctly orders objects
- Circular dependencies detected and reported
- Each chunk has metadata (name, type, dependencies)

### Dependencies: Phase 1
### Estimated Duration: 2 weeks

---

## Phase 3 — Deterministic Conversion Engine (Weeks 7-8)

### Objective
Handle all rule-based DB2 → Azure SQL mappings without AI.

### Tasks
- [ ] Implement datatype mapping rules (DB2 → T-SQL)
- [ ] Implement constraint conversion (CHECK, UNIQUE, FK, PK)
- [ ] Implement identity column conversion (GENERATED ALWAYS → IDENTITY)
- [ ] Implement sequence conversion
- [ ] Implement DB2 syntax stripping (DB2-specific clauses)
- [ ] Implement built-in function mapping (DB2 → T-SQL equivalents)
- [ ] Implement schema/qualifier handling
- [ ] Build conversion rule registry (extensible rule system)
- [ ] Write conversion workers for `conversion` queue
- [ ] Golden test suite: known DB2 inputs → expected T-SQL outputs

### Risks
- Edge cases in DB2 syntax variants
- Missing mapping rules for uncommon types

### Definition of Done
- All standard DB2 datatypes map correctly
- Constraints, identities, sequences convert correctly
- Golden test suite passes (≥ 50 test cases)
- Conversion workers process chunks from queue

### Dependencies: Phase 2
### Estimated Duration: 2 weeks

---

## Phase 4 — AI Translation Engine (Weeks 9-11)

### Objective
Handle semantic procedural conversion using AI with structured prompts.

### Tasks
- [ ] Build AI provider abstraction layer (OpenAI + Anthropic)
- [ ] Design prompt template system with versioning
- [ ] Implement procedure translation prompt
- [ ] Implement trigger translation prompt
- [ ] Implement cursor rewriting prompt
- [ ] Implement error correction prompt (validation feedback → fix)
- [ ] Implement confidence scoring heuristic
- [ ] Implement token budget management
- [ ] Implement AI response parser (extract SQL from response)
- [ ] Store all prompts + responses in database
- [ ] Build AI conversion workers
- [ ] Cost tracking per pipeline

### Risks
- AI hallucination producing invalid syntax
- Token cost explosion on large procedures
- Model API rate limiting

### Definition of Done
- Stored procedures translate with ≥ 70% first-pass accuracy
- All AI interactions logged with prompt version
- Token usage tracked per pipeline
- Retry prompts include validation error context

### Dependencies: Phase 3
### Estimated Duration: 3 weeks

---

## Phase 5 — Validation Engine (Weeks 12-13)

### Objective
Automatically validate generated SQL against Azure SQL.

### Tasks
- [ ] Build SQL Server / Azure SQL connection manager
- [ ] Implement syntax validation (parse without execute)
- [ ] Implement execution validation (deploy to test schema)
- [ ] Build structured error parser (extract line, error code, message)
- [ ] Implement retry loop (validation error → AI correction → re-validate)
- [ ] Implement retry budget enforcement (max 3 per chunk)
- [ ] Implement manual review queue for exhausted retries
- [ ] Build validation workers for `validation` queue
- [ ] Store validation results with full error details

### Risks
- Azure SQL connection management complexity
- Validation environment cleanup between runs

### Definition of Done
- Generated SQL validated against real Azure SQL instance
- Errors parsed and fed back to AI for retry
- Chunks exceeding retry budget flagged for manual review
- Validation results persisted per attempt

### Dependencies: Phase 4
### Estimated Duration: 2 weeks

---

## Phase 6 — Frontend Dashboard (Weeks 14-17)

### Objective
Build enterprise dashboard for pipeline management and monitoring.

### Tasks
- [ ] Setup Next.js project with TypeScript
- [ ] Implement authentication pages (login, register)
- [ ] Build dashboard page (active jobs, queue health, worker status)
- [ ] Build pipeline list page with status indicators
- [ ] Build pipeline detail page (chunk progress, stage progress)
- [ ] Build real-time log viewer with filtering
- [ ] Build artifact viewer with diff comparison
- [ ] Build worker health page
- [ ] Build settings page (AI provider config, validation target)
- [ ] Implement Zustand stores (auth, pipelines, logs)
- [ ] Implement API client layer
- [ ] Responsive layout with sidebar navigation
- [ ] Loading states, error boundaries, empty states

### Risks
- Real-time updates may require WebSocket or polling
- Large log volumes may impact browser performance

### Definition of Done
- User can create project, upload schema, run pipeline from UI
- Pipeline progress visible in real-time
- Logs searchable and filterable
- Artifact diff view works for converted SQL

### Dependencies: Phases 1-5 (API endpoints)
### Estimated Duration: 3-4 weeks

---

## Phase 7 — Packaging & Desktop Deployment (Weeks 18-19)

### Objective
Package SchemaForge as a Windows desktop application.

### Tasks
- [ ] Integrate Tauri shell
- [ ] Configure Tauri to launch FastAPI backend as sidecar
- [ ] Configure service bootstrap (PostgreSQL, Redis, Workers)
- [ ] Build Windows installer (MSI/NSIS)
- [ ] Implement auto-update mechanism
- [ ] Create runtime configuration wizard (first-run setup)
- [ ] Write installation documentation
- [ ] End-to-end testing on clean Windows machine

### Risks
- Packaging Python + Redis + PostgreSQL is complex
- Windows service permissions

### Definition of Done
- Single installer sets up entire stack on Windows
- App launches and shows dashboard
- Pipeline runs successfully on fresh install
- App survives system reboot

### Dependencies: Phase 6
### Estimated Duration: 2 weeks

---

## Timeline Summary

| Phase | Duration | Cumulative |
|---|---|---|
| Phase 0: Bootstrap | 1 week | Week 1 |
| Phase 1: Infrastructure | 3 weeks | Week 4 |
| Phase 2: Parsing | 2 weeks | Week 6 |
| Phase 3: Deterministic | 2 weeks | Week 8 |
| Phase 4: AI Engine | 3 weeks | Week 11 |
| Phase 5: Validation | 2 weeks | Week 13 |
| Phase 6: Frontend | 4 weeks | Week 17 |
| Phase 7: Packaging | 2 weeks | Week 19 |
| **Total** | **~19 weeks** | |
