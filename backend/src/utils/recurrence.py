"""
Recurrence Logic Utility - Phase 4: Intermediate Features
Calculate next occurrence dates for recurring tasks
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional
import sys
sys.path.append('/mnt/e/q4-hackathon/todo-app-hackthon2/backend/src')
from models.enums import RecurrencePattern


def calculate_next_occurrence(
    current_date: datetime,
    pattern: RecurrencePattern,
    interval: int = 1
) -> datetime:
    """
    Calculate the next occurrence date for a recurring task.

    Args:
        current_date: Current occurrence date
        pattern: Recurrence pattern (daily, weekly, monthly, custom)
        interval: How often to recur (e.g., every 2 weeks)

    Returns:
        Next occurrence datetime

    Examples:
        >>> now = datetime(2025, 12, 31, 12, 0, 0)
        >>> calculate_next_occurrence(now, RecurrencePattern.DAILY, 1)
        datetime.datetime(2026, 1, 1, 12, 0, 0)

        >>> calculate_next_occurrence(now, RecurrencePattern.WEEKLY, 2)
        datetime.datetime(2026, 1, 14, 12, 0, 0)
    """
    if pattern == RecurrencePattern.DAILY:
        return current_date + timedelta(days=interval)

    elif pattern == RecurrencePattern.WEEKLY:
        return current_date + timedelta(weeks=interval)

    elif pattern == RecurrencePattern.MONTHLY:
        return current_date + relativedelta(months=interval)

    elif pattern == RecurrencePattern.CUSTOM:
        # TODO: Implement cron-like custom patterns
        # For now, default to daily
        return current_date + timedelta(days=interval)

    else:
        raise ValueError(f"Unknown recurrence pattern: {pattern}")


def should_generate_occurrence(
    next_recurrence_date: Optional[datetime],
    now: Optional[datetime] = None
) -> bool:
    """
    Check if it's time to generate the next occurrence.

    Args:
        next_recurrence_date: When the next occurrence should be created
        now: Current time (default: utcnow)

    Returns:
        True if should generate next occurrence, False otherwise
    """
    if next_recurrence_date is None:
        return False

    if now is None:
        now = datetime.utcnow()

    return now >= next_recurrence_date


def get_recurrence_interval_from_text(text: str) -> tuple[RecurrencePattern, int]:
    """
    Parse recurrence pattern and interval from natural language.

    Args:
        text: Natural language description (e.g., "every 2 weeks", "daily")

    Returns:
        Tuple of (RecurrencePattern, interval)

    Examples:
        >>> get_recurrence_interval_from_text("daily")
        (RecurrencePattern.DAILY, 1)

        >>> get_recurrence_interval_from_text("every 2 weeks")
        (RecurrencePattern.WEEKLY, 2)

        >>> get_recurrence_interval_from_text("every 3 days")
        (RecurrencePattern.DAILY, 3)
    """
    text_lower = text.lower().strip()

    # Default values
    pattern = RecurrencePattern.DAILY
    interval = 1

    # Parse "every X days/weeks/months"
    import re
    match = re.search(r"every (\d+) (day|days|week|weeks|month|months)", text_lower)

    if match:
        interval = int(match.group(1))
        unit = match.group(2)

        if "day" in unit:
            pattern = RecurrencePattern.DAILY
        elif "week" in unit:
            pattern = RecurrencePattern.WEEKLY
        elif "month" in unit:
            pattern = RecurrencePattern.MONTHLY

        return pattern, interval

    # Simple keywords
    if "daily" in text_lower or "every day" in text_lower:
        return RecurrencePattern.DAILY, 1

    if "weekly" in text_lower or "every week" in text_lower:
        return RecurrencePattern.WEEKLY, 1

    if "monthly" in text_lower or "every month" in text_lower:
        return RecurrencePattern.MONTHLY, 1

    # Specific weekday patterns
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if any(f"every {day}" in text_lower for day in weekdays):
        return RecurrencePattern.WEEKLY, 1

    # Default
    return pattern, interval


def format_recurrence_text(pattern: RecurrencePattern, interval: int = 1) -> str:
    """
    Format recurrence pattern as human-readable text.

    Args:
        pattern: Recurrence pattern
        interval: Recurrence interval

    Returns:
        Human-readable recurrence description

    Examples:
        >>> format_recurrence_text(RecurrencePattern.DAILY, 1)
        "Daily"

        >>> format_recurrence_text(RecurrencePattern.WEEKLY, 2)
        "Every 2 weeks"
    """
    if pattern == RecurrencePattern.DAILY:
        if interval == 1:
            return "Daily"
        return f"Every {interval} days"

    elif pattern == RecurrencePattern.WEEKLY:
        if interval == 1:
            return "Weekly"
        return f"Every {interval} weeks"

    elif pattern == RecurrencePattern.MONTHLY:
        if interval == 1:
            return "Monthly"
        return f"Every {interval} months"

    elif pattern == RecurrencePattern.CUSTOM:
        return "Custom recurrence"

    return "Unknown recurrence"


def get_next_occurrences(
    start_date: datetime,
    pattern: RecurrencePattern,
    interval: int = 1,
    count: int = 5
) -> list[datetime]:
    """
    Generate a list of next occurrence dates.

    Useful for previewing recurring task schedule.

    Args:
        start_date: Starting date
        pattern: Recurrence pattern
        interval: Recurrence interval
        count: How many occurrences to generate

    Returns:
        List of datetime objects for next occurrences
    """
    occurrences = []
    current_date = start_date

    for _ in range(count):
        next_date = calculate_next_occurrence(current_date, pattern, interval)
        occurrences.append(next_date)
        current_date = next_date

    return occurrences


# Export all functions
__all__ = [
    "calculate_next_occurrence",
    "should_generate_occurrence",
    "get_recurrence_interval_from_text",
    "format_recurrence_text",
    "get_next_occurrences",
]
