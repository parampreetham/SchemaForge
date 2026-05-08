"""Authentication service."""

import structlog
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User

logger = structlog.get_logger(__name__)


class AuthService:
    """Service handling user registration and authentication."""

    def __init__(self, db: Session):
        self.db = db

    def register(self, username: str, email: str, password: str) -> User:
        """Register a new user.

        Args:
            username: Desired username.
            email: User email address.
            password: Plain text password.

        Returns:
            Created User object.

        Raises:
            ValueError: If username or email already exists.
        """
        # Check for existing username
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError(f"Username '{username}' already exists")

        # Check for existing email
        existing = self.db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError(f"Email '{email}' already registered")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role="operator",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        logger.info("user_registered", user_id=user.id, username=username)
        return user

    def login(self, username: str, password: str) -> tuple[User, str]:
        """Authenticate a user and return a JWT token.

        Args:
            username: Username to authenticate.
            password: Plain text password.

        Returns:
            Tuple of (User, JWT token string).

        Raises:
            ValueError: If credentials are invalid.
        """
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            logger.warning("login_failed", username=username)
            raise ValueError("Invalid username or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        token = create_access_token(user.id, user.role)
        logger.info("user_logged_in", user_id=user.id, username=username)
        return user, token
