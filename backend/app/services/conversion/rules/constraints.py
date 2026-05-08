"""Constraint conversion rules."""

import re
from app.services.conversion.registry import BaseRule, RuleRegistry

@RuleRegistry.register
class ConstraintRule(BaseRule):
    """Converts DB2 specific constraints and identities to Azure SQL."""
    priority = 70

    # GENERATED ALWAYS AS IDENTITY (START WITH x INCREMENT BY y) -> IDENTITY(x, y)
    # Simplified regex for MVP. Robust regex needs to handle optional clauses.
    IDENTITY_PATTERN = re.compile(
        r"GENERATED\s+(?:ALWAYS|BY\s+DEFAULT)\s+AS\s+IDENTITY\s*(?:\(\s*START\s+WITH\s+(\d+)\s+INCREMENT\s+BY\s+(\d+)\s*\))?",
        re.IGNORECASE
    )

    @classmethod
    def apply(cls, sql: str, metadata: dict) -> tuple[str, bool]:
        if metadata.get("object_type") not in ("TABLE", "ALTER_TABLE"):
            return sql, True
            
        current_sql = sql
        
        # Handle identity
        def identity_repl(match):
            start = match.group(1) or "1"
            increment = match.group(2) or "1"
            return f"IDENTITY({start},{increment})"
            
        current_sql = cls.IDENTITY_PATTERN.sub(identity_repl, current_sql)
        
        # We can add more DB2 specific constraint syntax translations here.
        
        return current_sql, True
