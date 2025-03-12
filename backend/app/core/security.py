from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from app.core.config import settings
from app.core.logging import get_logger
from passlib.context import CryptContext

# Create a logger for this module
logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

logger.debug("Security module initialized with algorithm: %s", ALGORITHM)


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Create a new JWT access token."""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}

    logger.debug(
        "Creating access token",
        extra={
            "subject": str(subject),
            "expires_in_minutes": expires_delta.total_seconds() / 60,
        },
    )

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    result = pwd_context.verify(plain_password, hashed_password)

    logger.debug("Password verification", extra={"success": result})

    return result


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    logger.debug("Generating password hash")
    return pwd_context.hash(password)
