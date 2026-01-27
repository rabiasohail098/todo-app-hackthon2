"""Task service layer for business logic."""

from typing import List, Optional, Dict, Any
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
        session: Session, task_data: TaskCreate, user_id: str
    ) -> Task:
        """
        Create a new task for a user.

        Args:
            session: Database session
            task_data: Task creation data (title, description, is_completed, priority, due_date, category_id, etc.)
            user_id: UUID of the authenticated user (from JWT)

        Returns:
            Created Task instance with id and created_at populated

        Security:
            user_id is ALWAYS from JWT token, never from request body
        """
        # Phase 4: Include all new fields from TaskCreate
        # Note: Use .value for enums to ensure lowercase values match database constraints
        task = Task(
            title=task_data.title,
            description=task_data.description,
            is_completed=task_data.is_completed,
            priority=task_data.priority.value if task_data.priority else "medium",
            due_date=task_data.due_date,
            notes=task_data.notes,
            category_id=task_data.category_id,
            recurrence_pattern=task_data.recurrence_pattern.value if task_data.recurrence_pattern else None,
            recurrence_interval=task_data.recurrence_interval,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Phase 4: Set next_recurrence_date if recurring
        if task.recurrence_pattern:
            from ..utils.recurrence import calculate_next_occurrence
            task.next_recurrence_date = calculate_next_occurrence(
                datetime.utcnow(),
                task.recurrence_pattern,
                task.recurrence_interval
            )

        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get_tasks_by_user(
        session: Session,
        user_id: str,
        category_id: Optional[int] = None,
        priority: Optional[str] = None,
        is_completed: Optional[bool] = None,
        due_date_filter: Optional[str] = None,
        sort_by: Optional[str] = None,
        search_query: Optional[str] = None,
        tag_ids: Optional[List[int]] = None,
    ) -> List[Task]:
        """
        Get all tasks for a user with optional filters and sorting.

        Args:
            session: Database session
            user_id: UUID of the authenticated user
            category_id: Optional filter by category ID
            priority: Optional filter by priority (critical, high, medium, low)
            is_completed: Optional filter by completion status
            due_date_filter: Optional date filter (today, this_week, overdue, has_due_date, no_due_date)
            sort_by: Optional sorting (priority_asc, priority_desc, due_date_asc, due_date_desc, created_at_desc)
            search_query: Optional keyword search in title, description, and notes
            tag_ids: Optional filter by tag IDs (tasks must have at least one of these tags)

        Returns:
            List of Task instances belonging to the user

        Security:
            GOLDEN RULE: Always filter by user_id to enforce isolation
        """
        from datetime import datetime, timedelta
        from sqlalchemy import func, text
        from ..models.task_tag import TaskTag

        statement = select(Task).where(Task.user_id == user_id)

        # Phase 4: Apply optional filters
        if category_id is not None:
            statement = statement.where(Task.category_id == category_id)
        if priority is not None:
            statement = statement.where(Task.priority == priority)
        if is_completed is not None:
            statement = statement.where(Task.is_completed == is_completed)

        # Phase 4: US3 - Due date filters
        if due_date_filter:
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            week_end = today_start + timedelta(days=7)

            if due_date_filter == "today":
                statement = statement.where(
                    Task.due_date >= today_start,
                    Task.due_date < today_end
                )
            elif due_date_filter == "this_week":
                statement = statement.where(
                    Task.due_date >= today_start,
                    Task.due_date < week_end
                )
            elif due_date_filter == "overdue":
                statement = statement.where(
                    Task.due_date < now,
                    Task.is_completed == False
                )
            elif due_date_filter == "has_due_date":
                statement = statement.where(Task.due_date.isnot(None))
            elif due_date_filter == "no_due_date":
                statement = statement.where(Task.due_date.is_(None))

        # Phase 4: US4 - Full-text search
        if search_query:
            # Convert search query to tsquery format
            # Use plainto_tsquery for user-friendly search (handles phrases, ignores operators)
            search_ts = func.plainto_tsquery('english', search_query)
            statement = statement.where(
                text("search_vector @@ plainto_tsquery('english', :query)")
            ).params(query=search_query)

        # Phase 4: US7 - Tag filtering
        if tag_ids:
            # Filter tasks that have at least one of the specified tags
            statement = statement.join(TaskTag, Task.id == TaskTag.task_id).where(
                TaskTag.tag_id.in_(tag_ids)
            ).distinct()

        # Phase 4: Apply sorting
        if sort_by == "priority_desc":
            # Critical > High > Medium > Low
            priority_order = Task.priority.case(
                {"critical": 1, "high": 2, "medium": 3, "low": 4},
                else_=5
            )
            statement = statement.order_by(priority_order.asc(), Task.created_at.desc())
        elif sort_by == "priority_asc":
            # Low > Medium > High > Critical
            priority_order = Task.priority.case(
                {"low": 1, "medium": 2, "high": 3, "critical": 4},
                else_=5
            )
            statement = statement.order_by(priority_order.asc(), Task.created_at.desc())
        elif sort_by == "due_date_asc":
            # Earliest due date first, nulls last
            statement = statement.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
        elif sort_by == "due_date_desc":
            # Latest due date first, nulls last
            statement = statement.order_by(Task.due_date.desc().nullslast(), Task.created_at.desc())
        else:
            # Default: newest first
            statement = statement.order_by(Task.created_at.desc())

        tasks = session.exec(statement).all()
        return list(tasks)

    @staticmethod
    def get_task_by_id(
        session: Session, task_id: int, user_id: str
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
        session: Session, task_id: int, user_id: str, task_data: TaskUpdate
    ) -> Optional[Task]:
        """
        Update a task if it belongs to the user.

        Args:
            session: Database session
            task_id: ID of the task to update
            user_id: UUID of the authenticated user
            task_data: TaskUpdate with optional fields (all Phase 4 fields supported)

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

        # Phase 4: Update new fields
        # Note: Use .value for enums to ensure lowercase values match database constraints
        if task_data.priority is not None:
            task.priority = task_data.priority.value if hasattr(task_data.priority, 'value') else task_data.priority
        if task_data.due_date is not None:
            task.due_date = task_data.due_date
        if task_data.notes is not None:
            task.notes = task_data.notes
        if task_data.category_id is not None:
            task.category_id = task_data.category_id
        if task_data.recurrence_pattern is not None:
            pattern_value = task_data.recurrence_pattern.value if hasattr(task_data.recurrence_pattern, 'value') else task_data.recurrence_pattern
            task.recurrence_pattern = pattern_value
            # Recalculate next_recurrence_date if pattern changed
            if task.recurrence_pattern:
                from ..utils.recurrence import calculate_next_occurrence
                task.next_recurrence_date = calculate_next_occurrence(
                    datetime.utcnow(),
                    task_data.recurrence_pattern,
                    task.recurrence_interval
                )
        if task_data.recurrence_interval is not None:
            task.recurrence_interval = task_data.recurrence_interval

        # Update timestamp
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def delete_task(session: Session, task_id: int, user_id: str) -> bool:
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

    @staticmethod
    def get_task_with_progress(
        session: Session, task_id: int, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a task with subtask progress information.

        Args:
            session: Database session
            task_id: ID of the task
            user_id: UUID of the authenticated user

        Returns:
            Dict with task data and subtask_progress {total, completed, percentage}
            None if task not found or not owned by user
        """
        task = TaskService.get_task_by_id(session, task_id, user_id)
        if not task:
            return None

        # Import here to avoid circular dependency
        from .subtask_service import SubtaskService

        progress = SubtaskService.calculate_progress(session, task_id)

        return {
            "task": task,
            "subtask_progress": progress
        }
