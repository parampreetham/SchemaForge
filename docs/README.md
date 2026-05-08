# SchemaForge

> Enterprise-grade AI-assisted database schema migration and transformation platform for large-scale DB2 to Azure SQL migrations.

---

## Overview

SchemaForge is a desktop-first migration platform that combines deterministic SQL transformation with AI-assisted conversion to reliably migrate massive DB2 schemas to Azure SQL. Unlike one-shot conversion tools (e.g., SSMA), SchemaForge treats every database object as an independently resumable task — enabling long-running, crash-resilient, auditable migration pipelines.

### Why SchemaForge?

| Problem with Existing Tools | SchemaForge Solution |
|---|---|
| Choke on massive schemas | Intelligent chunking — every DB object is an independent task |
| No resume after failure | Persistent checkpoints — survive reboots mid-pipeline |
| Black-box AI conversion | Deterministic-first approach — AI only handles ambiguity |
| No audit trail | Full provenance — every transformation is logged and traceable |
| Manual retry loops | Automated validation → error feedback → AI retry loops |
| Single-user blocking | Multi-user concurrent pipeline orchestration |

---

## Core Features

### Pipeline Engine
- Long-running resumable migration pipelines
- Pause / Resume / Cancel at any point
- Per-chunk progress tracking with persistent state
- Crash recovery via database-backed checkpoints

### Schema Processing
- DB2 schema extraction and intelligent chunking
- AST-aware SQL parsing via `sqlglot`
- Automatic dependency graph construction
- Object classification (tables, views, procedures, triggers, functions, sequences)

### Conversion Engine
- **Deterministic layer**: Datatype mapping, constraint conversion, identity/sequence handling, syntax normalization
- **AI-assisted layer**: Stored procedure translation, trigger rewriting, complex cursor logic, procedural semantics conversion

### Validation & Retry
- Automated SQL execution validation against Azure SQL / SQL Server
- Structured error parsing and feedback
- AI-driven correction loops with validation-informed retry prompts
- Configurable retry budgets per object type

### Enterprise Features
- Multi-user job orchestration with role-based access
- Structured JSON logging with correlation IDs
- Full audit trail for every transformation
- Artifact versioning (original → converted → validated)

### Desktop Runtime
- Native Windows desktop app via Tauri
- Local FastAPI backend + Redis + PostgreSQL
- Background worker pool independent of UI lifecycle

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Tauri Desktop Shell                │
│  ┌───────────────────────────────────────────────┐  │
│  │           Next.js + React Frontend            │  │
│  │  (Dashboard, Pipeline Viewer, Artifact Diff)  │  │
│  └──────────────────────┬────────────────────────┘  │
│                         │ HTTP/REST                  │
│  ┌──────────────────────▼────────────────────────┐  │
│  │              FastAPI Backend                   │  │
│  │  (Auth, Pipeline API, Artifact API, Logs API) │  │
│  └───────┬──────────────┬──────────────┬─────────┘  │
│          │              │              │             │
│  ┌───────▼──────┐ ┌─────▼──────┐ ┌────▼──────────┐ │
│  │  PostgreSQL  │ │   Redis    │ │ File Storage  │ │
│  │  (Job State, │ │  (Queue,   │ │ (Artifacts,   │ │
│  │   Metadata)  │ │  Pub/Sub)  │ │  Originals)   │ │
│  └──────────────┘ └─────┬──────┘ └───────────────┘ │
│                         │                           │
│  ┌──────────────────────▼────────────────────────┐  │
│  │             Worker Pool (Python)              │  │
│  │  ┌────────┐ ┌──────────┐ ┌─────────────────┐ │  │
│  │  │ Parser │ │Converter │ │   Validator      │ │  │
│  │  │Workers │ │ Workers  │ │   Workers        │ │  │
│  │  └────────┘ └──────────┘ └─────────────────┘ │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Desktop Shell | Tauri | 2.x |
| Frontend | Next.js + React | 15.x / 19.x |
| Styling | Tailwind CSS + shadcn/ui | 4.x |
| State | Zustand | 5.x |
| Backend | FastAPI | 0.115+ |
| Queue | Redis + RQ | 7.x / 1.16+ |
| Database | PostgreSQL | 16+ |
| ORM | SQLAlchemy | 2.x |
| Migrations | Alembic | 1.13+ |
| SQL Parser | sqlglot | 25+ |
| AI | OpenAI / Anthropic SDK | Latest |
| Auth | JWT (PyJWT) | — |
| Logging | structlog | 24+ |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+ (LTS)
- PostgreSQL 16+
- Redis 7+
- Rust toolchain (for Tauri)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/schemaforge.git
cd schemaforge

# Backend setup
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements/dev.txt
alembic upgrade head

# Frontend setup
cd ../frontend
npm install

# Start services (development)
# Terminal 1: Redis
redis-server

# Terminal 2: Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 3: Workers
cd backend && rq worker parsing conversion validation --with-scheduler

# Terminal 4: Frontend
cd frontend && npm run dev

# Terminal 5: Tauri (optional — desktop shell)
cd frontend && npm run tauri dev
```

---

## Documentation

| Document | Description |
|---|---|
| [PRD](./PRD.md) | Product requirements, personas, success metrics |
| [Implementation Plan](./Implementation_plan.md) | Phased build plan with estimates |
| [Tech Stack](./tech_stack.md) | Technology choices and justifications |
| [Backend Structure](./Backend_structure.md) | API, services, workers, repository pattern |
| [Frontend Structure](./frontend_structure.md) | Pages, components, state management |
| [App Flow](./app_flow.md) | User flows, processing pipeline, state machines |
| [General Guidelines](./general_guidelines.md) | Architecture, AI, security, performance principles |
| [Frontend Guidelines](./frontend_guidelines.md) | Design system, color palette, typography, UX |
| [AI Agents](./agents_use.md) | Agent types, workflows, prompt strategy, cost management |
| [Deployment Architecture](./deployment_architecture.md) | Windows desktop, future Linux/cloud |
| [Database Schema](./database_schema.md) | Full schema with types, constraints, indexes |
| [Worker Lifecycle](./worker_lifecycle.md) | Boot, execution, recovery, scaling |
| [Observability](./observability.md) | Logging, metrics, alerting, health checks |
| [Roadmap](./roadmap.md) | Versioned feature roadmap with timelines |
| [Risks & Considerations](./risks_and_considerations.md) | Risk matrix, mitigations, compliance |
| [Coding Standards](./coding_standards.md) | Python, TypeScript, testing, commit conventions |
| [API Design](./api_design.md) | REST API spec, schemas, errors, pagination |
| [Storage Structure](./storage_structure.md) | Artifact storage, retention, cleanup |
| [MVP Scope](./mvp_scope.md) | MVP feature set, acceptance criteria, timeline |

---

## Core Principles

1. **Reliability over speed** — A correct migration is infinitely more valuable than a fast one
2. **Deterministic before AI** — Handle known patterns with rules; reserve AI for ambiguity
3. **Every task is resumable** — Crash at any point and pick up where you left off
4. **Never trust AI blindly** — All generated SQL must pass validation before acceptance
5. **Persist everything** — Job state, prompts, responses, validation results — all in the database
6. **Chunk everything** — Never process a giant schema as a monolith

---

## Project Status

🟡 **Pre-development** — Documentation and architecture phase

---

## License

Proprietary — All rights reserved.
