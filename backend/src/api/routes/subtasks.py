"""Subtask API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ...models.subtask import Subtask, SubtaskCreate, SubtaskUpdate, SubtaskRead
from ...models.task import Task
from ...services.subtask_service import SubtaskService
from ...services.task_service import TaskService
from ..deps import get_db, get_current_user

router = APIRouter()


@router.post(
    "/tasks/{task_id}/subtasks",
    response_model=SubtaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new subtask",
)
async def create_subtask(
    task_id: int,
    subtask_data: SubtaskCreate,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Subtask:
    """
    Create a new subtask for a parent task.

    Args:
        task_id: Parent task ID from path parameter
        subtask_data: SubtaskCreate with title, is_completed, order
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        Created Subtask with id, parent_task_id, timestamps populated

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies parent task ownership (404 if task not owned by user)
    """
    # Verify parent task exists and belongs to user
    task = TaskService.get_task_by_id(session, task_id, current_user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found or access denied",
        )

    subtask = SubtaskService.create_subtask(session, task_id, subtask_data)
    return subtask


@router.get(
    "/tasks/{task_id}/subtasks",
    response_model=List[SubtaskRead],
    summary="Get all subtasks for a task",
)
async def get_subtasks(
    task_id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> List[Subtask]:
    """
    Get all subtasks for a parent task.

    Args:
        task_id: Parent task ID from path parameter
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        List of Subtask instances ordered by display order

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies parent task ownership (404 if task not owned by user)
    """
    # Verify parent task exists and belongs to user
    task = TaskService.get_task_by_id(session, task_id, current_user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found or access denied",
        )

    subtasks = SubtaskService.get_subtasks_by_task(session, task_id)
    return subtasks


@router.get(
    "/tasks/{task_id}/subtasks/progress",
    summary="Get subtask completion progress",
)
async def get_subtask_progress(
    task_id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict:
    """
    Get subtask completion progress for a parent task.

    Args:
        task_id: Parent task ID from path parameter
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        Dict with total, completed, and percentage

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies parent task ownership (404 if task not owned by user)
    """
    # Verify parent task exists and belongs to user
    task = TaskService.get_task_by_id(session, task_id, current_user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found or access denied",
        )

    progress = SubtaskService.calculate_progress(session, task_id)
    return progress


@router.patch(
    "/subtasks/{subtask_id}",
    response_model=SubtaskRead,
    summary="Update a subtask",
)
async def update_subtask(
    subtask_id: int,
    subtask_data: SubtaskUpdate,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Subtask:
    """
    Update a subtask's title, completion status, or order.

    Args:
        subtask_id: Subtask ID from path parameter
        subtask_data: SubtaskUpdate with optional fields
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        Updated Subtask instance

    Raises:
        404: Subtask not found or parent task not owned by user

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies parent task ownership before updating
    """
    # Get subtask
    subtask = SubtaskService.get_subtask_by_id(session, subtask_id)
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtask with id {subtask_id} not found",
        )

    # Verify parent task belongs to user
    task = TaskService.get_task_by_id(session, subtask.parent_task_id, current_user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent task not found or access denied",
        )

    updated_subtask = SubtaskService.update_subtask(session, subtask_id, subtask_data)
    if not updated_subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtask with id {subtask_id} not found",
        )

    return updated_subtask


@router.delete(
    "/subtasks/{subtask_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a subtask",
)
async def delete_subtask(
    subtask_id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    """
    Permanently delete a subtask.

    Args:
        subtask_id: Subtask ID from path parameter
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        204 No Content on success

    Raises:
        404: Subtask not found or parent task not owned by user

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies parent task ownership before deletion
    """
    # Get subtask
    subtask = SubtaskService.get_subtask_by_id(session, subtask_id)
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtask with id {subtask_id} not found",
        )

    # Verify parent task belongs to user
    task = TaskService.get_task_by_id(session, subtask.parent_task_id, current_user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent task not found or access denied",
        )

    success = SubtaskService.delete_subtask(session, subtask_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtask with id {subtask_id} not found",
        )
    # FastAPI automatically returns 204 when return type is None
