# Product Requirements Document (PRD)

## Product Name

**SchemaForge**

---

## Product Vision

Build a reliable, enterprise-grade, AI-assisted schema migration platform capable of converting massive DB2 schemas into Azure SQL compatible structures using deterministic parsing, intelligent AI-assisted transformation, and automated validation loops — with full auditability and crash resilience.

---

## Problem Statement

Enterprise DB2 to Azure SQL migrations face critical challenges that existing tools fail to solve:

| Problem with Existing Tools | Impact |
|---|---|
| SSMA chokes on massive schemas (10K+ objects) | Migration stalls, requires manual splitting |
| Complex DB2 procedural logic not handled | Manual rewrite of 40-60% of procedures |
| No crash recovery | Days of wasted compute on failure |
| No multi-user support | Team bottleneck — one person at a time |
| No audit trail | Compliance risk — can't prove correctness |
| AI tools hallucinate SQL syntax | Silent semantic errors in production |
| Manual retry loops | Weeks spent fixing validation errors |

**Root Cause**: Existing tools treat migration as a single atomic operation rather than a pipeline of independently resumable, validatable, auditable tasks.

---

## Goals

### Primary Goals

| ID | Goal | Measurable Target |
|---|---|---|
| G1 | Reliable DB2 → Azure SQL conversion | ≥ 85% auto-conversion rate |
| G2 | Crash-resilient pipelines | Resume within 30s after failure |
| G3 | Multi-user concurrent processing | ≥ 5 concurrent pipelines |
| G4 | Background execution independent of UI | Workers survive UI restart |
| G5 | Full audit trail | 100% of transformations logged |
| G6 | AI-assisted correction workflows | ≥ 60% reduction in manual effort |
| G7 | Cross-platform portability | Backend runs on Linux without changes |

### Non-Goals

- Real-time collaborative schema editing
- Fully autonomous production deployment
- Browser-only execution
- Serverless infrastructure
- Live bidirectional schema synchronization
- Data migration (schema structure only)

---

## Target Users

### 1. Migration Lead (Primary)
- **Role**: Senior DBA or architect leading a DB2 → Azure migration
- **Need**: Dashboard showing pipeline health, team progress, failure hotspots
- **Success**: Can assign pipeline segments and track completion

### 2. Database Administrator
- **Role**: DBA executing individual migration tasks
- **Need**: Upload schema → start → monitor → download converted SQL
- **Success**: ≥ 85% of converted SQL passes validation on first attempt

### 3. Cloud Migration Consultant
- **Role**: External consultant managing migrations for clients
- **Need**: Project isolation, structured pipeline, exportable reports
- **Success**: Consistent, repeatable workflow across engagements

### 4. System Integrator
- **Role**: Developer connecting legacy DB2 to modern Azure workloads
- **Need**: Side-by-side diff with AI explanations
- **Success**: Understands every transformation decision

---

## Functional Requirements

### Authentication & Authorization

| ID | Requirement | Priority |
|---|---|---|
| FR-AUTH-01 | User registration and login | Must |
| FR-AUTH-02 | Role-based access (Admin, Operator, Viewer) | Must |
| FR-AUTH-03 | Session persistence across restarts | Must |
| FR-AUTH-04 | Password hashing (bcrypt) | Must |
| FR-AUTH-05 | API key support for service accounts | Should |

### Pipeline Management

| ID | Requirement | Priority |
|---|---|---|
| FR-PIPE-01 | Create pipeline from uploaded schema | Must |
| FR-PIPE-02 | Accept .sql/.ddl files up to 500MB | Must |
| FR-PIPE-03 | Start / Pause / Resume / Cancel | Must |
| FR-PIPE-04 | Retry individual failed chunks | Must |
| FR-PIPE-05 | Real-time progress tracking | Must |
| FR-PIPE-06 | Concurrent pipelines | Should |

### Schema Processing

| ID | Requirement | Priority |
|---|---|---|
| FR-PARSE-01 | Chunk schemas into individual objects | Must |
| FR-PARSE-02 | AST generation per chunk | Must |
| FR-PARSE-03 | Dependency graph construction | Must |
| FR-PARSE-04 | Object classification | Must |

### Conversion Engine

| ID | Requirement | Priority |
|---|---|---|
| FR-CONV-01 | Deterministic datatype mapping | Must |
| FR-CONV-02 | Constraint/identity/sequence conversion | Must |
| FR-CONV-03 | AI procedure translation | Must |
| FR-CONV-04 | AI trigger translation | Must |
| FR-CONV-05 | Conversion confidence scoring | Should |

### Validation & Retry

| ID | Requirement | Priority |
|---|---|---|
| FR-VAL-01 | Syntax + execution validation | Must |
| FR-VAL-02 | Structured error parsing | Must |
| FR-VAL-03 | AI retry loop (max 3 retries) | Must |
| FR-VAL-04 | Manual review queue | Should |

### Logging & Artifacts

| ID | Requirement | Priority |
|---|---|---|
| FR-LOG-01 | Structured JSON logging | Must |
| FR-LOG-02 | Per-chunk log streams | Must |
| FR-LOG-03 | AI prompt/response storage | Must |
| FR-ART-01 | Immutable original SQL storage | Must |
| FR-ART-02 | Versioned conversion artifacts | Must |
| FR-ART-03 | Side-by-side diff view | Should |
| FR-ART-04 | Bulk ZIP download | Should |

---

## Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| Scalability | Large schema support | 10,000+ objects |
| Scalability | Parallel chunk processing | ≥ 20 concurrent chunks |
| Reliability | Crash recovery | Resume within 30 seconds |
| Reliability | Worker recovery | Orphaned tasks requeued in 60s |
| Performance | API response time | p95 < 200ms |
| Performance | Pipeline throughput | ≥ 100 chunks/hour/worker |
| Security | Credential encryption | AES-256 at rest |
| Security | Audit trail | All mutations logged |
| Portability | Windows desktop | Windows 10/11 |
| Portability | Future Linux | Ubuntu 22.04+ |

---

## Success Metrics

| Metric | Target |
|---|---|
| Auto-conversion rate | ≥ 85% |
| First-attempt validation pass | ≥ 70% |
| Post-retry validation pass | ≥ 90% |
| Mean pipeline time (5K objects) | < 4 hours |
| Manual correction reduction vs SSMA | ≥ 60% |
| Resume time after crash | < 30 seconds |
