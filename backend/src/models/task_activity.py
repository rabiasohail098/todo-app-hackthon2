"""TaskActivity model for audit logging task changes."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class TaskActivityBase(SQLModel):
    """Base model for TaskActivity - shared fields."""

    action: str = Field(max_length=50, nullable=False)  # created, updated, completed, deleted, etc.
    field: Optional[str] = Field(default=None, max_length=50)  # Which field changed (title, priority, etc.)
    old_value: Optional[str] = Field(default=None, max_length=500)  # Previous value
    new_value: Optional[str] = Field(default=None, max_length=500)  # New value
    description: Optional[str] = Field(default=None, max_length=500)  # Human-readable description


class TaskActivity(TaskActivityBase, table=True):
    """Database model for TaskActivity entity.

    Attributes:
        id: Auto-incrementing primary key
        task_id: Foreign key to Task
        user_id: Foreign key to User (who made the change)
        action: Type of action (created, updated, completed, deleted, etc.)
        field: Field that was changed (optional, for updates)
        old_value: Previous value (optional)
        new_value: New value (optional)
        description: Human-readable description of the change
        created_at: Timestamp when action occurred
    """

    __tablename__ = "task_activities"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", nullable=False, index=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class TaskActivityRead(TaskActivityBase):
    """Schema for reading task activity."""

    id: int
    task_id: int
    user_id: str
    created_at: datetime
