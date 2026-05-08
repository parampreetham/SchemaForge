"""Datatype conversion rules."""

import re
from app.services.conversion.registry import BaseRule, RuleRegistry

@RuleRegistry.register
class DatatypeRule(BaseRule):
    """Converts DB2 specific datatypes to Azure SQL."""
    priority = 80
    
    # DB2 to Azure SQL datatype mappings
    # Using regex to ensure word boundaries and case insensitivity
    DATATYPE_MAPPINGS = [
        (r"\bCLOB\b(?:\(\d+\))?", "VARCHAR(MAX)"),
        (r"\bBLOB\b(?:\(\d+\))?", "VARBINARY(MAX)"),
        (r"\bDECFLOAT\b", "FLOAT"),
        (r"\bTIMESTAMP\b", "DATETIME2"),
        (r"\bXML\b", "XML"),
        (r"\bGRAPHIC\b", "NCHAR"),
        (r"\bVARGRAPHIC\b", "NVARCHAR"),
    ]

    @classmethod
    def apply(cls, sql: str, metadata: dict) -> tuple[str, bool]:
        if metadata.get("object_type") not in ("TABLE", "ALTER_TABLE"):
            return sql, True
            
        current_sql = sql
        for pattern, replacement in cls.DATATYPE_MAPPINGS:
            current_sql = re.sub(pattern, replacement, current_sql, flags=re.IGNORECASE)
            
        return current_sql, True
