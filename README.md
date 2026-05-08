# SchemaForge

> Enterprise-grade AI-assisted database schema migration and transformation platform for large-scale DB2 to Azure SQL migrations.

![Project Status](https://img.shields.io/badge/Status-Active_Development_(MVP_Complete)-green)

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

## How to Run & Work With This Project

SchemaForge consists of a **FastAPI backend** (with PostgreSQL and Redis) and a **Next.js frontend**. The system heavily relies on asynchronous background workers (`rq`) to process chunks, parse schemas, query AI APIs, and validate output.

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- **PostgreSQL 16+** (Make sure it is running on port 5432)
- **Redis 7+** (Make sure it is running on port 6379)
- (Optional) **Rust toolchain** if you want to build the Tauri desktop app.

### 2. Backend Setup
The backend manages the database, the API endpoints, and the migration workers.

1. **Clone the repo** and open the `backend` folder:
   ```bash
   cd SchemaForge/backend
   ```
2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   # source .venv/bin/activate # Linux/Mac
   pip install -r requirements/dev.txt
   ```
3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` in the `backend` directory.
   ```bash
   cp .env.example .env
   ```
   *Crucial Env Vars:*
   - `DATABASE_URL`: Setup your Postgres connection string (e.g. `postgresql+asyncpg://postgres:password@localhost/schemaforge`).
   - `REDIS_URL`: Defaults to `redis://localhost:6379/0`.
   - `OPENAI_API_KEY`: Required if using OpenAI as your LLM translation provider.
   - `VALIDATION_DB_CONNECTION`: Connection string for the target Azure SQL/SQL Server validation database.
   
4. **Run Database Migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start the FastAPI Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *The API will be available at `http://localhost:8000`. You can view the Swagger docs at `http://localhost:8000/docs`.*

6. **Start the Background Workers**:
   Open a *new* terminal, activate the virtual environment, and run the worker pool. This processes the `parsing`, `conversion`, and `validation` queues.
   ```bash
   cd SchemaForge/backend
   .venv\Scripts\activate
   rq worker parsing conversion validation --with-scheduler
   ```

### 3. Frontend Setup
The frontend is a stunning Next.js 16 app leveraging Tailwind CSS v4 and Zustand for real-time state management.

1. **Navigate to the frontend folder**:
   ```bash
   cd SchemaForge/frontend
   ```
2. **Install Node dependencies**:
   ```bash
   npm install --legacy-peer-deps
   ```
3. **Configure Environment Variables**:
   Create a `.env.local` file in the `frontend` folder with:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```
4. **Start the Next.js Dev Server**:
   ```bash
   npm run dev
   ```
   *The dashboard will be available at `http://localhost:3000`.*

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

| Layer | Technology |
|---|---|
| Frontend | Next.js (React 19), Tailwind CSS v4, Zustand |
| Backend | FastAPI (Python 3.11+), Pydantic |
| Queue / PubSub | Redis + RQ |
| Database | PostgreSQL + SQLAlchemy + Alembic |
| SQL Parser | sqlglot |
| AI Integration | litellm (Supports OpenAI, Anthropic, etc) |
| SQL Validation | pyodbc (Connects directly to Azure SQL) |

For more deep-dives into our architecture and documentation, please check out the `docs/` folder.

## Key Documentation Links

- [App Flow](./docs/app_flow.md)
- [Backend Structure](./docs/Backend_structure.md)
- [Database Schema](./docs/database_schema.md)
- [Tech Stack Justifications](./docs/tech_stack.md)

---

## License

Proprietary — All rights reserved.
