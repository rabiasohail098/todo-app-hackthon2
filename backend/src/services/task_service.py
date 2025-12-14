"""Task service layer for business logic."""

from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime

from ..models.task import Task, TaskCreate, TaskUpdate


class TaskService:
    """
    Task service for handling task-related business logic.

    All methods enforce user isolation - tasks are always filtered by user_id.
    """

    @staticmethod
    def create_task(
        session: Session, task_data: TaskCreate, user_id: UUID
    ) -> Task:
        """
        Create a new task for a user.

        Args:
            session: Database session
            task_data: Task creation data (title, description, is_completed)
            user_id: UUID of the authenticated user (from JWT)

        Returns:
            Created Task instance with id and created_at populated

        Security:
            user_id is ALWAYS from JWT token, never from request body
        """
        task = Task(
            title=task_data.title,
            description=task_data.description,
            is_completed=task_data.is_completed,
            user_id=user_id,
            created_at=datetime.utcnow(),
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get_tasks_by_user(session: Session, user_id: UUID) -> List[Task]:
        """
        Get all tasks for a user, ordered by created_at DESC.

        Args:
            session: Database session
            user_id: UUID of the authenticated user

        Returns:
            List of Task instances belonging to the user

        Security:
            GOLDEN RULE: Always filter by user_id to enforce isolation
        """
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        tasks = session.exec(statement).all()
        return list(tasks)

    @staticmethod
    def get_task_by_id(
        session: Session, task_id: int, user_id: UUID
    ) -> Optional[Task]:
        """
        Get a specific task by ID if it belongs to the user.

        Args:
            session: Database session
            task_id: ID of the task
            user_id: UUID of the authenticated user

        Returns:
            Task instance if found and belongs to user, None otherwise

        Security:
            GOLDEN RULE: Always verify task ownership with user_id filter
        """
        statement = select(Task).where(
            Task.id == task_id, Task.user_id == user_id
        )
        task = session.exec(statement).first()
        return task

    @staticmethod
    def update_task(
        session: Session, task_id: int, user_id: UUID, task_data: TaskUpdate
    ) -> Optional[Task]:
        """
        Update a task if it belongs to the user.

        Args:
            session: Database session
            task_id: ID of the task to update
            user_id: UUID of the authenticated user
            task_data: TaskUpdate with optional fields (title, description, is_completed)

        Returns:
            Updated Task instance if found and belongs to user, None otherwise

        Security:
            GOLDEN RULE: Verify ownership before updating
        """
        task = TaskService.get_task_by_id(session, task_id, user_id)
        if not task:
            return None

        # Update only provided fields (PATCH semantics)
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.is_completed is not None:
            task.is_completed = task_data.is_completed

        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def delete_task(session: Session, task_id: int, user_id: UUID) -> bool:
        """
        Delete a task if it belongs to the user.

        Args:
            session: Database session
            task_id: ID of the task to delete
            user_id: UUID of the authenticated user

        Returns:
            True if task was deleted, False if not found or not owned by user

        Security:
            GOLDEN RULE: Verify ownership before deletion
        """
        task = TaskService.get_task_by_id(session, task_id, user_id)
        if not task:
            return False

        session.delete(task)
        session.commit()
        return True
