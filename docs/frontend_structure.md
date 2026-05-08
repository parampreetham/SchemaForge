# Frontend Structure

---

## Directory Layout

```
frontend/
├── app/                              # Next.js App Router
│   ├── layout.tsx                    # Root layout (sidebar, providers)
│   ├── page.tsx                      # Redirect to /dashboard
│   ├── globals.css                   # Tailwind imports + custom tokens
│   │
│   ├── (auth)/                       # Auth route group (no sidebar)
│   │   ├── layout.tsx                # Centered auth layout
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   │
│   ├── (app)/                        # Authenticated route group (with sidebar)
│   │   ├── layout.tsx                # Sidebar + topbar layout
│   │   ├── dashboard/
│   │   │   └── page.tsx              # Overview: active jobs, queue health, stats
│   │   ├── projects/
│   │   │   ├── page.tsx              # Project list
│   │   │   ├── new/page.tsx          # Create project
│   │   │   └── [projectId]/
│   │   │       ├── page.tsx          # Project detail
│   │   │       └── pipelines/
│   │   │           ├── page.tsx      # Pipeline list for project
│   │   │           └── [pipelineId]/
│   │   │               └── page.tsx  # Pipeline detail (progress, chunks, logs)
│   │   ├── logs/
│   │   │   └── page.tsx              # Global log viewer with filters
│   │   ├── workers/
│   │   │   └── page.tsx              # Worker health and status
│   │   ├── artifacts/
│   │   │   └── [artifactId]/
│   │   │       └── page.tsx          # Artifact viewer with diff
│   │   └── settings/
│   │       └── page.tsx              # App settings (AI config, validation target)
│   │
│   └── not-found.tsx                 # 404 page
│
├── components/
│   ├── ui/                           # shadcn/ui primitives (Button, Card, Table, etc.)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── table.tsx
│   │   ├── badge.tsx
│   │   ├── dialog.tsx
│   │   ├── toast.tsx
│   │   ├── skeleton.tsx
│   │   ├── progress.tsx
│   │   ├── tabs.tsx
│   │   └── dropdown-menu.tsx
│   │
│   ├── layout/
│   │   ├── sidebar.tsx               # Fixed sidebar navigation
│   │   ├── topbar.tsx                # Breadcrumbs + user menu
│   │   ├── page-header.tsx           # Page title + actions
│   │   └── error-boundary.tsx        # Error fallback UI
│   │
│   ├── dashboard/
│   │   ├── stats-cards.tsx           # Active/completed/failed job counts
│   │   ├── queue-health.tsx          # Queue depth visualization
│   │   ├── recent-pipelines.tsx      # Recent pipeline activity
│   │   └── worker-status.tsx         # Worker heartbeat indicators
│   │
│   ├── pipeline/
│   │   ├── pipeline-card.tsx         # Pipeline summary card
│   │   ├── pipeline-progress.tsx     # Stage + chunk progress bars
│   │   ├── pipeline-controls.tsx     # Start/Pause/Resume/Cancel buttons
│   │   ├── chunk-table.tsx           # Paginated chunk status table
│   │   ├── chunk-detail.tsx          # Single chunk detail (logs, artifacts, retries)
│   │   └── retry-chain.tsx           # Visualization of retry attempts
│   │
│   ├── logs/
│   │   ├── log-viewer.tsx            # Scrollable structured log display
│   │   ├── log-filters.tsx           # Level, stage, job, task filters
│   │   └── log-entry.tsx             # Single log entry component
│   │
│   ├── artifacts/
│   │   ├── sql-viewer.tsx            # Syntax-highlighted SQL display
│   │   ├── diff-viewer.tsx           # Side-by-side original vs converted
│   │   └── download-button.tsx       # Download artifact / bulk ZIP
│   │
│   └── common/
│       ├── loading-spinner.tsx
│       ├── empty-state.tsx           # "No data yet" illustrations
│       ├── status-badge.tsx          # RUNNING, FAILED, COMPLETED badges
│       ├── confirm-dialog.tsx        # Confirmation modal
│       └── data-table.tsx            # Reusable sortable/filterable table
│
├── hooks/
│   ├── use-auth.ts                   # Authentication state hook
│   ├── use-pipeline.ts              # Pipeline data + polling
│   ├── use-logs.ts                   # Log fetching with filters
│   ├── use-polling.ts               # Generic polling hook
│   └── use-debounce.ts              # Input debouncing
│
├── services/
│   ├── api-client.ts                 # Axios/fetch wrapper with auth headers
│   ├── auth-service.ts              # Login, register, token management
│   ├── project-service.ts           # Project API calls
│   ├── pipeline-service.ts          # Pipeline API calls
│   ├── log-service.ts               # Log API calls
│   ├── artifact-service.ts          # Artifact API calls
│   └── worker-service.ts            # Worker health API calls
│
├── stores/
│   ├── auth-store.ts                # User session, token, role
│   ├── pipeline-store.ts            # Active pipeline state
│   ├── ui-store.ts                  # Sidebar state, theme, preferences
│   └── notification-store.ts        # Toast notifications queue
│
├── lib/
│   ├── utils.ts                      # cn() helper, formatters
│   ├── constants.ts                  # Status enums, color maps
│   └── validators.ts                # Form validation schemas (zod)
│
├── types/
│   ├── api.ts                        # API response types
│   ├── models.ts                     # Domain model types
│   └── common.ts                     # Shared utility types
│
├── styles/
│   └── globals.css                   # Tailwind config + custom properties
│
├── public/
│   └── icons/                        # App icons
│
├── tailwind.config.ts
├── next.config.ts
├── tsconfig.json
├── package.json
└── components.json                   # shadcn/ui configuration
```

---

## Key Pages

### Dashboard (`/dashboard`)
- **Stats cards**: Active pipelines, completed today, failed chunks, worker count
- **Queue health**: Bar chart showing queue depth per queue type
- **Recent activity**: Last 10 pipeline events
- **Worker status**: Green/yellow/red indicators per worker

### Pipeline Detail (`/projects/[id]/pipelines/[id]`)
- **Stage progress**: Parsing → Conversion → Validation stages with completion %
- **Chunk table**: Sortable table of all chunks with status, retries, duration
- **Controls**: Start / Pause / Resume / Cancel action buttons
- **Live logs**: Auto-scrolling log stream for this pipeline

### Artifact Viewer (`/artifacts/[id]`)
- **Original SQL**: Syntax-highlighted source DB2 SQL
- **Converted SQL**: Syntax-highlighted target T-SQL
- **Diff view**: Side-by-side diff highlighting changes
- **Retry history**: Timeline of conversion attempts

---

## State Management Pattern

```
Component → Hook → Store → API Service → Backend
                     ↑
              Polling / SSE
```

- **Zustand stores** hold application state
- **Hooks** encapsulate data fetching + store interaction
- **API services** handle HTTP calls
- **Polling** (every 3-5 seconds) for pipeline progress updates
- Future: **Server-Sent Events (SSE)** for real-time updates

---

## Component Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Page component | `page.tsx` (Next.js convention) | `app/(app)/dashboard/page.tsx` |
| Layout | `layout.tsx` | `app/(app)/layout.tsx` |
| UI primitive | `kebab-case.tsx` | `components/ui/button.tsx` |
| Feature component | `kebab-case.tsx` | `components/pipeline/chunk-table.tsx` |
| Hook | `use-kebab-case.ts` | `hooks/use-pipeline.ts` |
| Store | `kebab-case-store.ts` | `stores/auth-store.ts` |
| Service | `kebab-case-service.ts` | `services/pipeline-service.ts` |
| Type file | `kebab-case.ts` | `types/models.ts` |

---

## Responsive Breakpoints

| Breakpoint | Width | Layout |
|---|---|---|
| Desktop | ≥ 1280px | Full sidebar + content |
| Tablet | 768-1279px | Collapsed sidebar + content |
| Mobile | < 768px | Hidden sidebar + hamburger menu |

> **Note**: Primary target is desktop (Tauri). Mobile-responsive is a future nice-to-have.
