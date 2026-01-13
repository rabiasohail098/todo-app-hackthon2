"""Tag model for task tagging."""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class TagBase(SQLModel):
    """Base schema for Tag with common fields."""

    name: str = Field(
        max_length=50,
        description="Tag name (e.g., 'urgent', 'meeting', 'work')"
    )


class Tag(TagBase, table=True):
    """
    Database model for Tag entity.

    Represents a reusable label that users can attach to tasks for flexible organization.
    Tags are user-specific and can be applied to multiple tasks.
    """

    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        max_length=255,
        nullable=False,
        description="UUID of the user who created this tag"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when tag was created"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "urgent",
                "created_at": "2025-01-01T12:00:00Z"
            }
        }


class TagCreate(TagBase):
    """Schema for creating a new tag."""

    class Config:
        json_schema_extra = {
            "example": {
                "name": "urgent"
            }
        }


class TagRead(TagBase):
    """Schema for reading tag data (response model)."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "urgent",
                "created_at": "2025-01-01T12:00:00Z"
            }
        }
