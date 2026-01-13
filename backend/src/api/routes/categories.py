"""
Categories API Routes
REST endpoints for category management
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...models.category import Category, CategoryCreate, CategoryRead, CategoryUpdate
from ...services.category_service import CategoryService
from ..deps import get_current_user, get_session

router = APIRouter()


def get_user_id(current_user: Any = Depends(get_current_user)) -> str:
    """
    Extract user ID from current_user as a String.
    """
    try:
        # 1. If dictionary (JWT Claims)
        if isinstance(current_user, dict):
            uid = (
                current_user.get("user_id")
                or current_user.get("sub")
                or current_user.get("id")
            )
            if uid:
                return str(uid)

        # 2. If Object (ORM Model)
        if hasattr(current_user, "user_id"):
            return str(current_user.user_id)
        if hasattr(current_user, "id"):
            return str(current_user.id)

        # 3. Fallback: Convert whatever it is to string
        return str(current_user)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not determine valid user ID",
        )


@router.get("/categories", response_model=List[CategoryRead])
async def list_categories(
    user_id: str = Depends(get_user_id),
    session: Session = Depends(get_session),
):
    """List all categories for the authenticated user."""
    service = CategoryService(session)
    return service.get_categories(user_id)


@router.post(
    "/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_data: CategoryCreate,
    user_id: str = Depends(get_user_id),
    session: Session = Depends(get_session),
):
    """Create a new category."""
    service = CategoryService(session)
    try:
        return service.create_category(user_id, category_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/categories/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int,
    user_id: str = Depends(get_user_id),
    session: Session = Depends(get_session),
):
    """Get a specific category by ID."""
    service = CategoryService(session)
    category = service.get_category_by_id(user_id, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found",
        )
    return category


@router.put("/categories/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    user_id: str = Depends(get_user_id),
    session: Session = Depends(get_session),
):
    """Update a category."""
    service = CategoryService(session)
    try:
        category = service.update_category(user_id, category_id, category_data)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {category_id} not found",
            )
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    user_id: str = Depends(get_user_id),
    session: Session = Depends(get_session),
):
    """Delete a category."""
    service = CategoryService(session)
    deleted = service.delete_category(user_id, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found",
        )


__all__ = ["router"]
