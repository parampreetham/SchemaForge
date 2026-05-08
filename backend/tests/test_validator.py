"""Tests for Validation Engine."""

import pytest
from app.services.validation.validator import ErrorParser, Validator

def test_error_parser():
    """Test extracting error code, line, and message from pyodbc exceptions."""
    raw_error = "('42000', \"[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Incorrect syntax near 'X'. (102) (SQLExecDirectW)\")"
    
    parsed = ErrorParser.parse(raw_error)
    assert parsed["error_code"] == "42000"
    assert "Incorrect syntax near 'X'" in parsed["error_message"]
    # No line number in this simple string
    assert parsed["error_line"] is None

def test_error_parser_with_line():
    raw_error = "('42000', \"[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Incorrect syntax near 'X'. Line 14 (102) (SQLExecDirectW)\")"
    
    parsed = ErrorParser.parse(raw_error)
    assert parsed["error_code"] == "42000"
    assert parsed["error_line"] == 14
    assert "Incorrect syntax near 'X'" in parsed["error_message"]

def test_validator_mock_syntax(monkeypatch):
    """Test validator routing with the built-in MockCursor."""
    monkeypatch.setenv("TESTING", "1")
    
    # Should pass
    passed, err = Validator.full_validation("SELECT 1")
    assert passed is True
    assert not err
    
    # Should fail syntax
    passed_fail, err_fail = Validator.full_validation("FAIL_SYNTAX")
    assert passed_fail is False
    assert err_fail["error_code"] == "42000"
    assert "Incorrect syntax near 'FAIL_SYNTAX'" in err_fail["error_message"]
    
    # Should fail exec
    passed_exec, err_exec = Validator.full_validation("FAIL_EXEC")
    assert passed_exec is False
    assert err_exec["error_code"] == "HY000"
    assert "Invalid object name 'FAIL_EXEC'" in err_exec["error_message"]
