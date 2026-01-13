"""Task model for todo application."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from .enums import TaskPriority, RecurrencePattern


class TaskBase(SQLModel):
    """Base model for Task - shared fields for create/update."""

    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    is_completed: bool = Field(default=False, nullable=False)

    # Phase 4: Intermediate Features
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, nullable=False)
    due_date: Optional[datetime] = Field(default=None, nullable=True)
    notes: Optional[str] = Field(default=None, nullable=True)  # Markdown notes


class Task(TaskBase, table=True):
    """Database model for Task entity.

    Attributes:
        id: Auto-incrementing primary key
        user_id: Foreign key to User (string), indexed for performance
        title: Task title, max 200 characters
        description: Optional task description
        is_completed: Task completion status, defaults to False
        created_at: Timestamp when task was created
        priority: Task priority level (critical, high, medium, low)
        due_date: Optional due date for the task
        category_id: Optional foreign key to Category
        recurrence_pattern: Optional recurrence pattern (daily, weekly, monthly, custom)
        recurrence_interval: How often to recur (e.g., every 2 weeks)
        next_recurrence_date: When to create next occurrence
        parent_recurrence_id: Link to original recurring task
        notes: Optional markdown notes
    """

    __tablename__ = "tasks"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Phase 4: Database-only fields
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id", nullable=True)
    recurrence_pattern: Optional[RecurrencePattern] = Field(default=None, nullable=True)
    recurrence_interval: int = Field(default=1, nullable=False)
    next_recurrence_date: Optional[datetime] = Field(default=None, nullable=True)
    parent_recurrence_id: Optional[int] = Field(default=None, foreign_key="tasks.id", nullable=True)


class TaskCreate(TaskBase):
    """Schema for creating a task.

    Note: user_id is assigned by server from JWT, not from request body.
    Includes all fields from TaskBase plus optional category and recurrence.
    """
    category_id: Optional[int] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: int = 1


class TaskUpdate(SQLModel):
    """Schema for updating a task.

    All fields are optional for PATCH semantics.
    """

    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    is_completed: Optional[bool] = None

    # Phase 4: Intermediate Features
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    category_id: Optional[int] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: Optional[int] = None


class TaskRead(TaskBase):
    """Schema for reading a task.

    Includes all server-assigned fields and Phase 4 additions.
    """

    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    # Phase 4: Additional fields
    category_id: Optional[int] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: int = 1
    next_recurrence_date: Optional[datetime] = None
    parent_recurrence_id: Optional[int] = None
