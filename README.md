# Todo Application - Phase 1

A command-line todo application built with Python 3.13+, implementing core CRUD operations (Create, Read, Update, Delete) with task completion tracking.

## Features

- **Add Tasks**: Create new tasks with title (required) and optional description
- **View All Tasks**: Display tasks in a formatted table with ID, title, description, and status
- **Mark Complete**: Mark tasks as complete (status shows [X])
- **Delete Tasks**: Permanently remove tasks from the list
- **Update Tasks**: Modify task title and/or description
- **Exit**: Gracefully shut down the application

## Requirements

- Python 3.13 or later
- No external dependencies (uses Python standard library only)

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd todo-app
   ```

2. Install the project:
   ```bash
   pip install -e .
   ```

## Usage

### Run the Application

```bash
python main.py
```

### Commands

The application provides an interactive command loop with the following commands:

#### add
Add a new task
```
> add
Enter title: Buy groceries
Enter description (optional): Milk, eggs, bread
Task 1 created successfully
```

#### view
Display all tasks
```
> view
ID | Title         | Description         | Status
---|---------------|---------------------|-------
1  | Buy groceries | Milk, eggs, bread   | [ ]
2  | Review PR     | Check code quality  | [X]
```

#### mark `<ID>`
Mark a task as complete
```
> mark 1
Task 1 marked as complete
```

#### delete `<ID>`
Delete a task
```
> delete 1
Task 1 deleted
```

#### update `<ID>`
Update a task's title or description
```
> update 2
Current title: Review PR
Enter new title (leave blank to keep): Review PR changes
Current description: Check code quality
Enter new description (leave blank to keep):
Task 2 updated
```

#### exit
Exit the application
```
> exit
Goodbye!
```

#### help
Display available commands
```
> help
Available commands:
  add     - Add a new task
  view    - View all tasks
  mark    - Mark a task as complete (e.g., 'mark 1')
  delete  - Delete a task (e.g., 'delete 1')
  update  - Update a task (e.g., 'update 1')
  exit    - Exit the application
```

## Architecture

### Project Structure

```
src/
├── models/
│   ├── __init__.py
│   └── task.py                 # Task data model
├── services/
│   ├── __init__.py
│   └── task_service.py         # Business logic
├── cli/
│   ├── __init__.py
│   ├── main.py                 # Command-line interface
│   ├── input_helpers.py        # Input utilities
│   └── table_formatter.py      # Table display formatting
└── __init__.py

tests/
├── unit/                       # Unit tests (future)
├── integration/                # Integration tests (future)
└── contract/                   # Contract tests (future)

main.py                         # Application entry point
pyproject.toml                  # Project configuration
```

### Layered Architecture

- **Model Layer** (`src/models/`): Task entity with status tracking
- **Service Layer** (`src/services/`): Business logic independent of CLI
- **CLI Layer** (`src/cli/`): User interaction, prompts, and display

This separation enables:
- Independent testing of business logic
- Easy replacement of CLI with API or GUI in future phases
- Clean code organization with single responsibility

## Data Storage

- **In-Memory**: All data stored in Python lists/dictionaries
- **No Persistence**: Data resets when application exits
- **Auto-Incrementing IDs**: Tasks automatically assigned unique IDs starting from 1

## Edge Cases Handled

- Empty/whitespace input validation
- Invalid task ID handling with clear error messages
- Idempotent completion (marking already-complete task shows friendly message)
- Optional descriptions (can be empty)
- Unknown command handling with help display

## Known Limitations (Phase 1)

- No data persistence between sessions
- No task categories, priorities, or due dates
- No search or filtering functionality
- No user authentication
- No concurrent task operations

## Future Phases

Phase 2 will introduce:
- File persistence (JSON, SQLite)
- Task categories and priorities
- Due dates and recurrence
- User authentication
- Search and filtering
- Web/API interface

## Code Quality

- **PEP 8 Compliance**: Follows Python style guidelines
- **Modular Design**: Clear separation of concerns
- **Type Hints**: Python type annotations for clarity
- **Docstrings**: Comprehensive documentation of functions and classes

## Testing

Manual testing is recommended for Phase 1. Run through the following scenarios:

1. Add a task with title only
2. Add a task with title and description
3. View empty task list
4. View populated task list
5. Mark task complete and verify status change
6. Delete task and verify removal
7. Update task title only
8. Update task description only
9. Handle invalid task IDs with all commands
10. Exit gracefully

Automated test suites can be added in future phases using pytest.

## License

This project is part of the Q4 2025 Hackathon.
