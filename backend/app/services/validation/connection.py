"""SQL Server Connection Manager."""

import os
from contextlib import contextmanager
import structlog
from typing import Generator

logger = structlog.get_logger()

# We only import pyodbc if we're not in a mock/test environment
# that completely isolates it, though pyodbc is installed.
try:
    import pyodbc
except ImportError:
    pyodbc = None

class ConnectionManager:
    """Manages connections to Azure SQL / SQL Server for validation."""
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Get the pyodbc connection string."""
        conn_str = os.environ.get("AZURE_SQL_CONNECTION_STRING")
        if not conn_str:
            # Fallback for local testing if not provided
            conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=master;Trusted_Connection=yes;"
        return conn_str

    @classmethod
    @contextmanager
    def get_cursor(cls) -> Generator:
        """Yields a database cursor, handling connection cleanup.
        
        Usage:
            with ConnectionManager.get_cursor() as cursor:
                cursor.execute(...)
        """
        if os.environ.get("TESTING") == "1" or not pyodbc:
            # Yield a mock cursor for automated tests
            yield MockCursor()
            return

        conn = None
        try:
            conn = pyodbc.connect(cls.get_connection_string(), autocommit=False)
            cursor = conn.cursor()
            yield cursor
        except Exception as e:
            logger.error("Database connection failed", error=str(e))
            raise
        finally:
            if conn:
                try:
                    conn.rollback() # Ensure no pending transactions are left
                    conn.close()
                except Exception as e:
                    logger.warning("Error closing database connection", error=str(e))


class MockCursor:
    """Mock cursor for testing without a real SQL Server."""
    def execute(self, query: str):
        if "FAIL_SYNTAX" in query:
            # Simulate a pyodbc.ProgrammingError
            raise Exception("('42000', \"[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Incorrect syntax near 'FAIL_SYNTAX'. (102) (SQLExecDirectW)\")")
        if "FAIL_EXEC" in query:
            raise Exception("('HY000', \"[HY000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Invalid object name 'FAIL_EXEC'. (208) (SQLExecDirectW)\")")
        pass
