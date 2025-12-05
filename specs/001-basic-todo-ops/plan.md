# Implementation Plan: Basic Todo Operations

**Branch**: `001-basic-todo-ops` | **Date**: 2025-12-05 | **Spec**: specs/001-basic-todo-ops/spec.md
**Input**: Feature specification from `specs/001-basic-todo-ops/spec.md`

**Note**: This plan is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a command-line todo application with core CRUD operations (add, view, update, delete, mark complete). MVP scope: P1 stories only (add/view/mark complete) form a complete task management loop. Phase 1 constraints enforce in-memory storage, Python stdlib only, and modular code organization (models/services/CLI separation). Architecture is CLI-first with interactive prompts, table-based display, and simple command-line interface.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Python standard library only (no external packages)
**Storage**: In-memory (Python lists/dictionaries only; no persistence)
**Testing**: pytest (standard library compatible)
**Target Platform**: Console/Terminal (cross-platform)
**Project Type**: Single CLI project
**Performance Goals**: Immediate command response (<100ms), support display of 1000+ tasks
**Constraints**: No external dependencies, no databases, no file I/O, PEP 8 compliance, modular code structure
**Scale/Scope**: Phase 1 MVP: 3 P1 user stories (add/view/mark) + 2 P2 stories (delete/update); ~500-800 LOC

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Spec-Driven Development**: Spec complete with 5 prioritized user stories, acceptance scenarios, functional requirements
✅ **CLI-First Architecture**: All features accessible via command-line (add, view, update, delete, mark, exit commands)
✅ **In-Memory Storage Only**: No databases or file persistence; data stored in Python lists/dicts only
✅ **PEP 8 Compliance**: Code must follow PEP 8 (4-space indent, <100 char soft limit, descriptive names)
✅ **No External Dependencies**: Python 3.13+ stdlib only; no Flask, Django, requests, etc.
✅ **Modular Code Organization**: Architecture separates models (Task entity), services (business logic), CLI (user interaction)

**GATE RESULT**: ✅ **PASS** - All constitution principles verified. No violations or justified exceptions needed.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   └── task.py                    # Task entity with ID, title, description, status
├── services/
│   ├── __init__.py
│   └── task_service.py            # Business logic: add, view, update, delete, mark
├── cli/
│   ├── __init__.py
│   └── main.py                    # Command-line interface: input/output, command loop
└── __init__.py

tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_task_model.py         # Task entity tests
│   └── test_task_service.py       # Service logic tests
├── integration/
│   ├── __init__.py
│   └── test_cli_integration.py    # End-to-end CLI command tests
└── contract/
    ├── __init__.py
    └── test_cli_contract.py       # CLI interface contract tests

main.py                             # Application entry point
pyproject.toml                      # Project metadata (Python 3.13+, pytest)
```

**Structure Decision**: Single CLI project (Option 1) - Implements all CRUD operations in one Python package with clear separation of concerns:
- **models/**: Task entity (data structure only, no dependencies)
- **services/**: Business logic independent of CLI (testable in isolation)
- **cli/**: User-facing command-line interface (handles I/O, prompts, table display)
- **main.py**: Entry point that orchestrates CLI with services
- **tests/**: Unit (models/services), integration (CLI workflows), contract (command interface)

## Complexity Tracking

No violations - all constitution gates passed. No complexity justification needed.

## Technical Design Decisions

### Architecture Pattern: Layered Architecture

| Layer | Responsibility | Module |
|-------|---|---|
| **Model Layer** | Task entity (data structure) | `src/models/task.py` |
| **Service Layer** | Business logic (add, view, update, delete, mark) | `src/services/task_service.py` |
| **CLI Layer** | User interaction (prompts, table display, command parsing) | `src/cli/main.py` |

**Rationale**: Separation of concerns enables independent testing, reusability of services, and easy future replacement of CLI with API or GUI.

### Data Storage: In-Memory Lists

```python
# Global task store
tasks: list[Task] = []

# Task ID generation
next_task_id: int = 1
```

**Rationale**: Phase 1 constraint; simple, fast, suitable for MVP. Task objects are mutable; ID assignment is atomic.

### CLI Command Flow: Separate Prompts

1. User types command: `add` → `update` → `view` → `mark 2` → `exit`
2. For `add`: App prompts "Enter title:", user types, prompts "Enter description:", user types
3. For commands with ID: `mark <ID>`, `delete <ID>`, `update <ID>` on single line

**Rationale**: Learner-friendly, Unix conventions, reduces parsing complexity.

### Display Format: ASCII Table

```
ID | Title            | Description         | Status
---|------------------|---------------------|-------
1  | Buy groceries    | Milk, eggs, bread   | [ ]
2  | Review PR        | Check code quality  | [X]
```

**Rationale**: Clear at-a-glance visibility, standard CLI convention, easy to implement with string formatting.

## Testing Strategy

### Unit Tests (Test Models & Services in Isolation)

- **Task Model**: Entity creation, attributes, status transitions
- **Task Service**: Add task, view all tasks, mark complete, update, delete (no CLI dependency)

### Integration Tests (Task Service + CLI Workflows)

- **Full Command Workflows**: `add` → `view` → `mark 2` → `view` (end-to-end flows)
- **Error Handling**: Invalid IDs, empty input, unrecognized commands

### Contract Tests (CLI Interface Compliance)

- **Command Syntax**: `add`, `view`, `mark <ID>`, `delete <ID>`, `update <ID>`, `exit` all parse correctly
- **Display Format**: `view` output contains all 4 columns (ID, Title, Description, Status)
- **Status Display**: Pending tasks show [ ], completed tasks show [X]

## Risk Analysis

| Risk | Mitigation |
|------|-----------|
| Python 3.13 compatibility | Verify all stdlib functions used are available in 3.13+ |
| Command parsing complexity | Simple split-based parsing; validate ID conversion early |
| Large task lists (1000+) | Simple list operations O(n); acceptable for MVP; optimize in Phase 2 if needed |
| User input edge cases | Comprehensive validation: empty/whitespace input, invalid IDs, unrecognized commands |

## Next Steps

1. Generate **tasks.md** with `/sp.tasks` command (work items organized by user story)
2. Implement tasks in priority order: P1 (add/view/mark) → P2 (delete/update)
3. Validate each task against acceptance scenarios before marking complete
4. Ensure all code passes PEP 8 linting before commit
