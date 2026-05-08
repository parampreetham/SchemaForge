# Backend Structure

---

## Directory Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app factory + lifespan
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # POST /auth/login, /auth/register, /auth/logout
│   │   │   ├── projects.py          # CRUD /projects
│   │   │   ├── pipelines.py         # CRUD /pipelines + pause/resume/cancel
│   │   │   ├── chunks.py            # GET /chunks, POST /chunks/{id}/retry
│   │   │   ├── artifacts.py         # GET /artifacts/{id}, /artifacts/{id}/download
│   │   │   ├── logs.py              # GET /logs with filtering
│   │   │   ├── workers.py           # GET /workers/health
│   │   │   └── health.py            # GET /health, /health/ready
│   │   │
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # JWT verification middleware
│   │   │   ├── correlation.py       # Inject correlation ID into request context
│   │   │   ├── error_handler.py     # Global exception → JSON error response
│   │   │   └── logging.py           # Request/response logging
│   │   │
│   │   └── dependencies/
│   │       ├── __init__.py
│   │       ├── auth.py              # get_current_user, require_role
│   │       ├── database.py          # get_db_session
│   │       └── pagination.py        # PaginationParams
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Pydantic Settings (env-based config)
│   │   ├── database.py              # Engine, SessionLocal, Base
│   │   ├── redis.py                 # Redis connection pool
│   │   ├── security.py              # JWT encode/decode, password hashing
│   │   └── logging.py               # structlog configuration
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                  # User model
│   │   ├── project.py               # Project model
│   │   ├── pipeline_job.py          # PipelineJob model
│   │   ├── chunk_task.py            # ChunkTask model
│   │   ├── artifact.py              # Artifact model
│   │   ├── log_entry.py             # LogEntry model
│   │   ├── ai_interaction.py        # AIInteraction model (prompt + response)
│   │   └── worker_heartbeat.py      # WorkerHeartbeat model
│   │
│   ├── schemas/                     # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py                  # LoginRequest, TokenResponse
│   │   ├── project.py               # ProjectCreate, ProjectResponse
│   │   ├── pipeline.py              # PipelineCreate, PipelineResponse, PipelineProgress
│   │   ├── chunk.py                 # ChunkResponse, ChunkRetryRequest
│   │   ├── artifact.py              # ArtifactResponse
│   │   ├── log.py                   # LogResponse, LogFilter
│   │   ├── worker.py                # WorkerHealthResponse
│   │   └── common.py                # PaginatedResponse, ErrorResponse
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py          # Registration, login, token management
│   │   ├── project_service.py       # Project CRUD
│   │   ├── pipeline_service.py      # Pipeline orchestration (create, pause, resume, cancel)
│   │   ├── chunk_service.py         # Chunk lifecycle management
│   │   │
│   │   ├── parser/
│   │   │   ├── __init__.py
│   │   │   ├── chunker.py           # Split DDL into individual objects
│   │   │   ├── ast_generator.py     # sqlglot AST generation
│   │   │   ├── dependency_graph.py  # Build and topologically sort dependencies
│   │   │   └── classifier.py        # Classify object types
│   │   │
│   │   ├── converter/
│   │   │   ├── __init__.py
│   │   │   ├── deterministic.py     # Rule-based conversion engine
│   │   │   ├── rules/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── datatypes.py     # DB2 → T-SQL type mappings
│   │   │   │   ├── constraints.py   # Constraint conversion rules
│   │   │   │   ├── identity.py      # Identity/sequence rules
│   │   │   │   ├── functions.py     # Built-in function mappings
│   │   │   │   └── syntax.py        # DB2 syntax stripping
│   │   │   └── registry.py          # Rule registration and lookup
│   │   │
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── provider.py          # Abstract AI provider interface
│   │   │   ├── openai_provider.py   # OpenAI implementation
│   │   │   ├── anthropic_provider.py # Anthropic implementation
│   │   │   ├── prompt_manager.py    # Versioned prompt templates
│   │   │   ├── response_parser.py   # Extract SQL from AI responses
│   │   │   ├── token_tracker.py     # Token usage and cost tracking
│   │   │   └── prompts/
│   │   │       ├── procedure_v1.py  # Procedure translation prompt
│   │   │       ├── trigger_v1.py    # Trigger translation prompt
│   │   │       ├── cursor_v1.py     # Cursor rewriting prompt
│   │   │       └── correction_v1.py # Error correction prompt
│   │   │
│   │   ├── validator/
│   │   │   ├── __init__.py
│   │   │   ├── sql_validator.py     # Execute SQL against Azure SQL
│   │   │   ├── syntax_checker.py    # Parse-only validation
│   │   │   ├── error_parser.py      # Structured error extraction
│   │   │   └── retry_engine.py      # Validation → AI correction loop
│   │   │
│   │   └── artifacts/
│   │       ├── __init__.py
│   │       ├── storage.py           # File-based artifact storage
│   │       └── packager.py          # ZIP packaging for download
│   │
│   ├── workers/                     # RQ worker definitions
│   │   ├── __init__.py
│   │   ├── base_worker.py           # Base worker with heartbeat + error handling
│   │   ├── parsing_worker.py        # Chunk + parse + classify
│   │   ├── conversion_worker.py     # Deterministic + AI conversion
│   │   ├── validation_worker.py     # Validate + retry loop
│   │   └── cleanup_worker.py        # Orphaned task detection, heartbeat cleanup
│   │
│   ├── repositories/               # Data access layer (repository pattern)
│   │   ├── __init__.py
│   │   ├── base.py                  # BaseRepository with common CRUD
│   │   ├── user_repo.py
│   │   ├── project_repo.py
│   │   ├── pipeline_repo.py
│   │   ├── chunk_repo.py
│   │   ├── artifact_repo.py
│   │   ├── log_repo.py
│   │   └── ai_interaction_repo.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── correlation.py           # Correlation ID generation and propagation
│       ├── datetime.py              # Timezone-aware datetime utilities
│       └── file_utils.py            # Safe file I/O helpers
│
├── migrations/                      # Alembic migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/
│   ├── conftest.py                  # Fixtures: test DB, test client, factory functions
│   ├── unit/
│   │   ├── services/
│   │   ├── workers/
│   │   └── utils/
│   ├── integration/
│   │   ├── api/
│   │   └── workers/
│   └── fixtures/
│       └── sample_ddl/             # DB2 DDL test files
│
├── scripts/
│   ├── setup_db.py                  # Initialize database
│   ├── run_workers.py               # Start worker pool
│   ├── seed_data.py                 # Development seed data
│   └── install_service.py           # Windows service installation
│
├── requirements/
│   ├── base.txt                     # Production dependencies
│   ├── dev.txt                      # Dev/test dependencies
│   └── lock.txt                     # Pinned versions
│
├── alembic.ini
├── pyproject.toml
└── Dockerfile
```

---

## Dependency Flow

```
Routes → Dependencies → Services → Repositories → Models
                ↓
            Middleware
                ↓
          Core (config, security, logging)
```

**Rules**:
- Routes never access repositories directly
- Services contain all business logic
- Repositories are the only layer that touches SQLAlchemy
- Workers use services, never routes
- Core modules have zero dependencies on other app modules

---

## Worker Architecture

| Worker | Queue | Responsibility | Concurrency |
|---|---|---|---|
| ParsingWorker | `parsing` | Chunk DDL, generate AST, build dependency graph | 2 per pipeline |
| ConversionWorker | `conversion` | Deterministic + AI conversion | 4 (configurable) |
| ValidationWorker | `validation` | Execute SQL validation, trigger retries | 2 |
| CleanupWorker | `cleanup` | Detect orphaned tasks, clean heartbeats | 1 (scheduled) |

---

## Configuration Management

All configuration via environment variables with Pydantic Settings:

```python
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Auth
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440
    
    # AI
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    AI_PROVIDER: str = "openai"
    AI_MAX_RETRIES: int = 3
    
    # Validation
    AZURE_SQL_CONNECTION_STRING: str | None = None
    
    # Workers
    WORKER_HEARTBEAT_INTERVAL: int = 30
    WORKER_ORPHAN_TIMEOUT: int = 120
    
    class Config:
        env_file = ".env"
```
