"""Tests for security utilities."""

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_returns_different_from_input():
    """Test that hashing produces a different string from the input."""
    password = "TestPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 0


def test_verify_password_correct():
    """Test that correct password verification returns True."""
    password = "TestPassword123!"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test that incorrect password verification returns False."""
    hashed = hash_password("CorrectPassword")
    assert verify_password("WrongPassword", hashed) is False


def test_create_and_decode_token():
    """Test JWT token creation and decoding roundtrip."""
    user_id = "test-user-123"
    role = "operator"
    token = create_access_token(user_id, role)
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert "exp" in payload
    assert "iat" in payload


def test_different_users_get_different_tokens():
    """Test that different users produce different tokens."""
    token1 = create_access_token("user-1", "admin")
    token2 = create_access_token("user-2", "operator")
    assert token1 != token2
