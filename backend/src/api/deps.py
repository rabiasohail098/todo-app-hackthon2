"""FastAPI dependencies for database and authentication."""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from jose import JWTError, jwt
import os
from uuid import UUID
from dotenv import load_dotenv

from ..db.session import get_session

# Load environment variables
load_dotenv()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is not set")

# Security scheme for JWT Bearer tokens
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """Get database session dependency.

    Yields:
        Session: SQLModel database session

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    yield from get_session()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """Get current user from JWT token.

    This dependency extracts and validates the JWT token from the
    Authorization header, then returns the user_id claim.

    Args:
        credentials: HTTP Authorization credentials from Bearer token

    Returns:
        UUID: User ID extracted from JWT token

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired

    Example:
        @app.get("/api/tasks")
        def get_tasks(user_id: UUID = Depends(get_current_user)):
            return {"user_id": str(user_id)}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials

        # Decode JWT token
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        # Extract user_id from 'sub' claim (standard JWT claim for subject)
        user_id_str: Optional[str] = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        # Convert string to UUID
        user_id = UUID(user_id_str)

    except (JWTError, ValueError):
        raise credentials_exception

    return user_id


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[UUID]:
    """Get current user from JWT token if present (optional).

    This dependency is similar to get_current_user but doesn't raise
    an exception if no token is provided. Useful for endpoints that
    can work with or without authentication.

    Args:
        credentials: HTTP Authorization credentials (optional)

    Returns:
        UUID or None: User ID if token is valid, None otherwise

    Example:
        @app.get("/api/public-tasks")
        def get_public_tasks(user_id: Optional[UUID] = Depends(get_current_user_optional)):
            if user_id:
                return {"message": "Authenticated user"}
            return {"message": "Anonymous user"}
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        user_id_str: Optional[str] = payload.get("sub")

        if user_id_str is None:
            return None

        return UUID(user_id_str)

    except (JWTError, ValueError):
        return None
