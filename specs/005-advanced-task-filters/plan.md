# Implementation Plan: Advanced Task Filtering & Organization

**Feature Branch**: `005-advanced-task-filters`
**Status**: Complete
**Created**: 2025-12-31
**Completed**: 2026-01-11

---

## Overview

This feature adds natural language querying capabilities to the task management system. It builds upon the Phase 4 intermediate features (specs/004) which provide the underlying data structures for priority, tags, categories, due dates, and search.

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Chat Kit UI │  │  TaskList    │  │  TaskFilters         │   │
│  │  (ChatPanel) │  │  Component   │  │  Component           │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      ChatAgent                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │ Direct      │  │ OpenRouter  │  │ Action          │  │   │
│  │  │ Intent      │→ │ AI Model    │→ │ Executor        │  │   │
│  │  │ Detection   │  │ (LLaMA 3.3) │  │                 │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ TaskService  │  │ TagService   │  │ CategoryService      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PostgreSQL (Neon Serverless)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │  tasks   │  │   tags   │  │categories│  │ task_tags    │    │
│  │  (GIN    │  │          │  │          │  │ (junction)   │    │
│  │  index)  │  │          │  │          │  │              │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Natural Language Processing Flow

```
User Input: "show my high priority work tasks"
                    │
                    ▼
┌──────────────────────────────────────┐
│  1. Direct Intent Detection          │
│     - Pattern matching for common    │
│       commands (add task, list, etc) │
│     - Fast, reliable first-attempt   │
└──────────────────────────────────────┘
                    │ (not matched)
                    ▼
┌──────────────────────────────────────┐
│  2. AI Processing (OpenRouter)       │
│     - System prompt defines actions  │
│     - Extracts JSON action from resp │
│     - e.g., {"action": "list_tasks", │
│              "filter": "high"}       │
└──────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────┐
│  3. Action Execution                 │
│     - Calls appropriate service      │
│     - TaskService.get_tasks_by_user( │
│         priority="high",             │
│         category_id=work_category_id │
│       )                              │
└──────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────┐
│  4. Response Formatting              │
│     - Conversational response        │
│     - Includes task list with IDs    │
│     - Translated to Urdu if needed   │
└──────────────────────────────────────┘
```

## Key Design Decisions

### 1. Direct Intent Detection for Reliability

**Decision**: Implement regex-based direct intent detection before AI processing.

**Rationale**:
- AI responses can be inconsistent on first attempt
- Common commands should work 100% of the time
- Reduces latency for simple operations

**Implementation**: `ChatAgent._detect_direct_intent()` handles:
- "add task X" → start_guided_task with initial_title
- "list tasks" → list_tasks action
- "complete task #N" → complete_task action
- "delete task #N" → delete_task action

### 2. Guided Task Creation Flow

**Decision**: Implement multi-step wizard for task creation instead of single-shot.

**Rationale**:
- Users want to add all task details (priority, due date, tags, etc.)
- Step-by-step is more user-friendly than complex single commands
- State persisted in database for reliability across requests

**States**:
1. AWAITING_TITLE
2. AWAITING_DESCRIPTION
3. AWAITING_CATEGORY
4. AWAITING_PRIORITY
5. AWAITING_DUE_DATE
6. AWAITING_RECURRENCE
7. AWAITING_TAGS

### 3. Full-Text Search with PostgreSQL

**Decision**: Use PostgreSQL native full-text search (tsvector, GIN index).

**Rationale**:
- No external dependencies (Elasticsearch, etc.)
- Good enough for MVP task volumes (<1000 tasks per user)
- Fuzzy matching with plainto_tsquery

**Implementation**:
- `search_vector` column on tasks table
- GIN index for fast lookups
- Searches title, description, and notes

### 4. Bilingual Support (English/Urdu)

**Decision**: Full Urdu translation in chatbot responses.

**Rationale**:
- Target user base includes Urdu speakers
- Better UX with native language support

**Implementation**:
- System prompts in both languages
- `_translate_to_urdu()` fallback for AI responses
- Urdu patterns in direct intent detection

## Dependencies

This feature depends on Phase 4 (specs/004-intermediate-features):

1. **Task Model** with priority, due_date, category_id, recurrence fields
2. **Tag/Category Models** and services
3. **Full-text search** vector column and GIN index
4. **Subtask support** for checklist items

## Testing Strategy

### Unit Tests
- TaskService filter/sort methods
- Direct intent detection patterns
- Date parsing utilities

### Integration Tests
- Chatbot end-to-end conversation flows
- Database query performance with filters

### Manual Testing
- Natural language variations
- Multi-language support
- Edge cases (empty results, invalid IDs)

## Performance Considerations

1. **Database Indexes**:
   - GIN index on search_vector
   - B-tree index on user_id, category_id, priority
   - Composite index on (user_id, is_completed, priority)

2. **Query Optimization**:
   - Always filter by user_id first
   - Use DISTINCT only when joining with tags
   - Limit results for large task lists

3. **AI Latency**:
   - Direct intent detection bypasses AI for common commands
   - Async HTTP calls to OpenRouter
   - 30-second timeout with graceful error handling

## Security Considerations

1. **SQL Injection Prevention**:
   - All queries use SQLAlchemy ORM
   - Search queries use parameterized plainto_tsquery

2. **User Isolation**:
   - All service methods require user_id
   - user_id comes from JWT, never from request body

3. **Input Validation**:
   - Tag names validated (1-30 characters)
   - Priority values validated against enum
   - Task IDs validated as integers

## Completion Status

All core functionality is implemented. The feature is production-ready with:

- Natural language task filtering (status, priority, category, tags)
- Keyword search with fuzzy matching
- Guided task creation with all fields
- Basic CRUD operations via chatbot
- Bilingual support (English/Urdu)
- Direct intent detection for reliability

### Future Enhancements
- Natural language sorting ("sort by due date")
- Combined filter+sort in single request
- Pagination for large result sets
- Smart filter suggestions
