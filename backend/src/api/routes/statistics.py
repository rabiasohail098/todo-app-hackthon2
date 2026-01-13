"""Statistics API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from datetime import datetime, timedelta

from ...services.statistics_service import StatisticsService
from ..deps import get_db, get_current_user

router = APIRouter()


@router.get(
    "/statistics",
    summary="Get overall task statistics",
)
async def get_statistics(
    start_date: Optional[str] = Query(None, description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format: YYYY-MM-DD)"),
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict:
    """
    Get overall task statistics for the authenticated user.

    Args:
        start_date: Optional start date filter (ISO format)
        end_date: Optional end date filter (ISO format)
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        Dict with statistics:
        - total_tasks: Total number of tasks
        - completed_tasks: Number of completed tasks
        - pending_tasks: Number of pending tasks
        - completion_rate: Percentage of completed tasks
        - overdue_tasks: Number of overdue tasks
        - due_today: Number of tasks due today
        - due_this_week: Number of tasks due this week

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Statistics filtered by user_id for isolation
    """
    # Parse date filters
    start_dt = None
    end_dt = None

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            # Invalid date format - use default
            pass

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            # Invalid date format - use default
            pass

    stats = StatisticsService.get_overall_statistics(
        session, current_user_id, start_dt, end_dt
    )

    return stats


@router.get(
    "/statistics/daily",
    summary="Get daily task creation and completion statistics",
)
async def get_daily_statistics(
    start_date: Optional[str] = Query(None, description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format: YYYY-MM-DD)"),
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> List[dict]:
    """
    Get daily task statistics (created and completed counts per day).

    Args:
        start_date: Optional start date filter (default: 30 days ago)
        end_date: Optional end date filter (default: now)
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        List of dicts with date, created_count, completed_count per day

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Statistics filtered by user_id for isolation
    """
    # Parse date filters
    start_dt = None
    end_dt = None

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            pass

    daily_stats = StatisticsService.get_tasks_per_day(
        session, current_user_id, start_dt, end_dt
    )

    return daily_stats


@router.get(
    "/statistics/productive-day",
    summary="Get most productive day of the week",
)
async def get_most_productive_day(
    start_date: Optional[str] = Query(None, description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format: YYYY-MM-DD)"),
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict:
    """
    Get the most productive day of the week (day with most completed tasks).

    Args:
        start_date: Optional start date filter (default: 30 days ago)
        end_date: Optional end date filter (default: now)
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        Dict with day_name, completed_count

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Statistics filtered by user_id for isolation
    """
    # Parse date filters
    start_dt = None
    end_dt = None

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            pass

    productive_day = StatisticsService.get_most_productive_day(
        session, current_user_id, start_dt, end_dt
    )

    return productive_day


@router.get(
    "/statistics/categories",
    summary="Get task distribution across categories",
)
async def get_category_distribution(
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> List[dict]:
    """
    Get task distribution across categories.

    Args:
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        List of dicts with category_id, category_name, task_count, completion_rate

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Statistics filtered by user_id for isolation
    """
    distribution = StatisticsService.get_category_distribution(session, current_user_id)
    return distribution


@router.get(
    "/statistics/priorities",
    summary="Get task distribution across priority levels",
)
async def get_priority_distribution(
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> List[dict]:
    """
    Get task distribution across priority levels.

    Args:
        current_user_id: UUID from JWT token (automatic)
        session: Database session (automatic)

    Returns:
        List of dicts with priority, task_count, completion_rate

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Statistics filtered by user_id for isolation
    """
    distribution = StatisticsService.get_priority_distribution(session, current_user_id)
    return distribution
