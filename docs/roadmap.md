# Roadmap

---

## Version 1.0 — MVP (Weeks 1-19)

**Goal**: Reliable DB2 → Azure SQL desktop migration tool for a single team.

### Milestone 1: Core Infrastructure (Weeks 1-4)
- [ ] Project scaffolding (backend + frontend)
- [ ] PostgreSQL + Redis setup
- [ ] Authentication (JWT + RBAC)
- [ ] Job queue infrastructure (RQ)
- [ ] Worker heartbeat system
- [ ] Database schema + Alembic migrations

### Milestone 2: Parsing & Conversion (Weeks 5-8)
- [ ] DB2 schema chunking
- [ ] AST generation via sqlglot
- [ ] Dependency graph construction
- [ ] Deterministic conversion rules (datatypes, constraints, identities)
- [ ] Conversion rule registry

### Milestone 3: AI & Validation (Weeks 9-13)
- [ ] AI provider abstraction (OpenAI + Anthropic)
- [ ] Procedure/trigger translation prompts
- [ ] SQL validation against Azure SQL
- [ ] Error parsing + AI retry loop
- [ ] Token/cost tracking

### Milestone 4: Frontend & Packaging (Weeks 14-19)
- [ ] Dashboard (stats, queue health, workers)
- [ ] Pipeline management UI (create, monitor, control)
- [ ] Log viewer with filtering
- [ ] Artifact viewer with diff
- [ ] Tauri desktop packaging
- [ ] Windows installer

### v1.0 Deliverables
| Feature | Status |
|---|---|
| DB2 → Azure SQL conversion | ✅ |
| Long-running resumable pipelines | ✅ |
| AI-assisted procedure conversion | ✅ |
| Automated validation loop | ✅ |
| Multi-user access | ✅ |
| Structured logging + audit | ✅ |
| Windows desktop installer | ✅ |

---

## Version 1.5 — Hardening (Weeks 20-24)

**Goal**: Production stability, performance optimization, user feedback incorporation.

### Features
- [ ] Performance profiling and optimization
- [ ] Enhanced error messages and UX polish
- [ ] Bulk retry operations
- [ ] Pipeline templates (save/reuse configurations)
- [ ] Export reports (PDF/CSV of migration results)
- [ ] Dark mode UI
- [ ] Keyboard shortcuts
- [ ] User preferences persistence

### Technical
- [ ] Load testing with 10K+ object schemas
- [ ] Memory profiling and leak detection
- [ ] Worker pool auto-tuning
- [ ] Database query optimization
- [ ] Log archival automation

---

## Version 2.0 — Server Deployment (Months 6-9)

**Goal**: Deploy on Linux servers for always-on, multi-team access.

### Features
- [ ] Docker Compose deployment
- [ ] Web-only UI (no Tauri dependency)
- [ ] Distributed worker pool
- [ ] WebSocket / SSE real-time updates
- [ ] Advanced diff visualization (semantic diff)
- [ ] Dependency visualization graph
- [ ] Manual review workflow UI
- [ ] Team/project permissions

### Observability
- [ ] Prometheus metrics integration
- [ ] Grafana dashboards
- [ ] Alerting rules (PagerDuty/Slack)
- [ ] Distributed tracing (OpenTelemetry)

### Technical
- [ ] SQLAlchemy async migration
- [ ] Connection pooling optimization
- [ ] Horizontal worker scaling
- [ ] Database partitioning for logs

---

## Version 3.0 — Enterprise & Multi-DB (Months 12-18)

**Goal**: Multi-database support, cloud deployment, enterprise features.

### Features
- [ ] Oracle → Azure SQL migration support
- [ ] PostgreSQL → Azure SQL migration support
- [ ] MySQL → Azure SQL migration support
- [ ] Cloud-native deployment (Azure Container Apps)
- [ ] Managed database services (Azure SQL, Azure Cache)
- [ ] SSO integration (SAML, OIDC)
- [ ] Multi-tenant SaaS architecture
- [ ] API-first workflow (headless mode)

### AI Enhancements
- [ ] Fine-tuned migration model
- [ ] Semantic validation engine
- [ ] AI explainability layer (explain why transformation was made)
- [ ] Confidence calibration (learn from historical accuracy)
- [ ] Auto-classification improvement (learn which objects need AI)

### Enterprise
- [ ] Remote execution clusters
- [ ] Multi-region deployment
- [ ] Compliance reporting (SOC2, HIPAA audit export)
- [ ] Custom rule authoring UI
- [ ] Plugin system for custom transformations

---

## Version 4.0 — Platform (Months 18-24)

**Goal**: SchemaForge as a platform for any database migration.

### Vision
- [ ] Universal SQL dialect translation
- [ ] Schema comparison and sync (bi-directional)
- [ ] Migration marketplace (community rules/prompts)
- [ ] IDE plugins (VS Code, JetBrains)
- [ ] CLI tool for CI/CD pipeline integration
- [ ] REST API for third-party integration

---

## Timeline Visualization

```
Month   1   2   3   4   5   6   7   8   9  10  11  12  ...  18  ...  24
        ├───────────────────┤
              v1.0 MVP
                            ├─────┤
                            v1.5 Hardening
                                  ├─────────────┤
                                   v2.0 Server
                                                ├─────────────────┤
                                                  v3.0 Enterprise
                                                                  ├──────┤
                                                                   v4.0
```
