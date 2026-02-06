"""FastAPI dependencies for database and authentication."""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from jose import JWTError, jwt
import os
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
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """Get current user from JWT token with X-User-Id header fallback.

    This dependency first tries to extract and validate the JWT token from the
    Authorization header, then falls back to X-User-Id header if present.
    Returns the user_id.

    Args:
        request: FastAPI request object to access headers
        credentials: HTTP Authorization credentials from Bearer token (optional)

    Returns:
        str: User ID extracted from JWT token or X-User-Id header

    Raises:
        HTTPException: 401 if no valid token or header is present

    Example:
        @app.get("/api/tasks")
        def get_tasks(user_id: str = Depends(get_current_user)):
            return {"user_id": user_id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # First, try to get user ID from Authorization header JWT
    if credentials:
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
            user_id: Optional[str] = payload.get("sub")

            if user_id is not None:
                return user_id

        except JWTError:
            # JWT was provided but is invalid, so raise exception
            raise credentials_exception

    # If no valid JWT or no JWT provided, try X-User-Id header fallback
    user_id_from_header = request.headers.get("x-user-id")
    if user_id_from_header:
        return user_id_from_header

    # No authentication method worked
    raise credentials_exception


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[str]:
    """Get current user from JWT token if present with X-User-Id header fallback (optional).

    This dependency is similar to get_current_user but doesn't raise
    an exception if no token is provided. Useful for endpoints that
    can work with or without authentication.

    Args:
        request: FastAPI request object to access headers
        credentials: HTTP Authorization credentials (optional)

    Returns:
        str or None: User ID if token is valid, None otherwise

    Example:
        @app.get("/api/public-tasks")
        def get_public_tasks(user_id: Optional[str] = Depends(get_current_user_optional)):
            if user_id:
                return {"message": "Authenticated user"}
            return {"message": "Anonymous user"}
    """
    # First, try to get user ID from Authorization header JWT
    if credentials:
        try:
            token = credentials.credentials
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )
            user_id: Optional[str] = payload.get("sub")

            if user_id is not None:
                return user_id

        except JWTError:
            # JWT was provided but is invalid, continue to try header fallback
            pass

    # If no valid JWT or no JWT provided, try X-User-Id header fallback
    user_id_from_header = request.headers.get("x-user-id")
    if user_id_from_header:
        return user_id_from_header

    # No authentication method worked
    return None
