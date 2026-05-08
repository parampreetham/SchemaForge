"""Tests for AI Engine."""

import pytest
import os
from decimal import Decimal
from app.services.ai.engine import AIEngine
from app.services.ai.provider import AIProvider

def test_extract_sql():
    # Test valid block
    content = "Here is the code:\n```sql\nSELECT * FROM T;\n```\nHope it helps!"
    sql = AIEngine._extract_sql(content)
    assert sql == "SELECT * FROM T;"
    
    # Test block without 'sql'
    content2 = "```\nEXEC PROC;\n```"
    sql2 = AIEngine._extract_sql(content2)
    assert sql2 == "EXEC PROC;"
    
    # Test no block
    content3 = "SELECT 1;"
    sql3 = AIEngine._extract_sql(content3)
    assert sql3 is None

def test_confidence_score():
    # Perfect score
    score = AIEngine._calculate_confidence("SELECT 1 FROM T", "SELECT 1 FROM T", "```sql\nSELECT 1 FROM T\n```")
    assert score == 0.95
    
    # Warning deduction
    score_warn = AIEngine._calculate_confidence("SELECT 1", "SELECT 1", "Note: this is a guess\n```sql\nSELECT 1\n```")
    assert score_warn == 0.90
    
    # Length deduction
    score_len = AIEngine._calculate_confidence("SELECT 1", "SELECT 1 "*20, "```sql\nSELECT 1\n```")
    assert score_len == 0.85

def test_engine_translation_with_mock(monkeypatch):
    """Test engine using the built-in mock in AIProvider."""
    # Ensure TESTING is set so the mock triggers
    monkeypatch.setenv("TESTING", "1")
    
    sql, metrics = AIEngine.translate("CREATE PROCEDURE P AS BEGIN END;", "PROCEDURE")
    
    assert sql == "CREATE PROCEDURE P1 AS\nBEGIN\nEND;"
    assert metrics["input_tokens"] >= 0
    assert metrics["output_tokens"] >= 0
    assert isinstance(metrics["cost_usd"], Decimal)
    assert metrics["confidence_score"] > 0
