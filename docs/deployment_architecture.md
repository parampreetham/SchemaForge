# Deployment Architecture

---

## Deployment Tiers

| Tier | Platform | Timeline | Use Case |
|---|---|---|---|
| Tier 1 (MVP) | Windows Desktop (Tauri) | v1.0 | Single-team enterprise deployment |
| Tier 2 | Linux Server (Docker) | v2.0 | Multi-team, always-on server |
| Tier 3 | Cloud (Azure/AWS) | v3.0 | SaaS / managed enterprise offering |

---

## Tier 1 — Windows Desktop Deployment (MVP)

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Windows 10/11 Machine                │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │              Tauri Desktop App                │  │
│  │           (WebView2 + Rust core)              │  │
│  │                                               │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │        Next.js Frontend (SSG)           │  │  │
│  │  │        http://localhost:3000             │  │  │
│  │  └──────────────────┬──────────────────────┘  │  │
│  └─────────────────────┼────────────────────────┘  │
│                        │ HTTP                       │
│  ┌─────────────────────▼────────────────────────┐  │
│  │        FastAPI Backend (Sidecar)              │  │
│  │        http://localhost:8000                   │  │
│  │        Managed as Tauri sidecar process       │  │
│  └───────┬──────────────┬──────────────┬────────┘  │
│          │              │              │            │
│  ┌───────▼──────┐ ┌─────▼──────┐ ┌────▼─────────┐ │
│  │ PostgreSQL   │ │   Redis    │ │ File Storage │ │
│  │ Port: 5432   │ │ Port: 6379 │ │ %APPDATA%/   │ │
│  │ (Local/Docker)│ │(Local/Docker)│ │ SchemaForge/ │ │
│  └──────────────┘ └─────┬──────┘ └──────────────┘ │
│                         │                          │
│  ┌──────────────────────▼───────────────────────┐  │
│  │         Worker Pool (Python processes)       │  │
│  │         Managed via NSSM or systemd-like     │  │
│  │                                              │  │
│  │  Worker 1: parsing queue                     │  │
│  │  Worker 2: conversion queue                  │  │
│  │  Worker 3: conversion queue                  │  │
│  │  Worker 4: validation queue                  │  │
│  │  Worker 5: cleanup (scheduled)               │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Port Allocation

| Service | Port | Protocol |
|---|---|---|
| Frontend (Next.js) | 3000 | HTTP |
| Backend (FastAPI) | 8000 | HTTP |
| PostgreSQL | 5432 | TCP |
| Redis | 6379 | TCP |

### Windows Service Management

**Option A: NSSM (Non-Sucking Service Manager)**
```
nssm install SchemaForge-API "C:\SchemaForge\backend\.venv\Scripts\python.exe" "-m" "uvicorn" "app.main:app" "--port" "8000"
nssm install SchemaForge-Workers "C:\SchemaForge\backend\.venv\Scripts\python.exe" "scripts\run_workers.py"
nssm install SchemaForge-Redis "C:\SchemaForge\redis\redis-server.exe"
```

**Option B: Tauri Sidecar (Preferred for MVP)**
- FastAPI launched as Tauri sidecar process
- Tauri manages lifecycle (start on app launch, stop on close)
- Workers spawned as subprocess of FastAPI

### Resource Requirements

| Resource | Minimum | Recommended |
|---|---|---|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Disk | 10 GB free | 50 GB free |
| OS | Windows 10 (64-bit) | Windows 11 |
| .NET | WebView2 Runtime | Pre-installed on Win 11 |

### Installation Flow

```
1. User runs SchemaForge-Setup.exe
2. Installer checks prerequisites (Python 3.11+, WebView2)
3. Installs PostgreSQL (embedded) or connects to existing
4. Installs Redis (Windows port or Docker)
5. Creates database and runs migrations
6. Installs desktop app and creates shortcuts
7. First-run wizard: configure AI keys, validation target
8. App launches and shows dashboard
```

---

## Tier 2 — Linux Server Deployment (v2.0)

### Architecture

```
┌───────────────────────────────────────────────────┐
│                Linux Server (Ubuntu)              │
│                                                   │
│  ┌─────────────────────────────────────────────┐  │
│  │              Docker Compose                 │  │
│  │                                             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │ Frontend │  │ Backend  │  │ Workers  │  │  │
│  │  │ (Nginx)  │  │ (FastAPI)│  │ (x4)     │  │  │
│  │  │ :80/443  │  │ :8000    │  │          │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  │  │
│  │                                             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │PostgreSQL│  │  Redis   │  │ Volumes  │  │  │
│  │  │ :5432    │  │  :6379   │  │(artifacts)│  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  │  │
│  └─────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
```

### Docker Compose

```yaml
version: "3.8"
services:
  frontend:
    build: ./frontend
    ports: ["80:80", "443:443"]
    depends_on: [backend]
    
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://sf:password@postgres:5432/schemaforge
      REDIS_URL: redis://redis:6379/0
    depends_on: [postgres, redis]
    
  workers:
    build: ./backend
    command: python scripts/run_workers.py
    environment:
      DATABASE_URL: postgresql://sf:password@postgres:5432/schemaforge
      REDIS_URL: redis://redis:6379/0
    depends_on: [postgres, redis]
    deploy:
      replicas: 4
      
  postgres:
    image: postgres:16
    volumes: [pgdata:/var/lib/postgresql/data]
    environment:
      POSTGRES_DB: schemaforge
      POSTGRES_USER: sf
      POSTGRES_PASSWORD: password
      
  redis:
    image: redis:7-alpine
    volumes: [redisdata:/data]

volumes:
  pgdata:
  redisdata:
```

---

## Tier 3 — Enterprise Cloud Deployment (v3.0)

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Azure Cloud                        │
│                                                         │
│  ┌──────────┐    ┌──────────────────┐    ┌───────────┐ │
│  │  CDN /   │    │  API Gateway     │    │ Azure     │ │
│  │ Frontend │───▶│  (Auth, Rate     │───▶│ Container │ │
│  │ (Static) │    │   Limiting)      │    │ Apps      │ │
│  └──────────┘    └──────────────────┘    └─────┬─────┘ │
│                                                │       │
│                    ┌───────────────────────────┤       │
│                    ▼                           ▼       │
│            ┌──────────────┐          ┌──────────────┐  │
│            │ Azure SQL    │          │ Azure Cache  │  │
│            │ (Managed)    │          │ for Redis    │  │
│            └──────────────┘          └──────┬───────┘  │
│                                             │          │
│            ┌────────────────────────────────▼────────┐ │
│            │      Worker Cluster (Auto-scaling)      │ │
│            │      Azure Container Instances          │ │
│            └─────────────────────────────────────────┘ │
│                                                         │
│            ┌─────────────────────────────────────────┐  │
│            │      Azure Blob Storage (Artifacts)     │  │
│            └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Backup & Recovery

### Tier 1 (Desktop)
- PostgreSQL: `pg_dump` scheduled daily via Windows Task Scheduler
- Artifacts: File copy to backup directory
- Configuration: Export to `.json` backup file

### Tier 2 (Server)
- PostgreSQL: `pg_dump` via cron + offsite copy
- Artifacts: Volume snapshots
- Redis: AOF persistence enabled

### Tier 3 (Cloud)
- Azure SQL: Automated backups (PITR 35 days)
- Blob Storage: Geo-redundant storage (GRS)
- Redis: AOF + snapshot backups

---

## Upgrade & Rollback

### Upgrade Process
1. Backup current database
2. Stop workers (graceful — wait for in-flight tasks)
3. Apply database migrations (`alembic upgrade head`)
4. Deploy new backend
5. Deploy new frontend
6. Start workers
7. Verify health checks

### Rollback Process
1. Stop workers
2. Rollback database migration (`alembic downgrade -1`)
3. Deploy previous backend version
4. Deploy previous frontend version
5. Start workers
6. Verify health checks

---

## Network Security

| Tier | Strategy |
|---|---|
| Desktop | All services on localhost — no external exposure |
| Server | Services on internal Docker network, only Nginx exposed |
| Cloud | VNet isolation, private endpoints, WAF on API Gateway |
