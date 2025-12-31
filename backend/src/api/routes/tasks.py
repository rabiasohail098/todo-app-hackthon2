"""Task API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ...models.task import Task, TaskCreate, TaskUpdate, TaskRead
from ...services.task_service import TaskService
from ..deps import get_db, get_current_user

router = APIRouter()


@router.post(
    "/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Task:
    """
    Create a new task for the authenticated user.

    Args:
        task_data: TaskCreate with title (required), description (optional), is_completed (default False)
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        Created Task with id, user_id, created_at populated

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - user_id is ALWAYS from JWT, never from request body
    """
    task = TaskService.create_task(session, task_data, current_user_id)
    return task


@router.get(
    "/tasks",
    response_model=List[TaskRead],
    summary="Get all tasks for current user",
)
async def get_tasks(
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> List[Task]:
    """
    Get all tasks for the authenticated user, ordered by created_at DESC.

    Args:
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        List of Task instances (may be empty)

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - GOLDEN RULE: Only returns tasks where user_id matches JWT
    """
    tasks = TaskService.get_tasks_by_user(session, current_user_id)
    return tasks


@router.get(
    "/tasks/{task_id}",
    response_model=TaskRead,
    summary="Get a specific task",
)
async def get_task(
    task_id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Task:
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID from path parameter
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        Task instance

    Raises:
        404: Task not found
        403: Task belongs to a different user

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Returns 403 Forbidden if task exists but belongs to another user
    """
    task = TaskService.get_task_by_id(session, task_id, current_user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found or access denied",
        )
    return task


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Task:
    """
    Update a task's title, description, or completion status.

    Args:
        task_id: Task ID from path parameter
        task_data: TaskUpdate with optional fields (title, description, is_completed)
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        Updated Task instance

    Raises:
        404: Task not found
        403: Task belongs to a different user

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies task ownership before updating
    """
    task = TaskService.update_task(session, task_id, current_user_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found or access denied",
        )
    return task


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
async def delete_task(
    task_id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    """
    Permanently delete a task.

    Args:
        task_id: Task ID from path parameter
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        204 No Content on success

    Raises:
        404: Task not found
        403: Task belongs to a different user

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies task ownership before deletion
    """
    success = TaskService.delete_task(session, task_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found or access denied",
        )
    # FastAPI automatically returns 204 when return type is None
