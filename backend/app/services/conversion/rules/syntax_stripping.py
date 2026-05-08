"""Syntax stripping rules."""

import re
from app.services.conversion.registry import BaseRule, RuleRegistry

@RuleRegistry.register
class SyntaxStrippingRule(BaseRule):
    """Removes DB2 specific syntax not supported or needed in Azure SQL."""
    priority = 90

    # Patterns to strip out completely
    STRIP_PATTERNS = [
        re.compile(r"\bIN\s+[\"']?\w+[\"']?\s+INDEX\s+IN\s+[\"']?\w+[\"']?", re.IGNORECASE), # IN tablespace INDEX IN tablespace
        re.compile(r"\bIN\s+[\"']?\w+[\"']?", re.IGNORECASE), # IN tablespace
        re.compile(r"\bORGANIZE\s+BY\s+(ROW|COLUMN)", re.IGNORECASE),
        re.compile(r"\bCOMPRESS\s+(YES|NO)", re.IGNORECASE),
        re.compile(r"\bWITH\s+RESTRICT\s+ON\s+DROP\b", re.IGNORECASE),
        re.compile(r"\bNOT\s+LOGGED\s+INITIALLY\b", re.IGNORECASE),
    ]

    @classmethod
    def apply(cls, sql: str, metadata: dict) -> tuple[str, bool]:
        if metadata.get("object_type") not in ("TABLE", "ALTER_TABLE", "INDEX"):
            return sql, True
            
        current_sql = sql
        for pattern in cls.STRIP_PATTERNS:
            current_sql = pattern.sub("", current_sql)
            
        return current_sql, True
