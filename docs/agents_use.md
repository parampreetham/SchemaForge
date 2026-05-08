# AI Agents Usage

---

## Philosophy

AI agents **augment** deterministic systems — they don't replace them. Every object that *can* be converted with rules *must* be converted with rules. AI handles only what requires semantic understanding.

### Decision Matrix: When to Use AI

| Object Type | Deterministic | AI-Assisted | Example |
|---|---|---|---|
| Table DDL | ✅ Always | ❌ Never | `CREATE TABLE` with datatypes, constraints |
| Views (simple) | ✅ Always | ❌ Never | `SELECT` with standard joins |
| Views (complex) | ⚠️ Partial | ✅ For DB2-specific functions | Views with `LATERAL`, `XMLTABLE` |
| Indexes | ✅ Always | ❌ Never | Standard B-tree indexes |
| Sequences | ✅ Always | ❌ Never | `CREATE SEQUENCE` |
| Stored Procedures | ⚠️ Partial | ✅ Always | Cursors, control flow, DB2 functions |
| Triggers | ⚠️ Partial | ✅ Always | Row-level logic, transition tables |
| Functions | ⚠️ Partial | ✅ For complex logic | Scalar/table functions with procedural code |

---

## Agent Types

### 1. Parser Agent

**Purpose**: Assist with malformed or ambiguous SQL that breaks `sqlglot`.

**Responsibilities**:
- Analyze malformed SQL that fails parsing
- Assist chunk classification when object type is ambiguous
- Detect DB2-specific constructs not in sqlglot's dialect map
- Suggest preprocessing transformations for unparseable blocks

**Input**: Raw SQL string that failed parsing + error message
**Output**: Suggested fix or classification

**When Invoked**: Only when `sqlglot.parse()` raises an exception

---

### 2. Conversion Agent (Primary)

**Purpose**: Translate procedural DB2 logic to T-SQL equivalents.

**Responsibilities**:
- Translate stored procedures (cursor logic, control flow)
- Translate triggers (transition tables → `INSERTED`/`DELETED`)
- Rewrite DB2-specific procedural constructs
- Map DB2 built-in functions to T-SQL equivalents
- Handle `DECLARE CURSOR`, `FETCH`, `WHILE`, `SIGNAL`

**Input**: Original DB2 SQL + conversion rules + object metadata
**Output**: Equivalent T-SQL

**Prompt Template Structure**:
```
SYSTEM:
  You are a DB2 to Azure SQL migration expert.
  Convert the following DB2 {object_type} to T-SQL.
  
  Rules:
  - Use T-SQL syntax for all control flow
  - Replace DB2 cursors with T-SQL cursor syntax
  - Map SIGNAL SQLSTATE to THROW
  - Replace transition tables with INSERTED/DELETED
  - Preserve all business logic semantics
  - Output only valid T-SQL, no explanations

USER:
  -- Original DB2 {object_type}: {object_name}
  {original_sql}

  -- Conversion context:
  - Source dialect: DB2 for LUW {version}
  - Target: Azure SQL Database
  - Dependencies: {dependency_list}
```

---

### 3. Validation Agent

**Purpose**: Interpret validation errors and suggest fixes.

**Responsibilities**:
- Parse SQL Server error messages into structured feedback
- Suggest specific syntax corrections
- Generate correction patches
- Explain why the original conversion failed

**Input**: Failed T-SQL + SQL Server error message + original DB2 SQL
**Output**: Corrected T-SQL

**Correction Prompt Structure**:
```
SYSTEM:
  You are debugging a DB2 to Azure SQL conversion.
  The converted T-SQL failed validation.
  Fix ONLY the error while preserving all other logic.

USER:
  -- Original DB2 SQL:
  {original_sql}

  -- Converted T-SQL (failed):
  {converted_sql}

  -- Validation error:
  Error {error_code}: {error_message}
  Line {line_number}: {offending_line}

  -- Fix the error and return corrected T-SQL only.
```

---

### 4. Optimization Agent (Future — v2.0)

**Purpose**: Reduce token usage and improve output quality.

**Responsibilities**:
- Simplify verbose AI-generated SQL
- Detect and eliminate duplicate transformations
- Suggest prompt optimizations based on success patterns
- Identify objects that could be reclassified as deterministic

---

## AI Workflow

```
┌──────────────────┐
│ Original DB2 SQL │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Deterministic    │───── Simple objects: DONE ──→ Validation
│ Conversion       │
└────────┬─────────┘
         │ Complex objects (procedures, triggers)
         ▼
┌──────────────────┐
│ AI Conversion    │ ← Prompt v{N} + conversion rules
│ (Attempt 1)      │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Validation       │
└────────┬─────────┘
    ┌────┴────┐
    ▼         ▼
  PASS      FAIL
    │         │
    │    ┌────▼──────────┐
    │    │ Error Parser  │
    │    └────┬──────────┘
    │         ▼
    │    ┌──────────────────┐
    │    │ AI Correction    │ ← Error context + original SQL
    │    │ (Attempt 2)      │
    │    └────┬─────────────┘
    │         ▼
    │    ┌──────────────────┐
    │    │ Re-Validation    │
    │    └────┬─────────────┘
    │    ┌────┴────┐
    │    ▼         ▼
    │  PASS      FAIL (retry ≤ 3)
    │    │         │
    │    │    ┌────▼──────────┐
    │    │    │ Manual Review │
    │    │    │ Queue         │
    │    │    └───────────────┘
    ▼    ▼
┌──────────────────┐
│ Store Artifact   │
│ Mark Complete    │
└──────────────────┘
```

---

## Token Budget Management

### Cost Control Rules
| Rule | Value |
|---|---|
| Max tokens per chunk (input + output) | 8,000 tokens |
| Max cost per pipeline | Configurable (default $50) |
| Alert threshold | 80% of pipeline budget |
| Chunk size limit for AI | 500 lines (split larger) |

### Cost Tracking
- Every AI call logs: `model`, `input_tokens`, `output_tokens`, `cost_usd`
- Dashboard shows cumulative cost per pipeline
- Cost alerts when threshold reached (pipeline pauses for approval)

### Cost Optimization Strategies
1. **Deterministic-first**: Reduces AI calls by 60-80%
2. **Caching**: Identical input patterns → cached output (hash-based)
3. **Chunk size control**: Smaller chunks = cheaper calls
4. **Model tiering**: Use cheaper models (GPT-4o-mini) for simple corrections, expensive models (Claude Opus) for complex procedures

---

## Model Selection

| Use Case | Recommended Model | Fallback |
|---|---|---|
| Procedure translation | Claude Sonnet 4 | GPT-4o |
| Trigger translation | Claude Sonnet 4 | GPT-4o |
| Error correction | GPT-4o-mini | Claude Haiku |
| Parser assistance | GPT-4o-mini | Claude Haiku |

### Provider Abstraction
```python
class AIProvider(Protocol):
    async def generate(self, prompt: str, max_tokens: int) -> AIResponse: ...

class AIResponse:
    content: str
    input_tokens: int
    output_tokens: int
    model: str
    latency_ms: int
```

---

## AI Safety Rules

1. **Never allow unrestricted generation** — always provide conversion rules in system prompt
2. **Never allow direct deployment** — AI output must pass validation
3. **Always validate generated SQL** — execute against test Azure SQL instance
4. **Always store prompt history** — every prompt + response persisted for audit
5. **Always version prompts** — prompt changes tracked in code with version numbers
6. **Set strict max_tokens** — prevent runaway generation
7. **Timeout all API calls** — 60 second timeout, fail gracefully
8. **Rate limit per pipeline** — max 100 AI calls per minute
