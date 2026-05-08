# MVP Scope

---

## MVP Definition

The MVP delivers a **fully functional desktop migration tool** that can take a DB2 schema file, convert it to Azure SQL, validate the output, and provide downloadable results — all through a polished dashboard UI.

---

## Included in MVP (v1.0)

### Core Pipeline
| Feature | Description | Acceptance Criteria |
|---|---|---|
| Schema upload | Accept DB2 .sql/.ddl files up to 500MB | File accepted, stored immutably, checksum verified |
| Chunking | Split schema into individual objects | Each DB object becomes an independent task |
| AST parsing | Parse chunks via sqlglot | AST generated; malformed SQL flagged |
| Dependency graph | Resolve object dependencies | Topological sort produces valid ordering |
| Deterministic conversion | Rule-based DB2 → T-SQL mapping | Datatypes, constraints, identities convert correctly |
| AI conversion | Procedure/trigger translation via LLM | Complex objects converted with ≥ 70% first-pass accuracy |
| Validation | Execute against Azure SQL/SQL Server | Syntax + execution validation with error capture |
| Retry loop | Validation error → AI correction | Up to 3 retries per chunk with error feedback |

### Pipeline Controls
| Feature | Acceptance Criteria |
|---|---|
| Start pipeline | Pipeline transitions to QUEUED → RUNNING |
| Pause pipeline | No new chunks dispatched; in-flight chunks complete |
| Resume pipeline | Processing resumes from last checkpoint |
| Cancel pipeline | Graceful cancellation; in-flight chunks finish |
| Retry failed chunks | Individual failed chunks can be requeued |

### Crash Resilience
| Feature | Acceptance Criteria |
|---|---|
| Survive reboot | Workers restart; orphaned tasks requeued |
| Resume interrupted pipelines | Pipeline picks up from last completed chunk |
| Persistent checkpoints | All progress saved to database, not memory |
| Worker heartbeats | Stale workers detected within 2 minutes |

### Dashboard
| Feature | Acceptance Criteria |
|---|---|
| Active pipelines overview | Shows running/completed/failed counts |
| Queue health | Shows queue depth per queue type |
| Worker status | Green/yellow/red indicators per worker |
| Pipeline progress | Stage bars + chunk count + percentage |
| Chunk table | Sortable, filterable table of all chunks |
| Log viewer | Structured logs with level/stage/job filtering |
| Artifact viewer | View original + converted SQL side-by-side |

### Authentication
| Feature | Acceptance Criteria |
|---|---|
| User registration | New users can create accounts |
| Login / logout | JWT-based session management |
| RBAC | Admin, Operator, Viewer roles enforced |
| Session persistence | User stays logged in across restarts |

### Desktop Runtime
| Feature | Acceptance Criteria |
|---|---|
| Windows installer | Single installer sets up entire stack |
| Tauri desktop shell | Native window with embedded frontend |
| Backend sidecar | FastAPI launches with desktop app |
| Worker management | Workers start/stop with application |

---

## Excluded from MVP

| Feature | Reason | Target Version |
|---|---|---|
| Distributed workers | Requires Linux server deployment | v2.0 |
| Kubernetes deployment | Enterprise cloud, not needed for desktop | v3.0 |
| Multi-region sync | Cloud-scale requirement | v3.0 |
| Live collaboration | Real-time editing is non-goal | Never |
| Fine-tuned AI models | Requires training infrastructure | v3.0 |
| Multi-database support | Oracle, PostgreSQL, MySQL sources | v3.0 |
| Advanced semantic testing | Data-driven validation | v2.0 |
| Keyboard shortcuts | Power user feature | v1.5 |
| WebSocket real-time updates | Polling sufficient for MVP | v2.0 |
| Export reports (PDF/CSV) | Dashboard sufficient for MVP | v1.5 |
| SSO integration | Enterprise auth feature | v3.0 |
| Plugin system | Extensibility feature | v4.0 |

---

## MVP Success Criteria

### Functional Criteria

| Criteria | Target | How to Verify |
|---|---|---|
| Process 5,000 object schema end-to-end | Complete without crash | Run full pipeline on test schema |
| Survive reboot during processing | Resume within 2 minutes | Kill app mid-pipeline, restart, verify resumption |
| Auto-conversion rate | ≥ 85% | Count chunks passing validation / total chunks |
| AI correction success | ≥ 70% after retries | Count failed→passed chunks / total retried |
| Pipeline completion | < 4 hours for 5,000 objects | Measure wall-clock time |
| Multi-user | 3 users can run simultaneous pipelines | Concurrent login + pipeline creation |
| Audit trail complete | 100% of transformations logged | Verify logs exist for every chunk |

### Non-Functional Criteria

| Criteria | Target | How to Verify |
|---|---|---|
| Installation time | < 15 minutes on clean Windows machine | Time fresh install |
| First pipeline time | < 10 minutes from first launch | Time onboarding flow |
| API response time | p95 < 200ms | Load test non-pipeline endpoints |
| Memory usage | < 4 GB during pipeline | Monitor during 5K object processing |
| Disk usage | < 5 GB for 5K object schema | Measure storage after completion |

---

## MVP Timeline

| Phase | Duration | Deliverable |
|---|---|---|
| Phase 0: Bootstrap | Week 1 | Dev environment + scaffolding |
| Phase 1: Infrastructure | Weeks 2-4 | Queue, workers, DB, auth |
| Phase 2: Parsing | Weeks 5-6 | Chunker, AST, dependency graph |
| Phase 3: Deterministic | Weeks 7-8 | Rule-based conversion engine |
| Phase 4: AI Engine | Weeks 9-11 | AI translation + retry loops |
| Phase 5: Validation | Weeks 12-13 | Azure SQL validation |
| Phase 6: Frontend | Weeks 14-17 | Dashboard + pipeline UI |
| Phase 7: Packaging | Weeks 18-19 | Tauri + installer |
| **Total** | **~19 weeks** | **Full MVP** |

---

## MVP Team Assumption

| Role | Count | Responsibility |
|---|---|---|
| Backend Engineer | 1-2 | API, services, workers, AI integration |
| Frontend Engineer | 1 | Dashboard, pipeline UI, artifact viewer |
| DevOps / Packaging | 0.5 | Tauri integration, installer, CI/CD |
| QA / Testing | 0.5 | Test plans, manual testing, bug reports |

**Minimum viable team**: 2 full-stack engineers

---

## Post-MVP Priority Queue

Once MVP ships, these features are prioritized based on user feedback:

| Priority | Feature | User Value |
|---|---|---|
| P0 | Bug fixes + stability | Essential |
| P1 | Performance optimization | High — faster pipelines |
| P1 | Export reports (CSV/PDF) | High — client deliverables |
| P2 | Dark mode | Medium — user preference |
| P2 | Pipeline templates | Medium — repeat migrations |
| P2 | Bulk retry | Medium — efficiency |
| P3 | Keyboard shortcuts | Low — power users |
| P3 | Custom conversion rules | Low — advanced users |
