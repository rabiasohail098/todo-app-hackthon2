"""Statistics service layer for calculating task analytics."""

from typing import Dict, Any, List, Optional
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from collections import defaultdict

from ..models.task import Task


class StatisticsService:
    """
    Statistics service for calculating task-related metrics and analytics.

    All methods enforce user isolation - statistics are always filtered by user_id.
    """

    @staticmethod
    def get_overall_statistics(
        session: Session,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get overall task statistics for a user within a date range.

        Args:
            session: Database session
            user_id: UUID of the authenticated user
            start_date: Optional start date for filtering (default: 30 days ago)
            end_date: Optional end date for filtering (default: now)

        Returns:
            Dict with statistics including:
            - total_tasks: Total number of tasks
            - completed_tasks: Number of completed tasks
            - pending_tasks: Number of pending tasks
            - completion_rate: Percentage of completed tasks
            - overdue_tasks: Number of overdue tasks
            - due_today: Number of tasks due today
            - due_this_week: Number of tasks due this week
        """
        # Set default date range
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        # Base query filtered by user and date range
        base_query = select(Task).where(
            Task.user_id == user_id,
            Task.created_at >= start_date,
            Task.created_at <= end_date
        )

        # Get all tasks in range
        tasks = session.exec(base_query).all()
        total_tasks = len(tasks)

        # Calculate completion metrics
        completed_tasks = sum(1 for t in tasks if t.is_completed)
        pending_tasks = total_tasks - completed_tasks
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Calculate due date metrics
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        week_end = today_start + timedelta(days=7)

        overdue_tasks = sum(
            1 for t in tasks
            if t.due_date and t.due_date < now and not t.is_completed
        )

        due_today = sum(
            1 for t in tasks
            if t.due_date and today_start <= t.due_date < today_end
        )

        due_this_week = sum(
            1 for t in tasks
            if t.due_date and today_start <= t.due_date < week_end
        )

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round(completion_rate, 2),
            "overdue_tasks": overdue_tasks,
            "due_today": due_today,
            "due_this_week": due_this_week,
        }

    @staticmethod
    def get_tasks_per_day(
        session: Session,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get daily task completion statistics.

        Args:
            session: Database session
            user_id: UUID of the authenticated user
            start_date: Optional start date (default: 30 days ago)
            end_date: Optional end date (default: now)

        Returns:
            List of dicts with date, created_count, completed_count per day
        """
        # Set default date range
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        # Get all tasks in range
        tasks = session.exec(
            select(Task).where(
                Task.user_id == user_id,
                Task.created_at >= start_date,
                Task.created_at <= end_date
            )
        ).all()

        # Group by day
        daily_stats = defaultdict(lambda: {"created": 0, "completed": 0})

        for task in tasks:
            date_key = task.created_at.date().isoformat()
            daily_stats[date_key]["created"] += 1

            if task.is_completed and task.updated_at:
                completed_date = task.updated_at.date().isoformat()
                daily_stats[completed_date]["completed"] += 1

        # Convert to list and sort by date
        result = [
            {
                "date": date,
                "created_count": stats["created"],
                "completed_count": stats["completed"],
            }
            for date, stats in daily_stats.items()
        ]

        result.sort(key=lambda x: x["date"])
        return result

    @staticmethod
    def get_most_productive_day(
        session: Session,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Find the most productive day (day with most completed tasks).

        Args:
            session: Database session
            user_id: UUID of the authenticated user
            start_date: Optional start date (default: 30 days ago)
            end_date: Optional end date (default: now)

        Returns:
            Dict with date, completed_count, day_name
        """
        # Set default date range
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        # Get completed tasks in range
        completed_tasks = session.exec(
            select(Task).where(
                Task.user_id == user_id,
                Task.is_completed == True,
                Task.updated_at >= start_date,
                Task.updated_at <= end_date
            )
        ).all()

        # Group by weekday
        weekday_counts = defaultdict(int)
        for task in completed_tasks:
            if task.updated_at:
                weekday = task.updated_at.strftime("%A")  # Monday, Tuesday, etc.
                weekday_counts[weekday] += 1

        if not weekday_counts:
            return {
                "day_name": "N/A",
                "completed_count": 0,
                "date": None,
            }

        # Find most productive day
        most_productive = max(weekday_counts.items(), key=lambda x: x[1])

        return {
            "day_name": most_productive[0],
            "completed_count": most_productive[1],
            "date": None,  # Could be enhanced to show most recent occurrence
        }

    @staticmethod
    def get_category_distribution(
        session: Session,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get task distribution across categories.

        Args:
            session: Database session
            user_id: UUID of the authenticated user

        Returns:
            List of dicts with category_id, category_name, task_count, completion_rate
        """
        from ..models.category import Category

        # Get all categories for user
        categories = session.exec(
            select(Category).where(Category.user_id == user_id)
        ).all()

        distribution = []

        for category in categories:
            # Count tasks in this category
            tasks = session.exec(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.category_id == category.id
                )
            ).all()

            total = len(tasks)
            completed = sum(1 for t in tasks if t.is_completed)
            completion_rate = (completed / total * 100) if total > 0 else 0

            distribution.append({
                "category_id": category.id,
                "category_name": category.name,
                "task_count": total,
                "completed_count": completed,
                "completion_rate": round(completion_rate, 2),
            })

        # Sort by task count descending
        distribution.sort(key=lambda x: x["task_count"], reverse=True)
        return distribution

    @staticmethod
    def get_priority_distribution(
        session: Session,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get task distribution across priority levels.

        Args:
            session: Database session
            user_id: UUID of the authenticated user

        Returns:
            List of dicts with priority, task_count, completion_rate
        """
        # Get all tasks for user
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()

        # Group by priority
        priority_stats = defaultdict(lambda: {"total": 0, "completed": 0})

        for task in tasks:
            priority = task.priority or "medium"  # Default to medium if null
            priority_stats[priority]["total"] += 1
            if task.is_completed:
                priority_stats[priority]["completed"] += 1

        # Convert to list
        distribution = []
        for priority in ["critical", "high", "medium", "low"]:
            stats = priority_stats[priority]
            total = stats["total"]
            completed = stats["completed"]
            completion_rate = (completed / total * 100) if total > 0 else 0

            distribution.append({
                "priority": priority,
                "task_count": total,
                "completed_count": completed,
                "completion_rate": round(completion_rate, 2),
            })

        return distribution
