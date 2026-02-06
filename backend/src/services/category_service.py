"""
CategoryService - Phase 4: User Story 1
Handles CRUD operations for task categories with user isolation
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.category import Category, CategoryCreate, CategoryUpdate


class CategoryService:
    """Service for managing task categories."""

    def __init__(self, session: Session):
        """Initialize service with database session."""
        self.session = session

    def create_category(
        self, user_id: str, category_data: CategoryCreate
    ) -> Category:
        """
        Create a new category for the user.

        Args:
            user_id: User's unique identifier
            category_data: Category creation data

        Returns:
            Created Category object

        Raises:
            IntegrityError: If category name already exists for user
        """
        category = Category(
            user_id=user_id,
            name=category_data.name,
            color=category_data.color,
            icon=category_data.icon,
        )

        self.session.add(category)

        try:
            self.session.commit()
            self.session.refresh(category)
            return category
        except IntegrityError:
            self.session.rollback()
            raise ValueError(f"Category '{category_data.name}' already exists")

    def get_categories(self, user_id: str) -> List[Category]:
        """
        Get all categories for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of Category objects
        """
        return (
            self.session.query(Category)
            .filter(Category.user_id == user_id)
            .order_by(Category.name)
            .all()
        )

    def get_category_by_id(
        self, user_id: str, category_id: int
    ) -> Optional[Category]:
        """
        Get a specific category by ID (user-scoped).

        Args:
            user_id: User's unique identifier
            category_id: Category ID

        Returns:
            Category object or None if not found
        """
        return (
            self.session.query(Category)
            .filter(Category.user_id == user_id, Category.id == category_id)
            .first()
        )

    def get_category_by_name(
        self, user_id: str, category_name: str
    ) -> Optional[Category]:
        """
        Get a category by name (user-scoped).

        Args:
            user_id: User's unique identifier
            category_name: Category name

        Returns:
            Category object or None if not found
        """
        return (
            self.session.query(Category)
            .filter(
                Category.user_id == user_id,
                Category.name.ilike(category_name)  # Case-insensitive
            )
            .first()
        )

    def update_category(
        self, user_id: str, category_id: int, category_data: CategoryUpdate
    ) -> Optional[Category]:
        """
        Update a category.

        Args:
            user_id: User's unique identifier
            category_id: Category ID to update
            category_data: Updated category data

        Returns:
            Updated Category object or None if not found
        """
        category = self.get_category_by_id(user_id, category_id)

        if not category:
            return None

        # Update only provided fields
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        try:
            self.session.commit()
            self.session.refresh(category)
            return category
        except IntegrityError:
            self.session.rollback()
            raise ValueError(f"Category name '{category_data.name}' already exists")

    def delete_category(self, user_id: str, category_id: int) -> bool:
        """
        Delete a category.

        Note: Tasks linked to this category will have category_id set to NULL
        (due to ON DELETE SET NULL constraint).

        Args:
            user_id: User's unique identifier
            category_id: Category ID to delete

        Returns:
            True if deleted, False if not found
        """
        category = self.get_category_by_id(user_id, category_id)

        if not category:
            return False

        self.session.delete(category)
        self.session.commit()
        return True

    def create_or_get_category(
        self, user_id: str, category_name: str, color: str = "#8B5CF6", icon: str = "📁"
    ) -> Category:
        """
        Get existing category by name or create new one.

        Useful for chatbot auto-creation of categories.

        Args:
            user_id: User's unique identifier
            category_name: Category name
            color: Category color (default: purple)
            icon: Category icon (default: folder)

        Returns:
            Existing or newly created Category
        """
        # Try to get existing category
        existing = self.get_category_by_name(user_id, category_name)

        if existing:
            return existing

        # Create new category
        category_data = CategoryCreate(name=category_name, color=color, icon=icon)
        return self.create_category(user_id, category_data)


# Export service
__all__ = ["CategoryService"]
