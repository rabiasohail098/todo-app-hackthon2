---

description: "Task list for Basic Todo Operations feature implementation"

---

# Tasks: Basic Todo Operations

**Input**: Design documents from `specs/001-basic-todo-ops/`
**Prerequisites**: spec.md (required), plan.md (required for structure and architecture)

**Tests**: No automated tests included - implementation focus for MVP. Integration tests via manual CLI testing. Can add pytest tests in future phases.

**Organization**: Tasks are grouped by phase: Setup → Foundational → User Stories (P1 first, then P2) → Polish. Each phase represents independently testable functionality.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4, US5) - only for story phases
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below are based on plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md (src/models, src/services, src/cli, tests/)
- [x] T002 Create Python package structure with __init__.py files in src/models/, src/services/, src/cli/, tests/unit/, tests/integration/, tests/contract/
- [x] T003 [P] Create pyproject.toml with Python 3.13+ requirement and pytest configuration for testing
- [x] T004 Create main.py application entry point that initializes CLI and starts command loop

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create src/models/task.py with Task class: ID (int, auto-assigned), Title (str, required), Description (str, optional), Status (bool, False=pending/True=complete)
- [x] T006 [P] Create src/services/task_service.py with global task store (list) and ID counter, implement add_task(title, description) → Task, mark_complete(task_id) → success/error
- [x] T007 [P] Create src/cli/main.py with command loop that accepts user input and routes to commands
- [x] T008 Create src/cli/input_helpers.py with utility functions: get_string(prompt, required=True), get_task_id(prompt) with validation

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Task (Priority: P1) 🎯 MVP

**Goal**: Users can quickly add tasks by providing title and optional description; system assigns unique IDs

**Independent Test**: Run app, type `add`, enter "Buy groceries" (title only), verify task created with ID 1 and success message shown

- [x] T009 [US1] Implement add command handler in src/cli/main.py: parse `add` command, prompt for title (required), prompt for description (optional), call task_service.add_task()
- [x] T010 [US1] Add error handling for empty/whitespace titles in add command - show error and reprompt
- [x] T011 [US1] Display success message after task added: "Task [ID] created successfully"
- [x] T012 [US1] Manual test: Run app, add task with title only, verify ID=1 assigned
- [x] T013 [US1] Manual test: Run app, add task with title and description, verify both stored

**Checkpoint**: User Story 1 functional and testable independently

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1) 🎯 MVP

**Goal**: Users see all tasks in a clear table format with ID, Title, Description, and Status columns

**Independent Test**: Add 3 tasks (2 pending, 1 complete), type `view`, verify table displays all tasks with correct columns and status symbols ([ ] vs [X])

- [x] T014 [US2] Implement view command handler in src/cli/main.py: parse `view` command, call task_service.get_all_tasks(), format and display results
- [x] T015 [US2] Create src/cli/table_formatter.py with format_tasks_table(tasks) function that returns ASCII table: ID | Title | Description | Status with header separator and aligned columns
- [x] T016 [US2] Implement status display: pending tasks show [ ], complete tasks show [X]
- [x] T017 [US2] Handle empty task list: display "No tasks found" message
- [x] T018 [US2] Manual test: View empty list, verify "No tasks found" message
- [x] T019 [US2] Manual test: Add 3 tasks (create one complete), run view, verify table format and status symbols correct

**Checkpoint**: User Stories 1 AND 2 work independently - basic add/view loop complete

---

## Phase 5: User Story 3 - Mark Task Complete (Priority: P1) 🎯 MVP

**Goal**: Users can mark individual tasks as complete, seeing status change from [ ] to [X]

**Independent Test**: Add task (ID 1), type `mark 1`, verify status changes to [X], type `view` to confirm status persisted

- [x] T020 [US3] Implement mark command handler in src/cli/main.py: parse `mark <ID>` command, validate ID, call task_service.mark_complete(task_id), display success/error
- [x] T021 [US3] Add ID parsing and validation: convert string to int, check if task exists, show "Task not found" error for invalid IDs
- [x] T022 [US3] Handle idempotent marking: if task already complete, show message "Task [ID] already marked complete"
- [x] T023 [US3] Display success message: "Task [ID] marked as complete"
- [x] T024 [US3] Manual test: Add task, mark it complete, verify status shows [X]
- [x] T025 [US3] Manual test: Mark already-complete task, verify friendly message shown
- [x] T026 [US3] Manual test: Mark non-existent ID, verify "Task not found" error

**Checkpoint**: All P1 stories complete - MVP functionality ready (add/view/mark complete forms complete workflow)

---

## Phase 6: User Story 4 - Delete Task (Priority: P2)

**Goal**: Users can permanently remove tasks they no longer need

**Independent Test**: Add task (ID 1), type `delete 1`, verify removed, type `view` to confirm task gone

- [x] T027 [US4] Implement delete command handler in src/cli/main.py: parse `delete <ID>` command, validate ID, call task_service.delete_task(task_id), display success/error
- [x] T028 [US4] Implement task deletion in src/services/task_service.py: delete_task(task_id) → success/error, remove from list
- [x] T029 [US4] Handle invalid delete attempts: show "Task not found" error for non-existent IDs
- [x] T030 [US4] Display success message: "Task [ID] deleted"
- [x] T031 [US4] Manual test: Add task, delete it, verify no longer in list
- [x] T032 [US4] Manual test: Delete non-existent ID, verify error message

**Checkpoint**: User Stories 1-4 complete

---

## Phase 7: User Story 5 - Update Task (Priority: P2)

**Goal**: Users can modify task title or description

**Independent Test**: Add task with title "Buy groceries", type `update 1`, change title to "Buy groceries and cook", verify changes with view command

- [x] T033 [US5] Implement update command handler in src/cli/main.py: parse `update <ID>` command, validate ID, prompt for new title and/or description, call task_service.update_task()
- [x] T034 [US5] Implement task update in src/services/task_service.py: update_task(task_id, title=None, description=None) → success/error, update only provided fields
- [x] T035 [US5] Handle update interaction: prompt "Enter new title (leave blank to keep current):", allow optional empty input to skip title, same for description
- [x] T036 [US5] Handle invalid update attempts: show "Task not found" error for non-existent IDs
- [x] T037 [US5] Display success message: "Task [ID] updated"
- [x] T038 [US5] Manual test: Update task title only, verify description unchanged
- [x] T039 [US5] Manual test: Update description only, verify title unchanged
- [x] T040 [US5] Manual test: Update non-existent ID, verify error message

**Checkpoint**: All user stories complete - full CRUD functionality implemented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories and overall app quality

- [x] T041 [P] Add input validation helper: validate_task_id(input_str) → int or None, handles non-numeric input gracefully
- [x] T042 [P] Implement command help: when user types unrecognized command, show available commands: add, view, mark, delete, update, exit
- [x] T043 Implement exit command: user types `exit`, app shuts down cleanly with "Goodbye!" message
- [x] T044 PEP 8 compliance check: Run linting on all src/ files (4-space indent, <100 char lines, descriptive names)
- [x] T045 Code review: Verify modularity - models/ has no CLI code, services/ has no I/O, cli/ orchestrates correctly
- [x] T046 Create README.md with: feature overview, how to run (python main.py), example commands, known limitations
- [x] T047 Manual full integration test: Run app end-to-end (add 3 tasks, view, mark 1 complete, view, delete 1, update 1, view, exit) with no errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - P1 stories (Add, View, Mark) can proceed in sequence (T009 → T014 → T020)
  - P2 stories (Delete, Update) can proceed in sequence (T027 → T033)
  - After Foundational, P1 and P2 can proceed in parallel (different developers)
- **Polish (Phase 8)**: Depends on all story phases

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 (needs tasks to view)
- **User Story 3 (P1)**: Depends on US1 and US2 (needs tasks to mark, view results)
- **User Story 4 (P2)**: Depends on US1, US2, US3 (independent after MVP, can delete tasks)
- **User Story 5 (P2)**: Depends on US1, US2, US3 (independent after MVP, can update tasks)

### Parallel Opportunities

**Setup Phase Tasks**:
- T003 (pyproject.toml) and T004 (main.py) can run in parallel

**Foundational Phase Tasks**:
- T005 (Task model) can run independently
- T006 (service functions) can run after T005 complete
- T007 (CLI loop) can run independently of T006 (implement after foundational APIs ready)
- T008 (input helpers) can run independently

**Within Each User Story (Example: User Story 1)**:
- T009, T010, T011 are sequential (depend on each other)
- T012, T013 are manual tests (can run in parallel after T011 complete)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

For fastest MVP delivery:

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T008)
3. Complete Phase 3: User Story 1 - Add Task (T009-T013)
4. **STOP and DEMO**: Can now add tasks and verify IDs assigned
5. Test on user: Is adding tasks enough value? Continue to Stories 2-3 or iterate

### Incremental Delivery (Recommended)

1. Phases 1-2: Setup & Foundation (T001-T008) → foundation ready
2. Phase 3: User Story 1 - Add Task (T009-T013) → **Demo: Add tasks**
3. Phase 4: User Story 2 - View All Tasks (T014-T019) → **Demo: See all tasks**
4. Phase 5: User Story 3 - Mark Complete (T020-T026) → **Demo: Track progress** 🎯 MVP READY
5. Phase 6: User Story 4 - Delete Task (T027-T032) → **Demo: Clean up**
6. Phase 7: User Story 5 - Update Task (T033-T040) → **Demo: Manage details**
7. Phase 8: Polish (T041-T047) → Production ready

### Parallel Team Strategy

With multiple developers (recommend 2-3 for this size):

1. All complete Phases 1-2 together (foundation shared)
2. Developer A: Phase 3 (User Story 1)
3. Developer B: Phases 4-5 (User Stories 2-3)
4. Developer C: Phases 6-7 (User Stories 4-5)
5. All: Phase 8 (polish together)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label = maps to user story (US1 = User Story 1, etc.)
- Each phase checkpoints: can stop and demo at each checkpoint
- All file paths absolute per plan.md structure: src/, tests/, main.py at repo root
- Manual tests verify against acceptance scenarios in spec.md
- Validation: PEP 8 + modularity + no external imports check before final commit

