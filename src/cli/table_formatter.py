"""Table formatting utilities for CLI."""

from src.models.task import Task


def format_tasks_table(tasks: list[Task]) -> str:
    """Format tasks as an ASCII table.

    Args:
        tasks: List of tasks to format

    Returns:
        Formatted table string
    """
    if not tasks:
        return "No tasks found"

    # Calculate column widths
    id_width = 2
    title_width = max(5, max(len(t.title) for t in tasks))
    desc_width = max(11, max(len(t.description) for t in tasks))
    status_width = 6

    # Create header
    header = (
        f"ID | {'Title'.ljust(title_width)} | "
        f"{'Description'.ljust(desc_width)} | Status"
    )
    separator = "-" * len(header)

    # Create rows
    rows = []
    for task in tasks:
        row = (
            f"{task.id:<2} | {task.title.ljust(title_width)} | "
            f"{task.description.ljust(desc_width)} | {task.get_status_symbol()}"
        )
        rows.append(row)

    # Combine all parts
    table = f"\n{header}\n{separator}\n" + "\n".join(rows)
    return table
