"""
Date Parser Utility - Phase 4: Intermediate Features
Parses natural language dates using python-dateutil
"""

from datetime import datetime, timedelta
from typing import Optional
from dateutil import parser
from dateutil.relativedelta import relativedelta
import re


def parse_natural_date(text: str, user_timezone: str = "UTC") -> Optional[datetime]:
    """
    Parse natural language date strings into datetime objects.

    Supports formats like:
    - "tomorrow"
    - "next Friday"
    - "next week"
    - "2025-12-31"
    - "December 31, 2025"
    - "in 3 days"
    - "next month"

    Args:
        text: Natural language date string
        user_timezone: User's timezone (default: UTC)

    Returns:
        datetime object or None if parsing fails
    """
    if not text or not text.strip():
        return None

    text_lower = text.lower().strip()
    now = datetime.utcnow()

    # Relative date shortcuts
    if text_lower in ["today"]:
        return now.replace(hour=23, minute=59, second=59)

    if text_lower in ["tomorrow"]:
        return (now + timedelta(days=1)).replace(hour=23, minute=59, second=59)

    if text_lower in ["next week"]:
        return (now + timedelta(weeks=1)).replace(hour=23, minute=59, second=59)

    if text_lower in ["next month"]:
        return (now + relativedelta(months=1)).replace(hour=23, minute=59, second=59)

    # Pattern: "in X days/weeks/months"
    in_pattern = r"in (\d+) (day|days|week|weeks|month|months)"
    match = re.search(in_pattern, text_lower)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)

        if "day" in unit:
            return (now + timedelta(days=amount)).replace(hour=23, minute=59, second=59)
        elif "week" in unit:
            return (now + timedelta(weeks=amount)).replace(hour=23, minute=59, second=59)
        elif "month" in unit:
            return (now + relativedelta(months=amount)).replace(hour=23, minute=59, second=59)

    # Specific weekday patterns: "next Monday", "next Friday"
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    for day_name, day_num in weekdays.items():
        if f"next {day_name}" in text_lower:
            days_ahead = (day_num - now.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7  # Next occurrence, not today
            target = now + timedelta(days=days_ahead)
            return target.replace(hour=23, minute=59, second=59)

    # Try python-dateutil parser for standard date formats
    try:
        parsed_date = parser.parse(text, fuzzy=True)

        # If only date is provided (no time), set to end of day
        if parsed_date.hour == 0 and parsed_date.minute == 0 and parsed_date.second == 0:
            parsed_date = parsed_date.replace(hour=23, minute=59, second=59)

        return parsed_date
    except (ValueError, parser.ParserError):
        pass

    # Parsing failed
    return None


def format_relative_date(dt: datetime) -> str:
    """
    Format datetime as relative string (e.g., "due tomorrow", "overdue by 3 days").

    Args:
        dt: Datetime to format

    Returns:
        Human-readable relative date string
    """
    now = datetime.utcnow()
    diff = dt - now

    if diff.days < 0:
        days_overdue = abs(diff.days)
        if days_overdue == 0:
            return "overdue (today)"
        elif days_overdue == 1:
            return "overdue by 1 day"
        else:
            return f"overdue by {days_overdue} days"

    if diff.days == 0:
        return "due today"

    if diff.days == 1:
        return "due tomorrow"

    if diff.days <= 7:
        return f"due in {diff.days} days"

    if diff.days <= 30:
        weeks = diff.days // 7
        if weeks == 1:
            return "due in 1 week"
        return f"due in {weeks} weeks"

    months = diff.days // 30
    if months == 1:
        return "due in 1 month"
    return f"due in {months} months"


def is_overdue(due_date: datetime) -> bool:
    """
    Check if a task is overdue.

    Args:
        due_date: Task's due date

    Returns:
        True if overdue, False otherwise
    """
    return datetime.utcnow() > due_date


def get_due_this_week() -> tuple[datetime, datetime]:
    """
    Get start and end of current week for filtering tasks.

    Returns:
        Tuple of (week_start, week_end)
    """
    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())  # Monday
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)  # Sunday

    return week_start, week_end


# Export all functions
__all__ = [
    "parse_natural_date",
    "format_relative_date",
    "is_overdue",
    "get_due_this_week",
]
