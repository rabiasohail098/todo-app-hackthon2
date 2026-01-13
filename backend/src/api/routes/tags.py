"""Tag API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from ...models.tag import Tag, TagCreate, TagRead
from ...models.task import Task as TaskModel
from ...services.tag_service import TagService
from ...services.task_service import TaskService
from ..deps import get_db, get_current_user

router = APIRouter()


@router.get(
    "/tags",
    response_model=List[TagRead],
    summary="Get all tags for user",
)
async def get_tags(
    search: Optional[str] = Query(None, description="Search tags by name"),
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> List[Tag]:
    """
    Get all tags for the authenticated user with optional search.

    Args:
        search: Optional search string for tag name
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        List of Tag instances belonging to the user

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Tags filtered by user_id for isolation
    """
    tags = TagService.get_tags_by_user(session, current_user_id, search)
    return tags


@router.post(
    "/tags",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tag",
)
async def create_tag(
    tag_data: TagCreate,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Tag:
    """
    Create a new tag for the authenticated user.

    If a tag with the same name already exists for this user, returns the existing tag.

    Args:
        tag_data: TagCreate with name
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        Created or existing Tag instance

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - user_id is ALWAYS from JWT token
    """
    tag = TagService.create_tag(session, tag_data, current_user_id)
    return tag


@router.delete(
    "/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a tag",
)
async def delete_tag(
    tag_id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    """
    Permanently delete a tag and all its task associations.

    Args:
        tag_id: ID of the tag to delete
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        204 No Content on success

    Raises:
        404: Tag not found or not owned by user

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies tag ownership before deletion
    """
    success = TagService.delete_tag(session, tag_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found or access denied",
        )
    # FastAPI automatically returns 204 when return type is None


@router.get(
    "/tags/popular",
    summary="Get most frequently used tags",
)
async def get_popular_tags(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of tags to return"),
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> List[dict]:
    """
    Get most frequently used tags for the authenticated user.

    Args:
        limit: Maximum number of tags to return (1-50, default 10)
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        List of dicts with tag info and usage count

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Tags filtered by user_id for isolation
    """
    popular_tags = TagService.get_popular_tags(session, current_user_id, limit)
    return popular_tags


@router.post(
    "/tasks/{task_id}/tags/{tag_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Add tag to task",
)
async def add_tag_to_task(
    task_id: int,
    tag_id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict:
    """
    Add a tag to a task.

    Args:
        task_id: ID of the task
        tag_id: ID of the tag
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        Success message

    Raises:
        404: Task or tag not found or not owned by user

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies both task and tag ownership
    """
    # Verify task ownership
    task = TaskService.get_task_by_id(session, task_id, current_user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found or access denied",
        )

    # Verify tag ownership
    tag = TagService.get_tag_by_id(session, tag_id, current_user_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found or access denied",
        )

    # Add tag to task
    TagService.add_tag_to_task(session, task_id, tag_id)

    return {"message": "Tag added to task successfully"}


@router.delete(
    "/tasks/{task_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove tag from task",
)
async def remove_tag_from_task(
    task_id: int,
    tag_id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    """
    Remove a tag from a task.

    Args:
        task_id: ID of the task
        tag_id: ID of the tag
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        204 No Content on success

    Raises:
        404: Task, tag, or association not found

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies both task and tag ownership
    """
    # Verify task ownership
    task = TaskService.get_task_by_id(session, task_id, current_user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found or access denied",
        )

    # Verify tag ownership
    tag = TagService.get_tag_by_id(session, tag_id, current_user_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found or access denied",
        )

    # Remove tag from task
    success = TagService.remove_tag_from_task(session, task_id, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag association not found",
        )
    # FastAPI automatically returns 204 when return type is None


@router.get(
    "/tasks/{task_id}/tags",
    response_model=List[TagRead],
    summary="Get all tags for a task",
)
async def get_task_tags(
    task_id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> List[Tag]:
    """
    Get all tags associated with a task.

    Args:
        task_id: ID of the task
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        List of Tag instances

    Raises:
        404: Task not found or not owned by user

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies task ownership
    """
    # Verify task ownership
    task = TaskService.get_task_by_id(session, task_id, current_user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found or access denied",
        )

    tags = TagService.get_tags_for_task(session, task_id)
    return tags
