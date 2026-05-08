"""Function translation rules."""

import re
from app.services.conversion.registry import BaseRule, RuleRegistry

@RuleRegistry.register
class FunctionRule(BaseRule):
    """Converts DB2 built-in functions to T-SQL equivalents."""
    priority = 60

    FUNCTION_MAPPINGS = [
        (r"\bNVL\s*\(", "ISNULL("),
        (r"\bSUBSTR\s*\(", "SUBSTRING("),
        (r"\bDAYS\s*\(", "DATEDIFF(day, '0001-01-01', "), # Rough approximation for DAYS()
        (r"\bVARCHAR_FORMAT\s*\(", "FORMAT("),
        (r"\bUCASE\s*\(", "UPPER("),
        (r"\bLCASE\s*\(", "LOWER("),
    ]

    @classmethod
    def apply(cls, sql: str, metadata: dict) -> tuple[str, bool]:
        # Functions can appear in views and constraints, so we apply broadly to TABLE and VIEW
        if metadata.get("object_type") not in ("TABLE", "ALTER_TABLE", "VIEW"):
            return sql, True
            
        current_sql = sql
        for pattern, replacement in cls.FUNCTION_MAPPINGS:
            current_sql = re.sub(pattern, replacement, current_sql, flags=re.IGNORECASE)
            
        return current_sql, True
