# Risks & Considerations

---

## Risk Matrix

| Risk | Probability | Impact | Severity | Mitigation Status |
|---|---|---|---|---|
| AI hallucination | High | High | 🔴 Critical | Mitigated by design |
| Massive token costs | Medium | High | 🟠 High | Mitigated by design |
| Silent semantic errors | Medium | Critical | 🔴 Critical | Partially mitigated |
| Long-running worker failures | Medium | Medium | 🟡 Medium | Mitigated by design |
| sqlglot DB2 dialect gaps | Medium | Medium | 🟡 Medium | Workaround planned |
| Windows service instability | Low | Medium | 🟢 Low | Mitigated |
| Dependency packaging complexity | Medium | Low | 🟢 Low | Mitigated |
| AI API rate limiting | Low | Medium | 🟡 Medium | Planned |
| Azure SQL connection failures | Low | Medium | 🟡 Medium | Mitigated |
| Data privacy (schema content) | Low | High | 🟠 High | Planned |

---

## Technical Risks

### 1. AI Hallucination (🔴 Critical)

**Risk**: AI generates syntactically valid but semantically incorrect SQL — business logic silently altered.

**Probability**: High — LLMs consistently produce plausible-looking but incorrect SQL.

**Mitigations**:
- ✅ **Deterministic-first**: AI only handles what rules can't — reduces AI surface area by 60-80%
- ✅ **Mandatory validation**: Every AI output executed against Azure SQL before acceptance
- ✅ **Error feedback loop**: Validation errors fed back as correction context
- ✅ **Confidence scoring**: Low-confidence conversions flagged for human review
- ⬜ **Golden test cases**: Known-good input/output pairs for regression testing (v1.5)
- ⬜ **Semantic comparison**: Compare query plans of original vs converted (v2.0)

**Residual Risk**: Semantic correctness can't be fully verified without understanding business intent. Human review remains essential for critical procedures.

---

### 2. Massive Token Costs (🟠 High)

**Risk**: Large schemas with thousands of procedures consume millions of tokens, creating unexpected costs.

**Probability**: Medium — depends on schema complexity.

**Mitigations**:
- ✅ **Chunking**: Small chunks = smaller prompts = lower cost per call
- ✅ **Deterministic-first**: Majority of objects never touch AI
- ✅ **Token tracking**: Every AI call logs token count and calculated cost
- ✅ **Budget limits**: Configurable max cost per pipeline (default $50)
- ✅ **Model tiering**: Cheap models (GPT-4o-mini) for simple corrections
- ⬜ **Caching**: Hash-based caching for identical input patterns (v1.5)
- ⬜ **Cost alerts**: Pipeline auto-pauses when budget threshold reached

**Estimated Costs**:
| Schema Size | Est. AI Chunks | Est. Cost |
|---|---|---|
| 1,000 objects | ~200 procedures | $5-15 |
| 5,000 objects | ~1,000 procedures | $25-75 |
| 10,000 objects | ~2,500 procedures | $60-200 |

---

### 3. Silent Semantic Errors (🔴 Critical)

**Risk**: Converted SQL passes syntax validation but produces different results than the original DB2 logic.

**Probability**: Medium — especially for complex cursor logic and DB2-specific functions.

**Mitigations**:
- ✅ **Execution validation**: SQL deployed and tested against Azure SQL
- ⬜ **Golden test cases**: Predefined input/output for known procedures (v1.5)
- ⬜ **Query plan comparison**: Compare execution plans original vs converted (v2.0)
- ⬜ **Data-driven testing**: Run same test data through both engines (v3.0)

**Residual Risk**: Full semantic verification requires understanding business intent. Recommend human review for all HIGH-complexity objects.

---

### 4. sqlglot DB2 Dialect Gaps (🟡 Medium)

**Risk**: sqlglot may not support all DB2-specific syntax, causing parsing failures.

**Probability**: Medium — DB2 has many vendor-specific extensions.

**Mitigations**:
- ✅ **Parser Agent**: AI assists with unparseable SQL
- ✅ **Graceful degradation**: Unparseable chunks classified as UNKNOWN, routed to AI
- ⬜ **Custom dialect extensions**: Extend sqlglot with DB2-specific rules (v1.0)
- ⬜ **Community contribution**: Upstream fixes to sqlglot (ongoing)

---

### 5. Long-Running Worker Failures (🟡 Medium)

**Risk**: Workers crash mid-processing (OOM, network issues), leaving tasks in limbo.

**Probability**: Medium — especially with large procedures and long AI calls.

**Mitigations**:
- ✅ **Heartbeat system**: Workers report health every 30 seconds
- ✅ **Orphan detection**: CleanupWorker requeues tasks from stale workers
- ✅ **Persistent checkpoints**: Task progress saved to DB, not memory
- ✅ **Graceful shutdown**: SIGTERM → finish current task → exit
- ✅ **Retry system**: Configurable retries per chunk

---

### 6. AI API Rate Limiting (🟡 Medium)

**Risk**: OpenAI/Anthropic rate limits throttle conversion speed during peak usage.

**Mitigations**:
- ✅ **Retry with backoff**: Rate limit errors trigger exponential backoff
- ⬜ **Multi-provider failover**: Switch to backup provider on rate limit
- ⬜ **Request queuing**: Internal queue with rate-aware dispatching
- ⬜ **Batch optimization**: Group small objects into single prompts

---

## Operational Risks

### 7. Windows Service Instability (🟢 Low)

**Risk**: Windows services (NSSM) may fail to restart or have permission issues.

**Mitigations**:
- ✅ **Tauri sidecar**: Primary approach — Tauri manages process lifecycle
- ✅ **Fallback to NSSM**: For background service deployment
- ✅ **Health monitoring**: Dashboard shows worker status
- ⬜ **Auto-restart scripts**: Watchdog script for service recovery

---

### 8. Dependency Packaging Complexity (🟢 Low)

**Risk**: Packaging Python + PostgreSQL + Redis into a Windows installer is non-trivial.

**Mitigations**:
- ✅ **Docker Desktop option**: Optional Docker-based deployment
- ✅ **Embedded PostgreSQL**: Portable PG distribution for Windows
- ✅ **Redis Windows port**: Memurai or Windows Redis fork
- ⬜ **Installer automation**: NSIS/WiX installer with dependency checks

---

### 9. Data Privacy — Schema Content Exposure (🟠 High)

**Risk**: Database schemas sent to AI APIs (OpenAI/Anthropic) may contain sensitive column names, table structures, or business logic.

**Probability**: Low (controlled by customer), but impact is HIGH.

**Mitigations**:
- ⬜ **Data classification**: Warn users about sensitive schema content
- ⬜ **Local AI option**: Support local LLM deployment (Ollama) for air-gapped environments
- ⬜ **Redaction engine**: Optionally anonymize object names before AI processing
- ⬜ **DPA compliance**: Data Processing Agreement with AI providers
- ✅ **Transparency**: All AI prompts/responses logged for audit

---

## Dependency Risks

| Dependency | Risk | Mitigation |
|---|---|---|
| sqlglot | DB2 support incomplete | Contribute upstream, build custom extensions |
| OpenAI API | Pricing changes, deprecation | Multi-provider abstraction, local model fallback |
| Redis (Windows) | Limited Windows support | Memurai or Docker |
| Tauri | Breaking changes in v2 | Pin version, follow upgrade guides |
| shadcn/ui | Component API changes | Copy-paste model — no vendor lock |
| Azure SQL | Connection/firewall issues | Clear setup docs, connection validation on startup |

---

## Decision Log

| Decision | Choice | Alternatives Considered | Rationale |
|---|---|---|---|
| Queue system | RQ | Celery, Dramatiq | Simplest for desktop deployment |
| Desktop runtime | Tauri | Electron | 10x smaller binary, Rust-native |
| State management | Zustand | Redux, Jotai | Zero boilerplate, tiny bundle |
| SQL parser | sqlglot | ANTLR, manual parsing | Multi-dialect AST, pure Python |
| Database | PostgreSQL | SQLite, MySQL | JSONB support, reliability, future scaling |
| ORM | SQLAlchemy 2.x | Tortoise, Django ORM | Async support, repository pattern |
