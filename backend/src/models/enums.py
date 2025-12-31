"""
Enums for Phase 4: Intermediate Features
Defines priority levels and recurrence patterns for tasks
"""

from enum import Enum


class TaskPriority(str, Enum):
    """
    Priority levels for tasks
    Used for filtering, sorting, and visual indicators
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_natural_language(cls, text: str) -> "TaskPriority":
        """
        Parse priority from natural language keywords

        Args:
            text: Natural language input (e.g., "urgent", "important", "low priority")

        Returns:
            TaskPriority enum value
        """
        text_lower = text.lower()

        # Critical/urgent keywords
        if any(word in text_lower for word in ["critical", "urgent", "asap", "emergency"]):
            return cls.CRITICAL

        # High priority keywords
        if any(word in text_lower for word in ["high", "important", "priority"]):
            return cls.HIGH

        # Low priority keywords
        if any(word in text_lower for word in ["low", "minor", "someday", "later"]):
            return cls.LOW

        # Default to medium
        return cls.MEDIUM


class RecurrencePattern(str, Enum):
    """
    Recurrence patterns for recurring tasks
    Used for auto-generating next occurrences
    """
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"  # For cron-like patterns

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_natural_language(cls, text: str) -> "RecurrencePattern | None":
        """
        Parse recurrence pattern from natural language

        Args:
            text: Natural language input (e.g., "daily", "every week", "monthly")

        Returns:
            RecurrencePattern enum value or None if not recurring
        """
        text_lower = text.lower()

        # Daily keywords
        if any(word in text_lower for word in ["daily", "every day", "each day"]):
            return cls.DAILY

        # Weekly keywords
        if any(word in text_lower for word in ["weekly", "every week", "each week"]):
            return cls.WEEKLY

        # Monthly keywords
        if any(word in text_lower for word in ["monthly", "every month", "each month"]):
            return cls.MONTHLY

        # Custom patterns (TODO: implement cron-like parsing)
        if "every" in text_lower and any(word in text_lower for word in ["monday", "tuesday", "wednesday"]):
            return cls.CUSTOM

        # Not a recurring task
        return None


# Export all enums
__all__ = ["TaskPriority", "RecurrencePattern"]
