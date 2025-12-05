"""Input helper functions for CLI."""


def get_string(prompt: str, required: bool = True) -> str:
    """Get string input from user.

    Args:
        prompt: Prompt to display
        required: If True, reject empty/whitespace input

    Returns:
        User input (stripped)

    Raises:
        ValueError: If required=True and input is empty/whitespace
    """
    while True:
        value = input(prompt).strip()
        if required and not value:
            print("Input cannot be empty. Please try again.")
            continue
        return value


def get_task_id(prompt: str) -> int | None:
    """Get task ID from user input.

    Args:
        prompt: Prompt to display

    Returns:
        Task ID as integer, or None if invalid

    Raises:
        ValueError: If input is not a valid integer
    """
    value = input(prompt).strip()
    try:
        task_id = int(value)
        if task_id <= 0:
            print("Task ID must be a positive number.")
            return None
        return task_id
    except ValueError:
        print(f"Invalid task ID '{value}'. Please enter a number.")
        return None


def get_optional_string(prompt: str) -> str:
    """Get optional string input from user.

    Args:
        prompt: Prompt to display

    Returns:
        User input (stripped), or empty string if user provides no input
    """
    return input(prompt).strip()
