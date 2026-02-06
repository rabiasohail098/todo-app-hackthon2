"""API routes for task activity logs."""

from typing import List
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session

from ..deps import get_db, get_current_user
from ...services.activity_log_service import ActivityLogService
from ...models.task_activity import TaskActivityRead

router = APIRouter(prefix="/api/tasks", tags=["activity"])


@router.get("/{task_id}/activity", response_model=List[TaskActivityRead])
def get_task_activity(
    request: Request,
    task_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity history for a task.

    Args:
        task_id: ID of task
        limit: Maximum number of activities to return (1-100, default 50)
        current_user: User ID from JWT token
        db: Database session

    Returns:
        List of activities ordered by created_at desc

    Raises:
        404: Task not found or user doesn't own task
    """
    return ActivityLogService.get_task_activities(
        db=db,
        task_id=task_id,
        user_id=current_user,
        limit=limit
    )
