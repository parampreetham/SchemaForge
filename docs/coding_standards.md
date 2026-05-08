# Coding Standards

---

## Python (Backend)

### Style
- **Formatter**: Ruff (format)
- **Linter**: Ruff (lint)
- **Line length**: 100 characters
- **Quotes**: Double quotes (`"`)
- **Imports**: Sorted by ruff (isort-compatible)

### Type Annotations
```python
# ✅ Always annotate function signatures
def get_pipeline(pipeline_id: UUID, db: Session) -> PipelineResponse:
    ...

# ✅ Annotate class attributes
class ChunkTask:
    id: UUID
    status: str
    retry_count: int = 0

# ❌ Never use bare dict/list without type params
def process(data: dict) -> list:  # BAD
def process(data: dict[str, Any]) -> list[ChunkResponse]:  # GOOD
```

### Function Design
```python
# ✅ Small, focused functions (< 30 lines)
# ✅ Single responsibility
# ✅ Clear return types
# ✅ Descriptive names (verbs for functions)

def create_pipeline(project_id: UUID, schema_file: UploadFile) -> PipelineResponse:
    ...

def validate_chunk_sql(chunk: ChunkTask, sql: str) -> ValidationResult:
    ...

# ❌ Avoid god functions
def do_everything(data):  # BAD
```

### Error Handling
```python
# ✅ Specific exceptions with context
class PipelineNotFoundError(Exception):
    def __init__(self, pipeline_id: UUID):
        super().__init__(f"Pipeline {pipeline_id} not found")
        self.pipeline_id = pipeline_id

# ✅ Catch specific exceptions
try:
    result = await ai_provider.generate(prompt)
except AIRateLimitError:
    await asyncio.sleep(backoff)
    # retry
except AITimeoutError:
    logger.error("ai_timeout", task_id=task.id)
    raise

# ❌ Never catch bare Exception (except at top-level handlers)
try:
    ...
except Exception:  # BAD — hides bugs
    pass
```

### Repository Pattern
```python
# ✅ Repository handles all DB access
class PipelineRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, pipeline_id: UUID) -> PipelineJob | None:
        return self.session.query(PipelineJob).filter_by(id=pipeline_id).first()

    def update_status(self, pipeline_id: UUID, status: str) -> None:
        self.session.query(PipelineJob).filter_by(id=pipeline_id).update({"status": status})
        self.session.commit()

# ❌ Never query DB directly in routes or workers
```

### Logging
```python
import structlog

logger = structlog.get_logger()

# ✅ Structured key-value logging
logger.info("chunk_processing_started",
    job_id=str(job.id),
    task_id=str(task.id),
    object_name=task.object_name,
    object_type=task.object_type,
)

# ❌ Never use print()
print(f"Processing {task.id}")  # BAD

# ❌ Never use string formatting in log messages
logger.info(f"Processing task {task.id}")  # BAD — defeats structured logging
```

---

## TypeScript (Frontend)

### Style
- **Formatter**: Prettier
- **Linter**: ESLint (with Next.js config)
- **Line length**: 100 characters
- **Quotes**: Single quotes (`'`)
- **Semicolons**: Yes

### Type Safety
```typescript
// ✅ Always type component props
interface PipelineCardProps {
  pipeline: Pipeline;
  onStart: (id: string) => void;
  onCancel: (id: string) => void;
  isLoading?: boolean;
}

export function PipelineCard({ pipeline, onStart, onCancel, isLoading = false }: PipelineCardProps) {
  // ...
}

// ✅ Type API responses
interface ApiResponse<T> {
  data: T;
  meta: {
    page: number;
    pageSize: number;
    total: number;
  };
}

// ❌ Never use `any`
function processData(data: any) { }  // BAD
function processData(data: unknown) { }  // BETTER — forces type checking
```

### Component Design
```typescript
// ✅ Prefer named exports
export function ChunkTable({ chunks }: ChunkTableProps) { ... }

// ✅ Keep components < 150 lines
// ✅ Extract custom hooks for complex logic
// ✅ Use composition over prop drilling

// ❌ Avoid deeply nested ternaries in JSX
// ❌ Avoid inline styles
// ❌ Avoid useEffect for data fetching (use hooks/services)
```

### State Management
```typescript
// ✅ Zustand store pattern
import { create } from 'zustand';

interface PipelineStore {
  pipelines: Pipeline[];
  isLoading: boolean;
  fetchPipelines: (projectId: string) => Promise<void>;
  updatePipelineStatus: (id: string, status: string) => void;
}

export const usePipelineStore = create<PipelineStore>((set) => ({
  pipelines: [],
  isLoading: false,
  fetchPipelines: async (projectId) => {
    set({ isLoading: true });
    const data = await pipelineService.list(projectId);
    set({ pipelines: data, isLoading: false });
  },
  updatePipelineStatus: (id, status) =>
    set((state) => ({
      pipelines: state.pipelines.map((p) =>
        p.id === id ? { ...p, status } : p
      ),
    })),
}));
```

---

## Testing Standards

### Backend (pytest)
```python
# ✅ Test file naming: test_{module}.py
# ✅ Test function naming: test_{scenario}_{expected_result}

def test_create_pipeline_returns_created_status():
    ...

def test_retry_chunk_increments_retry_count():
    ...

def test_cancel_pipeline_sets_cancel_flag():
    ...
```

### Coverage Targets
| Layer | Target |
|---|---|
| Services | ≥ 80% |
| Repositories | ≥ 70% |
| Routes | ≥ 60% |
| Workers | ≥ 60% |
| Utils | ≥ 90% |

### Frontend (Vitest)
```typescript
// ✅ Component tests: test rendering and interaction
// ✅ Hook tests: test state changes
// ✅ Service tests: mock API calls

describe('PipelineCard', () => {
  it('shows progress bar when pipeline is running', () => { ... });
  it('calls onCancel when cancel button clicked', () => { ... });
  it('disables start button when loading', () => { ... });
});
```

---

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

### Types
| Type | Usage |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructuring, no feature change |
| `test` | Adding/updating tests |
| `chore` | Build scripts, dependencies, CI |
| `perf` | Performance improvement |

### Scopes
`parser`, `converter`, `validator`, `worker`, `api`, `auth`, `ui`, `pipeline`, `config`, `db`

### Examples
```
feat(parser): add DB2 LATERAL view detection
fix(worker): handle Redis connection timeout gracefully
docs(api): document pipeline retry endpoint
refactor(converter): extract datatype mapping to registry
test(validator): add SQL Server error parsing tests
chore(deps): update sqlglot to v25.1
```

---

## Code Review Checklist

- [ ] Types are annotated (no `Any`, no `dict` without params)
- [ ] Error handling is specific (no bare `except`)
- [ ] Logging uses structlog with key-value pairs
- [ ] No `print()` statements
- [ ] No hardcoded secrets or credentials
- [ ] Tests added for new logic
- [ ] Repository pattern respected (no direct DB queries in routes/workers)
- [ ] Function is < 30 lines (Python) / Component < 150 lines (TSX)
- [ ] Commit message follows conventional commits
