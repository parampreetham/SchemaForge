"""SQL Server Validator logic."""

import re
import structlog
from typing import Tuple, Dict, Any

from app.services.validation.connection import ConnectionManager

logger = structlog.get_logger()

class ErrorParser:
    """Parses pyodbc error strings to extract code, message, and line number."""
    
    # Matches patterns like: "('42000', \"[42000] [Microsoft]... Incorrect syntax near 'X'. (102) (SQLExecDirectW)\")"
    ERROR_CODE_REGEX = re.compile(r"\[([A-Z0-9]+)\]")
    LINE_NUM_REGEX = re.compile(r"Line (\d+)", re.IGNORECASE)
    
    @classmethod
    def parse(cls, error_str: str) -> Dict[str, Any]:
        """Parse raw error string into structured data."""
        error_code = None
        error_line = None
        error_message = error_str
        
        # Try to extract OBDC error code
        code_match = cls.ERROR_CODE_REGEX.search(error_str)
        if code_match:
            error_code = code_match.group(1)
            
        # Try to extract Line number if SQL Server provides it
        line_match = cls.LINE_NUM_REGEX.search(error_str)
        if line_match:
            error_line = int(line_match.group(1))
            
        # Clean up the message slightly (removing the generic ODBC wrapper text if possible)
        try:
            # Often the actual message is inside the quotes after the brackets
            parts = error_str.split("] [SQL Server]")
            if len(parts) > 1:
                clean_msg = parts[1].split("(SQLExecDirectW)")[0].strip()
                if clean_msg:
                    error_message = clean_msg
        except Exception:
            pass # fallback to original
            
        return {
            "error_code": error_code,
            "error_line": error_line,
            "error_message": error_message
        }


class Validator:
    """Orchestrates validation phases."""
    
    @classmethod
    def validate_syntax(cls, sql: str) -> Tuple[bool, Dict[str, Any]]:
        """Phase 1: Validate syntax only using SET NOEXEC ON."""
        logger.info("Running syntax validation")
        query = f"SET NOEXEC ON;\n{sql}\nSET NOEXEC OFF;"
        
        try:
            with ConnectionManager.get_cursor() as cursor:
                cursor.execute(query)
            return True, {}
        except Exception as e:
            return False, ErrorParser.parse(str(e))

    @classmethod
    def validate_execution(cls, sql: str) -> Tuple[bool, Dict[str, Any]]:
        """Phase 2: Validate execution by wrapping in a rollback transaction."""
        logger.info("Running execution validation")
        query = f"BEGIN TRAN;\n{sql}\nROLLBACK TRAN;"
        
        try:
            with ConnectionManager.get_cursor() as cursor:
                cursor.execute(query)
            return True, {}
        except Exception as e:
            return False, ErrorParser.parse(str(e))
            
    @classmethod
    def full_validation(cls, sql: str) -> Tuple[bool, Dict[str, Any]]:
        """Run syntax validation, then execution validation if applicable."""
        passed, error_details = cls.validate_syntax(sql)
        if not passed:
            return False, error_details
            
        # If syntax passes, try execution
        # (We skip execution if it's purely a syntax check, but the plan calls for both)
        return cls.validate_execution(sql)
