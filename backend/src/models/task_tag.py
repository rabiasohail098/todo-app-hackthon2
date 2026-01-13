"""TaskTag join model for many-to-many relationship between tasks and tags."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class TaskTag(SQLModel, table=True):
    """
    Join table for many-to-many relationship between Task and Tag.

    A task can have multiple tags, and a tag can be applied to multiple tasks.
    This model represents the association between them.
    """

    __tablename__ = "task_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(
        foreign_key="tasks.id",
        nullable=False,
        description="ID of the task"
    )
    tag_id: int = Field(
        foreign_key="tags.id",
        nullable=False,
        description="ID of the tag"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when tag was added to task"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "task_id": 123,
                "tag_id": 5,
                "created_at": "2025-01-01T12:00:00Z"
            }
        }
