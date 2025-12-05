"""Task service for managing todo operations."""

from src.models.task import Task

# Global task store (in-memory)
_tasks: list[Task] = []
_next_id: int = 1


def reset() -> None:
    """Reset task store (for testing)."""
    global _tasks, _next_id
    _tasks = []
    _next_id = 1


def add_task(title: str, description: str = "") -> Task:
    """Add a new task.

    Args:
        title: Task title (required)
        description: Task description (optional)

    Returns:
        Created Task object

    Raises:
        ValueError: If title is empty or whitespace-only
    """
    global _next_id

    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    task = Task(_next_id, title.strip(), description.strip())
    _tasks.append(task)
    _next_id += 1
    return task


def get_all_tasks() -> list[Task]:
    """Get all tasks.

    Returns:
        List of all Task objects
    """
    return _tasks.copy()


def get_task_by_id(task_id: int) -> Task | None:
    """Get a task by ID.

    Args:
        task_id: Task ID to find

    Returns:
        Task object if found, None otherwise
    """
    for task in _tasks:
        if task.id == task_id:
            return task
    return None


def mark_complete(task_id: int) -> bool:
    """Mark a task as complete.

    Args:
        task_id: ID of task to mark complete

    Returns:
        True if successful, False if task not found

    Raises:
        ValueError: If task already complete
    """
    task = get_task_by_id(task_id)
    if not task:
        return False

    if task.completed:
        raise ValueError(f"Task {task_id} is already complete")

    task.mark_complete()
    return True


def delete_task(task_id: int) -> bool:
    """Delete a task.

    Args:
        task_id: ID of task to delete

    Returns:
        True if successful, False if task not found
    """
    global _tasks
    task = get_task_by_id(task_id)
    if not task:
        return False

    _tasks = [t for t in _tasks if t.id != task_id]
    return True


def update_task(
    task_id: int, title: str = None, description: str = None
) -> bool:
    """Update a task.

    Args:
        task_id: ID of task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        True if successful, False if task not found

    Raises:
        ValueError: If title is empty/whitespace when provided
    """
    task = get_task_by_id(task_id)
    if not task:
        return False

    if title is not None and (not title or not title.strip()):
        raise ValueError("Title cannot be empty")

    task.update(title.strip() if title else None,
                description.strip() if description else None)
    return True
