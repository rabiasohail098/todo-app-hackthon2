"""Subtask model for task breakdown."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class SubtaskBase(SQLModel):
    """Base model for Subtask - shared fields for create/update."""

    title: str = Field(max_length=200, nullable=False)
    is_completed: bool = Field(default=False, nullable=False)
    order: int = Field(default=0, nullable=False)


class Subtask(SubtaskBase, table=True):
    """Database model for Subtask entity.

    Attributes:
        id: Auto-incrementing primary key
        parent_task_id: Foreign key to parent Task
        title: Subtask title, max 200 characters
        is_completed: Subtask completion status
        order: Display order within parent task
        created_at: Timestamp when subtask was created
        updated_at: Timestamp when subtask was last updated
    """

    __tablename__ = "subtasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_task_id: int = Field(foreign_key="tasks.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class SubtaskCreate(SubtaskBase):
    """Schema for creating a subtask.

    Note: parent_task_id is provided via URL path parameter.
    """
    pass


class SubtaskUpdate(SQLModel):
    """Schema for updating a subtask.

    All fields are optional for PATCH semantics.
    """

    title: Optional[str] = Field(default=None, max_length=200)
    is_completed: Optional[bool] = None
    order: Optional[int] = None


class SubtaskRead(SubtaskBase):
    """Schema for reading a subtask.

    Includes all server-assigned fields.
    """

    id: int
    parent_task_id: int
    created_at: datetime
    updated_at: datetime
