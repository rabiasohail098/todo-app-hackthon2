"""
Category model for organizing tasks
Phase 4: Intermediate Features - User Story 1
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class CategoryBase(SQLModel):
    """Base model for Category - shared fields for create/update."""

    name: str = Field(max_length=50, nullable=False)
    color: str = Field(max_length=7, default="#8B5CF6")  # Hex color
    icon: Optional[str] = Field(max_length=10, default="📁")  # Emoji


class Category(CategoryBase, table=True):
    """Database model for Category entity.

    Attributes:
        id: Auto-incrementing primary key
        user_id: Foreign key to User (string), indexed for performance
        name: Category name, max 50 characters, unique per user
        color: Hex color code for visual indicator (#8B5CF6 = purple)
        icon: Emoji icon for category display
        created_at: Timestamp when category was created
        updated_at: Timestamp when category was last updated
    """

    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    # tasks: List["Task"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    """Schema for creating a category.

    Note: user_id is assigned by server from JWT, not from request body.
    """
    pass


class CategoryUpdate(SQLModel):
    """Schema for updating a category.

    All fields are optional for PATCH semantics.
    """

    name: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)
    icon: Optional[str] = Field(default=None, max_length=10)


class CategoryRead(CategoryBase):
    """Schema for reading a category.

    Includes all server-assigned fields.
    """

    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime


# Export all schemas
__all__ = ["Category", "CategoryCreate", "CategoryUpdate", "CategoryRead"]
