"""Service layer for task activity logging."""

from typing import List
from sqlmodel import Session, select
from fastapi import HTTPException

from ..models.task_activity import TaskActivity, TaskActivityRead
from ..models.task import Task


class ActivityLogService:
    """Service for logging and retrieving task activity history."""

    @staticmethod
    def log_activity(
        db: Session,
        task_id: int,
        user_id: str,
        action: str,
        field: str | None = None,
        old_value: str | None = None,
        new_value: str | None = None,
        description: str | None = None
    ) -> TaskActivity:
        """Log a task activity event.

        Args:
            db: Database session
            task_id: ID of task
            user_id: ID of user who performed action
            action: Action type (created, updated, completed, etc.)
            field: Field that changed (optional)
            old_value: Previous value (optional)
            new_value: New value (optional)
            description: Human-readable description (optional)

        Returns:
            Created activity record
        """
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action=action,
            field=field,
            old_value=old_value,
            new_value=new_value,
            description=description
        )

        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def get_task_activities(
        db: Session,
        task_id: int,
        user_id: str,
        limit: int = 50
    ) -> List[TaskActivityRead]:
        """Get activity history for a task.

        Args:
            db: Database session
            task_id: ID of task
            user_id: ID of user (for security check)
            limit: Maximum number of activities to return

        Returns:
            List of activities ordered by created_at desc

        Raises:
            HTTPException: If task not found or user doesn't own task
        """
        # Verify task exists and user owns it
        task = db.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found or you don't have permission"
            )

        # Get activities
        activities = db.exec(
            select(TaskActivity)
            .where(TaskActivity.task_id == task_id)
            .order_by(TaskActivity.created_at.desc())
            .limit(limit)
        ).all()

        return [TaskActivityRead.model_validate(act) for act in activities]
