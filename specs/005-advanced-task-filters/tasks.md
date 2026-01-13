# Tasks: Advanced Task Filtering & Organization

**Feature Branch**: `005-advanced-task-filters`
**Status**: Complete
**Dependencies**: specs/004-intermediate-features (Phase 4 must be complete)

---

## User Story 1: Natural Language Task Filtering (P1)

### Backend Tasks

- [X] **Task 1.1**: Implement filter by status (pending/completed) in TaskService
  - File: `backend/src/services/task_service.py`
  - `get_tasks_by_user()` accepts `is_completed` parameter
  - Already implemented in Phase 4

- [X] **Task 1.2**: Implement filter by priority (high/medium/low) in TaskService
  - File: `backend/src/services/task_service.py`
  - `get_tasks_by_user()` accepts `priority` parameter
  - Already implemented in Phase 4

- [X] **Task 1.3**: Implement filter by category in TaskService
  - File: `backend/src/services/task_service.py`
  - `get_tasks_by_user()` accepts `category_id` parameter
  - Already implemented in Phase 4

- [X] **Task 1.4**: Implement filter by tag in TaskService
  - File: `backend/src/services/task_service.py`
  - `get_tasks_by_user()` accepts `tag_ids` parameter
  - Already implemented in Phase 4

- [X] **Task 1.5**: Implement combined filters (AND logic) in TaskService
  - File: `backend/src/services/task_service.py`
  - Multiple filters can be combined in single query
  - Already implemented in Phase 4

### Chatbot Integration Tasks

- [X] **Task 1.6**: Add `list_tasks` action with filter support in ChatAgent
  - File: `backend/src/agent/chat_agent.py`
  - Supports "all", "completed", "incomplete" filters
  - Implemented in chatbot

- [X] **Task 1.7**: Update system prompt to handle natural language filter requests
  - File: `backend/src/agent/chat_agent.py`
  - System prompt includes filter examples
  - Implemented

- [X] **Task 1.8**: Add empty result handling with friendly messages
  - File: `backend/src/agent/chat_agent.py`
  - Returns "You have no {filter} tasks" when empty
  - Implemented

---

## User Story 2: Natural Language Task Sorting (P2)

### Backend Tasks

- [X] **Task 2.1**: Implement sort by priority in TaskService
  - File: `backend/src/services/task_service.py`
  - `get_tasks_by_user()` accepts `sort_by="priority_desc"` or `"priority_asc"`
  - Implemented in Phase 4

- [X] **Task 2.2**: Implement sort by due date (ascending) in TaskService
  - File: `backend/src/services/task_service.py`
  - `get_tasks_by_user()` accepts `sort_by="due_date_asc"`
  - Implemented in Phase 4

- [X] **Task 2.3**: Implement sort by due date (descending) in TaskService
  - File: `backend/src/services/task_service.py`
  - `get_tasks_by_user()` accepts `sort_by="due_date_desc"`
  - Implemented in Phase 4

- [X] **Task 2.4**: Handle null due dates (appear at end when sorting by date)
  - File: `backend/src/services/task_service.py`
  - Uses `.nullslast()` in sorting
  - Implemented in Phase 4

### Chatbot Integration Tasks (Future Enhancement)

- [ ] **Task 2.5**: Add sorting action support in ChatAgent
  - File: `backend/src/agent/chat_agent.py`
  - Add ability to parse "sort by priority", "sort by due date" in natural language
  - Not critical for MVP - filtering works

- [ ] **Task 2.6**: Add combined filter+sort support in ChatAgent
  - File: `backend/src/agent/chat_agent.py`
  - e.g., "show high priority tasks sorted by due date"
  - Enhancement for future

---

## User Story 3: Keyword Search in Tasks (P2)

### Backend Tasks

- [X] **Task 3.1**: Add full-text search to TaskService
  - File: `backend/src/services/task_service.py`
  - `get_tasks_by_user()` accepts `search_query` parameter
  - Uses PostgreSQL `plainto_tsquery` for fuzzy matching
  - Implemented in Phase 4

- [X] **Task 3.2**: Add search_vector column to Task model
  - File: `backend/src/models/task.py`
  - GIN index for fast full-text search
  - Implemented in Phase 4

- [X] **Task 3.3**: Search in both title and description
  - File: `backend/src/services/task_service.py`
  - search_vector includes title, description, notes
  - Implemented in Phase 4

### Chatbot Integration Tasks

- [X] **Task 3.4**: Add `search_tasks` action in ChatAgent
  - File: `backend/src/agent/chat_agent.py`
  - Parses search query from natural language
  - Implemented

- [X] **Task 3.5**: Add no-results handling for search
  - File: `backend/src/agent/chat_agent.py`
  - Returns "No tasks found matching '{query}'" when empty
  - Implemented

---

## User Story 4: Priority-Based Task Management (P1)

### Backend Tasks

- [X] **Task 4.1**: Define TaskPriority enum with High/Medium/Low/Critical
  - File: `backend/src/models/enums.py`
  - Enum: CRITICAL, HIGH, MEDIUM, LOW
  - Implemented in Phase 4

- [X] **Task 4.2**: Add priority field to Task model
  - File: `backend/src/models/task.py`
  - `priority: Optional[TaskPriority]` field
  - Implemented in Phase 4

- [X] **Task 4.3**: Default new tasks to Medium priority
  - File: `backend/src/agent/chat_agent.py`
  - Default priority is "medium" in guided flow and create_task
  - Implemented

- [X] **Task 4.4**: Allow priority update via API
  - File: `backend/src/api/routes/tasks.py`
  - TaskUpdate includes priority field
  - Implemented in Phase 4

### Chatbot Integration Tasks

- [X] **Task 4.5**: Add priority selection in guided task creation
  - File: `backend/src/agent/chat_agent.py`
  - `_format_priority_options()` shows Critical/High/Medium/Low
  - Implemented

- [X] **Task 4.6**: Parse priority from natural language
  - File: `backend/src/agent/chat_agent.py`
  - Maps "urgent/important" to high, "normal" to medium, "minor" to low
  - Implemented

---

## User Story 5: Tag & Category Assignment (P1)

### Backend Tasks

- [X] **Task 5.1**: Create Tag model
  - File: `backend/src/models/tag.py`
  - Tag with name field
  - Implemented in Phase 4

- [X] **Task 5.2**: Create TaskTag many-to-many relationship
  - File: `backend/src/models/task_tag.py`
  - Links tasks to tags
  - Implemented in Phase 4

- [X] **Task 5.3**: Create TagService for tag operations
  - File: `backend/src/services/tag_service.py`
  - create_tag, add_tag_to_task, remove_tag_from_task
  - Implemented in Phase 4

- [X] **Task 5.4**: Create CategoryService
  - File: `backend/src/services/category_service.py`
  - create_or_get_category, get_categories_by_user
  - Implemented in Phase 4

- [X] **Task 5.5**: Add category_id to Task model
  - File: `backend/src/models/task.py`
  - Foreign key to Category table
  - Implemented in Phase 4

### Chatbot Integration Tasks

- [X] **Task 5.6**: Add category selection in guided task creation
  - File: `backend/src/agent/chat_agent.py`
  - `_format_category_options()` lists available categories
  - Allows creating new categories inline
  - Implemented

- [X] **Task 5.7**: Add tag input in guided task creation
  - File: `backend/src/agent/chat_agent.py`
  - Parses hashtags and comma-separated tags
  - Implemented

- [X] **Task 5.8**: Auto-create categories mentioned in natural language
  - File: `backend/src/agent/chat_agent.py`
  - `create_or_get_category()` called during task creation
  - Implemented

---

## User Story 6: Basic Task CRUD Operations (P1)

### Backend Tasks

- [X] **Task 6.1**: Implement TaskService.create_task()
  - File: `backend/src/services/task_service.py`
  - Creates task with all Phase 4 fields
  - Implemented

- [X] **Task 6.2**: Implement TaskService.get_tasks_by_user()
  - File: `backend/src/services/task_service.py`
  - Lists tasks with filters and sorting
  - Implemented

- [X] **Task 6.3**: Implement TaskService.update_task()
  - File: `backend/src/services/task_service.py`
  - PATCH semantics, updates only provided fields
  - Implemented

- [X] **Task 6.4**: Implement TaskService.delete_task()
  - File: `backend/src/services/task_service.py`
  - Verifies ownership before deletion
  - Implemented

- [X] **Task 6.5**: Enforce user isolation in all operations
  - File: `backend/src/services/task_service.py`
  - All queries filter by user_id from JWT
  - Implemented

### Chatbot Integration Tasks

- [X] **Task 6.6**: Add `create_task` action in ChatAgent
  - File: `backend/src/agent/chat_agent.py`
  - Implemented with guided flow

- [X] **Task 6.7**: Add `list_tasks` action in ChatAgent
  - File: `backend/src/agent/chat_agent.py`
  - Shows tasks with IDs for reference
  - Implemented

- [X] **Task 6.8**: Add `complete_task` action in ChatAgent
  - File: `backend/src/agent/chat_agent.py`
  - Marks task as completed
  - Implemented

- [X] **Task 6.9**: Add `uncomplete_task` action in ChatAgent
  - File: `backend/src/agent/chat_agent.py`
  - Marks task as incomplete
  - Implemented

- [X] **Task 6.10**: Add `delete_task` action in ChatAgent
  - File: `backend/src/agent/chat_agent.py`
  - Deletes task by ID
  - Implemented

- [X] **Task 6.11**: Add `update_task` action in ChatAgent
  - File: `backend/src/agent/chat_agent.py`
  - Updates task title/description
  - Implemented

- [X] **Task 6.12**: Add direct intent detection for common commands
  - File: `backend/src/agent/chat_agent.py`
  - `_detect_direct_intent()` for reliable first-attempt behavior
  - Implemented

---

## Edge Cases & Error Handling

- [X] **Task 7.1**: Handle empty result sets with friendly messages
  - Returns appropriate message when no tasks match filters
  - Implemented

- [X] **Task 7.2**: Handle invalid task IDs
  - Returns "Task {id} not found" error
  - Implemented

- [X] **Task 7.3**: Handle invalid priority values
  - Defaults to "medium" for unknown priorities
  - Implemented

- [X] **Task 7.4**: Sanitize user input (SQL injection prevention)
  - Uses parameterized queries with SQLAlchemy
  - Implemented

- [X] **Task 7.5**: Enforce user data isolation
  - All queries include user_id filter
  - Implemented

---

## Summary

**Total Tasks**: 45
**Completed**: 43
**Remaining**: 2 (non-critical enhancements)

### Remaining Tasks (Future Enhancements)

1. **Task 2.5**: Add sorting action support in ChatAgent natural language
2. **Task 2.6**: Add combined filter+sort support in ChatAgent

These are enhancements that would improve UX but are not critical for the core functionality. The backend already supports sorting - it just needs to be exposed in the chatbot's natural language understanding.

### Implementation Notes

This feature was largely implemented through:
1. **Phase 4 (specs/004)**: Database models, services, API routes for priority, tags, categories, search
2. **Chatbot Enhancements**: Guided task creation wizard with all fields, direct intent detection, multi-language support

The natural language processing is handled by the OpenRouter AI model (Llama 3.3 70B) with structured system prompts that define available actions and their JSON formats.
