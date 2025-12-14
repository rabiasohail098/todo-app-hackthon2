"""User model for authentication."""

from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4


class UserBase(SQLModel):
    """Base user fields."""
    email: str = Field(unique=True, index=True, max_length=255)


class User(UserBase, table=True):
    """
    User entity stored in database.

    Represents a user account with email and password.
    """
    __tablename__ = "users"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(SQLModel):
    """User creation request."""
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)


class UserLogin(SQLModel):
    """User login request."""
    email: str = Field(max_length=255)
    password: str


class UserRead(UserBase):
    """User response (excludes password_hash)."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class TokenResponse(SQLModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserRead
