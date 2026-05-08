"""Conversion Engine orchestrator."""

import structlog
from app.services.conversion.registry import RuleRegistry

logger = structlog.get_logger()

class ConversionEngine:
    """Orchestrates the conversion of SQL chunks."""

    # Object types that require AI translation
    AI_REQUIRED_TYPES = {"PROCEDURE", "TRIGGER", "FUNCTION"}

    @classmethod
    def convert(cls, sql: str, metadata: dict) -> tuple[str | None, str, str | None]:
        """Convert a SQL string.
        
        Args:
            sql: The original DB2 SQL string.
            metadata: Dictionary containing 'object_type', 'object_name', etc.
            
        Returns:
            tuple[str | None, str, str | None]:
                - Converted SQL string (or None if sending to AI)
                - The status: 'converted' or 'needs_ai'
                - An error message if any
        """
        obj_type = metadata.get("object_type", "UNKNOWN")
        
        if obj_type in cls.AI_REQUIRED_TYPES or obj_type == "UNKNOWN":
            logger.info("Bypassing deterministic conversion, AI required", object_type=obj_type)
            return None, "needs_ai", None

        try:
            converted_sql, is_safe = RuleRegistry.apply_all(sql, metadata)
            if not is_safe:
                logger.info("Deterministic conversion bailed out, AI required", object_type=obj_type)
                return None, "needs_ai", None
            
            return converted_sql.strip().rstrip(";").strip() + ";", "converted", None
            
        except Exception as e:
            logger.exception("Deterministic conversion failed", error=str(e))
            # If deterministic engine fails catastrophically, we fallback to AI
            return None, "needs_ai", f"Deterministic conversion error: {str(e)}"
