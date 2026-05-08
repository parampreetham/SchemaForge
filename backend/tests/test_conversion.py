"""Golden tests for Deterministic Conversion Engine."""

import pytest
from app.services.conversion.engine import ConversionEngine

# Golden test cases: (input_db2_sql, object_type, object_name, expected_tsql, expected_status)
GOLDEN_CASES = [
    (
        "CREATE TABLE SCHEMA.T1 (ID INT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1), DATA CLOB, TS TIMESTAMP) IN USERSPACE1;",
        "TABLE",
        "T1",
        "CREATE TABLE SCHEMA.T1 (ID INT IDENTITY(1,1), DATA VARCHAR(MAX), TS DATETIME2);",
        "converted"
    ),
    (
        "CREATE UNIQUE INDEX SCHEMA.IDX ON SCHEMA.T1 (ID) COMPRESS YES;",
        "INDEX",
        "IDX",
        "CREATE UNIQUE INDEX SCHEMA.IDX ON SCHEMA.T1 (ID);",
        "converted"
    ),
    (
        "ALTER TABLE T1 ADD CONSTRAINT CHK CHECK (NVL(DATA, '') <> '') NOT LOGGED INITIALLY;",
        "ALTER_TABLE",
        "T1",
        "ALTER TABLE T1 ADD CONSTRAINT CHK CHECK (ISNULL(DATA, '') <> '');",
        "converted"
    ),
    (
        "CREATE PROCEDURE P1() BEGIN END;",
        "PROCEDURE",
        "P1",
        None,
        "needs_ai"
    )
]

@pytest.mark.parametrize("db2_sql, obj_type, obj_name, expected_tsql, expected_status", GOLDEN_CASES)
def test_deterministic_conversion(db2_sql, obj_type, obj_name, expected_tsql, expected_status):
    """Test standard DB2 inputs against expected T-SQL outputs."""
    metadata = {
        "object_type": obj_type,
        "object_name": obj_name
    }
    
    actual_tsql, status, error = ConversionEngine.convert(db2_sql, metadata)
    
    assert status == expected_status
    assert error is None
    
    if expected_tsql is not None:
        # Strip trailing semicolon for easier comparison if expected didn't have it, 
        # but our expected cases have them.
        assert actual_tsql == expected_tsql
