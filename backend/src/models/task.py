"""Task model for todo application."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel, Field


class TaskBase(SQLModel):
    """Base model for Task - shared fields for create/update."""

    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    is_completed: bool = Field(default=False, nullable=False)


class Task(TaskBase, table=True):
    """Database model for Task entity.

    Attributes:
        id: Auto-incrementing primary key
        user_id: Foreign key to User (UUID), indexed for performance
        title: Task title, max 200 characters
        description: Optional task description
        is_completed: Task completion status, defaults to False
        created_at: Timestamp when task was created
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class TaskCreate(TaskBase):
    """Schema for creating a task.

    Note: user_id is assigned by server from JWT, not from request body.
    """
    pass


class TaskUpdate(SQLModel):
    """Schema for updating a task.

    All fields are optional for PATCH semantics.
    """

    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    is_completed: Optional[bool] = None


class TaskRead(TaskBase):
    """Schema for reading a task.

    Includes all server-assigned fields.
    """

    id: int
    user_id: UUID
    created_at: datetime
