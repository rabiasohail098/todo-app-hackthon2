"""Subtask service layer for business logic."""

from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime

from ..models.subtask import Subtask, SubtaskCreate, SubtaskUpdate


class SubtaskService:
    """
    Subtask service for handling subtask-related business logic.

    All methods enforce parent task ownership through user_id checks.
    """

    @staticmethod
    def create_subtask(
        session: Session, parent_task_id: int, subtask_data: SubtaskCreate
    ) -> Subtask:
        """
        Create a new subtask for a parent task.

        Args:
            session: Database session
            parent_task_id: ID of parent task
            subtask_data: Subtask creation data

        Returns:
            Created Subtask instance with id and timestamps populated
        """
        # Get next order number for this parent task
        statement = select(Subtask).where(Subtask.parent_task_id == parent_task_id)
        existing_subtasks = session.exec(statement).all()
        next_order = len(existing_subtasks)

        subtask = Subtask(
            parent_task_id=parent_task_id,
            title=subtask_data.title,
            is_completed=subtask_data.is_completed,
            order=subtask_data.order if subtask_data.order >= 0 else next_order,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add(subtask)
        session.commit()
        session.refresh(subtask)
        return subtask

    @staticmethod
    def get_subtasks_by_task(
        session: Session, parent_task_id: int
    ) -> List[Subtask]:
        """
        Get all subtasks for a parent task, ordered by display order.

        Args:
            session: Database session
            parent_task_id: ID of parent task

        Returns:
            List of Subtask instances ordered by 'order' field
        """
        statement = (
            select(Subtask)
            .where(Subtask.parent_task_id == parent_task_id)
            .order_by(Subtask.order.asc(), Subtask.created_at.asc())
        )
        subtasks = session.exec(statement).all()
        return list(subtasks)

    @staticmethod
    def get_subtask_by_id(
        session: Session, subtask_id: int
    ) -> Optional[Subtask]:
        """
        Get a specific subtask by ID.

        Args:
            session: Database session
            subtask_id: ID of the subtask

        Returns:
            Subtask instance if found, None otherwise
        """
        statement = select(Subtask).where(Subtask.id == subtask_id)
        subtask = session.exec(statement).first()
        return subtask

    @staticmethod
    def update_subtask(
        session: Session, subtask_id: int, subtask_data: SubtaskUpdate
    ) -> Optional[Subtask]:
        """
        Update a subtask.

        Args:
            session: Database session
            subtask_id: ID of the subtask to update
            subtask_data: SubtaskUpdate with optional fields

        Returns:
            Updated Subtask instance if found, None otherwise
        """
        subtask = SubtaskService.get_subtask_by_id(session, subtask_id)
        if not subtask:
            return None

        # Update only provided fields (PATCH semantics)
        if subtask_data.title is not None:
            subtask.title = subtask_data.title
        if subtask_data.is_completed is not None:
            subtask.is_completed = subtask_data.is_completed
        if subtask_data.order is not None:
            subtask.order = subtask_data.order

        # Update timestamp
        subtask.updated_at = datetime.utcnow()

        session.add(subtask)
        session.commit()
        session.refresh(subtask)
        return subtask

    @staticmethod
    def delete_subtask(session: Session, subtask_id: int) -> bool:
        """
        Delete a subtask.

        Args:
            session: Database session
            subtask_id: ID of the subtask to delete

        Returns:
            True if subtask was deleted, False if not found
        """
        subtask = SubtaskService.get_subtask_by_id(session, subtask_id)
        if not subtask:
            return False

        session.delete(subtask)
        session.commit()
        return True

    @staticmethod
    def calculate_progress(session: Session, parent_task_id: int) -> dict:
        """
        Calculate subtask completion progress for a parent task.

        Args:
            session: Database session
            parent_task_id: ID of parent task

        Returns:
            Dict with total, completed, and percentage
        """
        subtasks = SubtaskService.get_subtasks_by_task(session, parent_task_id)

        total = len(subtasks)
        if total == 0:
            return {"total": 0, "completed": 0, "percentage": 0}

        completed = sum(1 for s in subtasks if s.is_completed)
        percentage = int((completed / total) * 100) if total > 0 else 0

        return {
            "total": total,
            "completed": completed,
            "percentage": percentage
        }
