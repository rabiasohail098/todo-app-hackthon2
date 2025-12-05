"""Task model for todo application."""


class Task:
    """Represents a single todo task."""

    def __init__(self, task_id: int, title: str, description: str = ""):
        """Initialize a Task.

        Args:
            task_id: Unique task identifier (auto-assigned)
            title: Task title (required)
            description: Task description (optional)
        """
        self.id = task_id
        self.title = title
        self.description = description
        self.completed = False

    def mark_complete(self) -> None:
        """Mark task as complete."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark task as incomplete."""
        self.completed = False

    def update(self, title: str = None, description: str = None) -> None:
        """Update task title and/or description.

        Args:
            title: New title (optional, keeps current if not provided)
            description: New description (optional, keeps current if not provided)
        """
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description

    def get_status_symbol(self) -> str:
        """Get status symbol for display.

        Returns:
            '[X]' if complete, '[ ]' if pending
        """
        return "[X]" if self.completed else "[ ]"

    def __repr__(self) -> str:
        """Return string representation of task."""
        return (
            f"Task(id={self.id}, title='{self.title}', "
            f"description='{self.description}', completed={self.completed})"
        )
