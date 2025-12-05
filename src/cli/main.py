"""CLI main module for todo application."""

from src.cli.input_helpers import get_string, get_task_id, get_optional_string
from src.cli.table_formatter import format_tasks_table
from src.services import task_service


def show_help() -> None:
    """Display available commands."""
    print("\nAvailable commands:")
    print("  add     - Add a new task")
    print("  view    - View all tasks")
    print("  mark    - Mark a task as complete (e.g., 'mark 1')")
    print("  delete  - Delete a task (e.g., 'delete 1')")
    print("  update  - Update a task (e.g., 'update 1')")
    print("  exit    - Exit the application\n")


def cmd_add() -> None:
    """Handle add command."""
    try:
        title = get_string("Enter title: ", required=True)
        description = get_optional_string("Enter description (optional): ")
        task = task_service.add_task(title, description)
        print(f"Task {task.id} created successfully")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_view() -> None:
    """Handle view command."""
    tasks = task_service.get_all_tasks()
    if not tasks:
        print("No tasks found")
        return
    print(format_tasks_table(tasks))


def cmd_mark() -> None:
    """Handle mark command."""
    task_id = get_task_id("Enter task ID to mark complete: ")
    if task_id is None:
        return

    try:
        if task_service.mark_complete(task_id):
            print(f"Task {task_id} marked as complete")
        else:
            print(f"Task not found")
    except ValueError as e:
        print(f"Task {task_id} already marked complete")


def cmd_delete() -> None:
    """Handle delete command."""
    task_id = get_task_id("Enter task ID to delete: ")
    if task_id is None:
        return

    if task_service.delete_task(task_id):
        print(f"Task {task_id} deleted")
    else:
        print(f"Task not found")


def cmd_update() -> None:
    """Handle update command."""
    task_id = get_task_id("Enter task ID to update: ")
    if task_id is None:
        return

    task = task_service.get_task_by_id(task_id)
    if not task:
        print(f"Task not found")
        return

    print(f"Current title: {task.title}")
    new_title = get_optional_string(
        "Enter new title (leave blank to keep): "
    )
    print(f"Current description: {task.description}")
    new_description = get_optional_string(
        "Enter new description (leave blank to keep): "
    )

    try:
        task_service.update_task(
            task_id,
            new_title if new_title else None,
            new_description if new_description else None,
        )
        print(f"Task {task_id} updated")
    except ValueError as e:
        print(f"Error: {e}")


def run_cli() -> None:
    """Run the command-line interface."""
    print("Welcome to Todo App!")
    print("Type 'exit' to quit or enter a command.")
    show_help()

    while True:
        try:
            command = input("> ").strip().lower()

            if not command:
                continue

            parts = command.split()
            cmd = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            if cmd == "add":
                cmd_add()
            elif cmd == "view":
                cmd_view()
            elif cmd == "mark":
                if args:
                    try:
                        task_id = int(args[0])
                        try:
                            if task_service.mark_complete(task_id):
                                print(f"Task {task_id} marked as complete")
                            else:
                                print(f"Task not found")
                        except ValueError:
                            print(f"Task {task_id} already marked complete")
                    except ValueError:
                        print(f"Invalid task ID '{args[0]}'")
                else:
                    cmd_mark()
            elif cmd == "delete":
                if args:
                    try:
                        task_id = int(args[0])
                        if task_service.delete_task(task_id):
                            print(f"Task {task_id} deleted")
                        else:
                            print(f"Task not found")
                    except ValueError:
                        print(f"Invalid task ID '{args[0]}'")
                else:
                    cmd_delete()
            elif cmd == "update":
                if args:
                    try:
                        task_id = int(args[0])
                        task = task_service.get_task_by_id(task_id)
                        if not task:
                            print(f"Task not found")
                        else:
                            print(f"Current title: {task.title}")
                            new_title = get_optional_string(
                                "Enter new title (leave blank to keep): "
                            )
                            print(f"Current description: {task.description}")
                            new_description = get_optional_string(
                                "Enter new description (leave blank to keep): "
                            )
                            task_service.update_task(
                                task_id,
                                new_title if new_title else None,
                                new_description if new_description else None,
                            )
                            print(f"Task {task_id} updated")
                    except ValueError as e:
                        if "not a valid integer" in str(e).lower():
                            print(f"Invalid task ID '{args[0]}'")
                        else:
                            print(f"Error: {e}")
                else:
                    cmd_update()
            elif cmd == "exit":
                print("Goodbye!")
                break
            elif cmd == "help":
                show_help()
            else:
                print(f"Unknown command '{cmd}'")
                show_help()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
