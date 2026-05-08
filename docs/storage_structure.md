# Storage Structure

---

## Overview

SchemaForge uses a **file-based artifact storage** system alongside the PostgreSQL database. The database stores metadata; files store actual SQL content and processing artifacts.

---

## Directory Layout

```
storage/                                    # Root storage directory
├── uploads/                                # Raw uploaded schemas (immutable)
│   └── {project_id}/
│       └── {pipeline_id}/
│           ├── original_schema.sql         # Original uploaded file
│           └── upload_metadata.json        # File hash, size, upload time
│
├── jobs/                                   # Per-pipeline processing artifacts
│   └── {pipeline_id}/
│       ├── chunks/                         # Individual chunked objects
│       │   ├── {chunk_id}/
│       │   │   ├── original.sql            # Extracted DB2 SQL for this object
│       │   │   ├── ast.json                # Parsed AST (sqlglot output)
│       │   │   ├── converted_v1.sql        # First conversion attempt
│       │   │   ├── converted_v2.sql        # Retry attempt 2
│       │   │   ├── converted_v3.sql        # Retry attempt 3
│       │   │   ├── validated.sql           # Final validated SQL
│       │   │   └── metadata.json           # Object name, type, dependencies
│       │   └── ...
│       │
│       ├── graphs/                         # Dependency analysis
│       │   ├── dependency_graph.json       # Full dependency graph
│       │   └── topological_order.json      # Sorted processing order
│       │
│       ├── reports/                        # Pipeline reports
│       │   ├── summary.json                # Completion stats
│       │   └── conversion_report.csv       # Per-chunk results table
│       │
│       └── output/                         # Final deliverables
│           ├── converted_schema.sql        # All converted SQL combined
│           └── converted_schema.zip        # ZIP download package
│
├── logs/                                   # File-based log backup
│   └── {date}/
│       ├── api.jsonl                       # API request/response logs
│       ├── workers.jsonl                   # Worker execution logs
│       └── errors.jsonl                    # Error-only logs
│
└── backups/                                # Database backups
    └── {date}/
        └── schemaforge_backup.sql.gz       # pg_dump output
```

---

## Storage Rules

### Immutability Rules
| Rule | Explanation |
|---|---|
| **Never overwrite originals** | `uploads/` directory is append-only |
| **Version retry outputs** | Each retry creates `converted_v{N}.sql` |
| **Keep immutable logs** | Log files are append-only, never edited |
| **Preserve all attempts** | Every conversion attempt stored, not just final |

### File Naming Conventions
| Pattern | Usage |
|---|---|
| `original.sql` | Source DB2 SQL (extracted chunk) |
| `converted_v{N}.sql` | Conversion attempt N (1-indexed) |
| `validated.sql` | Final validated output (copy of passing version) |
| `ast.json` | Parsed abstract syntax tree |
| `metadata.json` | Object metadata (name, type, dependencies) |

### Checksum Verification
```json
// upload_metadata.json
{
  "filename": "banking_schema.sql",
  "size_bytes": 52428800,
  "sha256": "e3b0c44298fc1c149afbf4c8996fb924...",
  "uploaded_at": "2026-01-15T10:30:00Z",
  "uploaded_by": "user-123"
}
```

---

## Storage Paths

### Path Resolution
```python
# Configuration
STORAGE_ROOT = os.getenv("STORAGE_ROOT", "%APPDATA%/SchemaForge/storage")

# Helper functions
def get_upload_path(project_id: str, pipeline_id: str) -> Path:
    return STORAGE_ROOT / "uploads" / project_id / pipeline_id

def get_chunk_path(pipeline_id: str, chunk_id: str) -> Path:
    return STORAGE_ROOT / "jobs" / pipeline_id / "chunks" / chunk_id

def get_output_path(pipeline_id: str) -> Path:
    return STORAGE_ROOT / "jobs" / pipeline_id / "output"
```

### Platform-Specific Defaults
| Platform | Default Storage Root |
|---|---|
| Windows | `%APPDATA%\SchemaForge\storage` |
| Linux | `/var/lib/schemaforge/storage` |
| Docker | `/data/storage` (volume mount) |

---

## Retention & Cleanup

### Retention Policies

| Category | Retention | Cleanup Strategy |
|---|---|---|
| Original uploads | Permanent | Never deleted |
| Processing artifacts (chunks) | 90 days after pipeline completion | CleanupWorker scheduled task |
| Final output (converted SQL) | Permanent | Never deleted |
| Log files | 30 days | Rotate daily, delete old |
| Database backups | 30 days | Keep last 30 daily backups |
| Dependency graphs | 90 days | Cleaned with processing artifacts |

### Cleanup Worker
```python
# Runs daily at 2:00 AM
async def cleanup_old_artifacts():
    cutoff = datetime.now() - timedelta(days=90)
    
    # Find completed pipelines older than 90 days
    old_pipelines = await pipeline_repo.get_completed_before(cutoff)
    
    for pipeline in old_pipelines:
        # Remove processing artifacts (keep originals and output)
        chunk_dir = get_chunk_path(pipeline.id, "*")
        shutil.rmtree(chunk_dir, ignore_errors=True)
        
        # Remove dependency graphs
        graph_dir = storage_root / "jobs" / pipeline.id / "graphs"
        shutil.rmtree(graph_dir, ignore_errors=True)
        
        logger.info("artifacts_cleaned", pipeline_id=str(pipeline.id))
```

---

## Disk Space Estimates

| Schema Size | Upload | Processing (chunks) | Output | Total (peak) |
|---|---|---|---|---|
| 10 MB (500 objects) | 10 MB | ~50 MB | ~15 MB | ~75 MB |
| 50 MB (2,000 objects) | 50 MB | ~250 MB | ~75 MB | ~375 MB |
| 200 MB (5,000 objects) | 200 MB | ~1 GB | ~300 MB | ~1.5 GB |
| 500 MB (10,000 objects) | 500 MB | ~2.5 GB | ~750 MB | ~3.75 GB |

> **Recommendation**: Reserve 10x the upload file size for peak processing storage.

---

## Backup Strategy

### Desktop (Tier 1)
```bash
# Daily backup via Windows Task Scheduler
pg_dump -U schemaforge -Fc schemaforge > backup_%DATE%.dump

# Rotate: keep last 7 daily backups
forfiles /p "backups" /m "*.dump" /d -7 /c "cmd /c del @path"
```

### Server (Tier 2)
```bash
# Daily backup via cron
0 2 * * * pg_dump -U schemaforge -Fc schemaforge | gzip > /backups/$(date +\%Y\%m\%d).sql.gz

# Rotate: keep last 30 days
find /backups -name "*.sql.gz" -mtime +30 -delete
```
