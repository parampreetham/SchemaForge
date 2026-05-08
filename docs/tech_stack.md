# Technology Stack

---

## Stack Overview

| Layer | Technology | Version | Justification |
|---|---|---|---|
| Desktop Shell | Tauri | 2.x | Lightweight (< 10MB), Rust-based, no Chromium overhead vs Electron |
| Frontend | Next.js (React) | 15.x | File-based routing, SSR capability, strong TypeScript support |
| Styling | Tailwind CSS | 4.x | Utility-first, consistent design tokens, small bundle |
| UI Components | shadcn/ui | Latest | Accessible, customizable, no vendor lock-in (copy-paste model) |
| State Management | Zustand | 5.x | Minimal boilerplate, predictable updates, React 19 compatible |
| Backend API | FastAPI | 0.115+ | Async-first, auto-generated OpenAPI docs, type validation via Pydantic |
| Queue | Redis + RQ | 7.x / 1.16+ | Simple, reliable, Python-native; sufficient for desktop-scale workloads |
| Database | PostgreSQL | 16+ | ACID compliance, JSON support, excellent indexing, battle-tested |
| ORM | SQLAlchemy | 2.x | Async support, flexible query building, repository pattern friendly |
| Migrations | Alembic | 1.13+ | First-class SQLAlchemy integration, auto-generation of diffs |
| SQL Parser | sqlglot | 25+ | Multi-dialect AST parsing, DB2 support, pure Python |
| AI SDK | litellm (OpenAI/Anthropic) | Latest | Universal abstraction layer for multiple AI providers |
| Auth | PyJWT + bcrypt | Latest | Stateless JWT tokens, industry-standard password hashing |
| Logging | structlog | 24+ | Structured JSON output, processor pipeline, correlation IDs |
| Validation Target | pyodbc (SQL Server / Azure SQL) | 2019+ | Target deployment platform for generated SQL validation |
| Testing (Backend) | pytest + pytest-asyncio | Latest | Async test support, fixtures, parametrize |
| Testing (Frontend) | Vitest + Testing Library | Latest | Fast, Vite-native, component testing |
| Containerization | Docker + Compose | Latest | Local dev environment, future Linux deployment |
| Packaging | Tauri Bundler | 2.x | Cross-platform installer generation |

---

## Alternatives Considered

### Queue System: RQ vs Celery vs Dramatiq

| Criteria | RQ | Celery | Dramatiq |
|---|---|---|---|
| Simplicity | ✅ Excellent | ❌ Complex | ⚠️ Moderate |
| Python-native | ✅ | ✅ | ✅ |
| Redis-only | ✅ | ❌ (supports many) | ✅ |
| Desktop suitability | ✅ Lightweight | ❌ Heavy | ⚠️ Moderate |
| Reliability | ✅ Good | ✅ Excellent | ✅ Good |
| Community | ⚠️ Moderate | ✅ Large | ⚠️ Small |

**Decision**: RQ chosen for simplicity and lightweight footprint — critical for desktop deployment. If we move to distributed Linux deployment (v2.0+), we'll evaluate Celery migration.

### Desktop Runtime: Tauri vs Electron

| Criteria | Tauri | Electron |
|---|---|---|
| Binary size | ✅ ~10MB | ❌ ~150MB |
| Memory usage | ✅ Low | ❌ High |
| Native feel | ✅ WebView2 | ⚠️ Chromium |
| Ecosystem | ⚠️ Growing | ✅ Mature |
| Sidecar support | ✅ Built-in | ⚠️ Manual |

**Decision**: Tauri for significantly smaller footprint and built-in sidecar process management (critical for launching FastAPI backend).

### State Management: Zustand vs Redux vs Jotai

| Criteria | Zustand | Redux Toolkit | Jotai |
|---|---|---|---|
| Boilerplate | ✅ Minimal | ❌ Moderate | ✅ Minimal |
| DevTools | ✅ | ✅ | ⚠️ |
| Async support | ✅ Native | ⚠️ Thunks | ✅ |
| Bundle size | ✅ ~1KB | ⚠️ ~12KB | ✅ ~3KB |

**Decision**: Zustand for zero-boilerplate stores with excellent TypeScript support.

---

## Version Pinning Strategy

- **Major versions pinned** in `requirements.txt` / `package.json`
- **Minor versions floating** for security patches
- **Lock files committed**: `requirements.lock` + `package-lock.json`
- **Quarterly dependency audit** via `pip-audit` and `npm audit`
- **Renovate/Dependabot** for automated update PRs (future)

---

## Migration Path Considerations

| Current Choice | Future Upgrade Path | Trigger |
|---|---|---|
| RQ | Celery or Temporal | Distributed workers needed (v2.0) |
| SQLAlchemy sync | SQLAlchemy async | High concurrency requirements |
| Local PostgreSQL | Managed Azure SQL | Cloud deployment (v3.0) |
| Local Redis | Azure Cache for Redis | Cloud deployment (v3.0) |
| Tauri desktop | Web-only deployment | Enterprise SaaS offering (v3.0) |
