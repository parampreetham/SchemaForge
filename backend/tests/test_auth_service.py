"""Tests for auth service."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.services.auth_service import AuthService

engine = create_engine("sqlite:///:memory:")
TestSession = sessionmaker(bind=engine)


def setup_function():
    """Create all tables before each test."""
    Base.metadata.create_all(engine)


def teardown_function():
    """Drop all tables after each test."""
    Base.metadata.drop_all(engine)


def test_register_creates_user():
    """Test that registration creates a new user."""
    db = TestSession()
    service = AuthService(db)
    user = service.register("newuser", "new@example.com", "StrongPass123!")

    assert user.id is not None
    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert user.role == "operator"
    assert user.password_hash != "StrongPass123!"  # Should be hashed
    db.close()


def test_register_duplicate_username_raises():
    """Test that duplicate username raises ValueError."""
    db = TestSession()
    service = AuthService(db)
    service.register("dupe_user", "first@example.com", "Pass123!")

    with pytest.raises(ValueError, match="already exists"):
        service.register("dupe_user", "second@example.com", "Pass123!")
    db.close()


def test_register_duplicate_email_raises():
    """Test that duplicate email raises ValueError."""
    db = TestSession()
    service = AuthService(db)
    service.register("user_a", "same@example.com", "Pass123!")

    with pytest.raises(ValueError, match="already registered"):
        service.register("user_b", "same@example.com", "Pass123!")
    db.close()


def test_login_valid_credentials():
    """Test login with valid username and password."""
    db = TestSession()
    service = AuthService(db)
    service.register("loginuser", "login@example.com", "MyPassword99!")

    user, token = service.login("loginuser", "MyPassword99!")
    assert user.username == "loginuser"
    assert token is not None
    assert len(token) > 0
    db.close()


def test_login_invalid_password():
    """Test login with wrong password raises ValueError."""
    db = TestSession()
    service = AuthService(db)
    service.register("wrongpw", "wp@example.com", "CorrectPassword!")

    with pytest.raises(ValueError, match="Invalid username or password"):
        service.login("wrongpw", "WrongPassword!")
    db.close()


def test_login_nonexistent_user():
    """Test login with nonexistent username raises ValueError."""
    db = TestSession()
    service = AuthService(db)

    with pytest.raises(ValueError, match="Invalid username or password"):
        service.login("ghost_user", "AnyPassword!")
    db.close()
