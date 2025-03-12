from collections.abc import Generator
from typing import Annotated

import jwt
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.core.logging import get_logger
from app.models import TokenPayload, User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

# Create a logger for this module
logger = get_logger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

logger.debug(f"OAuth2 token URL configured: {settings.API_V1_STR}/login/access-token")


def get_db() -> Generator[Session, None, None]:
    """Get a database session."""
    logger.debug("Creating new database session")
    try:
        with Session(engine) as session:
            yield session
            logger.debug("Database session closed")
    except Exception as e:
        logger.exception("Error with database session", exc_info=e)
        raise


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Get the current user from the token."""
    logger.debug("Authenticating user from token")
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        logger.debug(f"Token decoded successfully for subject: {token_data.sub}")
    except (InvalidTokenError, ValidationError) as e:
        logger.warning(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = session.get(User, token_data.sub)
    if not user:
        logger.warning(f"User not found for token subject: {token_data.sub}")
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        logger.warning(f"Inactive user attempted login: {user.id}")
        raise HTTPException(status_code=400, detail="Inactive user")

    logger.info(f"User authenticated: {user.id}", extra={"user_id": str(user.id)})
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Check if the current user is a superuser."""
    if not current_user.is_superuser:
        logger.warning(
            f"User {current_user.id} attempted to access superuser-only endpoint",
            extra={"user_id": str(current_user.id)},
        )
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    logger.debug(f"Superuser access granted: {current_user.id}")
    return current_user
