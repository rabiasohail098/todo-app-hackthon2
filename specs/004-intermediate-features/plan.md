# Implementation Plan: Intermediate Features

**Branch**: `004-intermediate-features` | **Date**: 2025-12-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-intermediate-features/spec.md`

## Summary

**Core Organization (P0)**: Categories, Priorities, Due Dates, Search
**Enhanced Features (P1)**: Subtasks, Task Statistics, Tags, Recurring Tasks
**Advanced Features (P2)**: Notes & Attachments, Activity Log

**Technical Approach**:
- Extend existing database schema with 5 new models (Category, Tag, Subtask, TaskActivity, Attachment)
- Add 4 new fields to Task model (priority, due_date, category_id, recurrence_pattern)
- Enhance AI chatbot to parse categories, priorities, dates, tags, and recurrence patterns from natural language
- Implement full-text search using PostgreSQL tsvector
- Build analytics dashboard with chart visualizations
- Use cloud storage (Cloudinary) for file attachments

**Milestones**:
1. Organization Features (Categories, Priorities, Tags, Filters) - Weeks 1-2
2. Time Management (Due Dates, Recurring Tasks) - Weeks 3-4
3. Advanced Features (Subtasks, Search, Activity Log, Attachments) - Weeks 5-6
4. Analytics (Statistics Dashboard, Charts) - Week 7

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.3 (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Pydantic, python-dateutil (date parsing), APScheduler (recurring tasks)
- Frontend: Next.js 16, React 19, Recharts (charts), React-Markdown (notes), Tailwind CSS
**Storage**: PostgreSQL (Neon Serverless) with full-text search indexes (tsvector, GIN)
**Testing**: pytest (backend), Vitest + React Testing Library (frontend)
**Target Platform**: Web application (responsive desktop/mobile)
**Project Type**: Web (frontend + backend)
**Performance Goals**:
- Search response: <200ms for 1000 tasks
- Statistics calculation: <500ms
- File upload: <3s for 5MB
- Page load: <2s with 100 tasks
**Constraints**:
- Full-text search must use PostgreSQL native capabilities (no external search service)
- File storage must use cloud provider (Cloudinary)
- User isolation: all queries filter by user_id
- File size limit: 10MB per attachment
- Rate limiting: 10 file uploads per hour per user
**Scale/Scope**:
- Support 1000+ tasks per user
- Up to 100 categories per user
- Unlimited tags (many-to-many with tasks)
- 10 subtasks per task limit
- 1 year of activity log retention

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Stateless by Design ✅ PASS
- All new endpoints (categories, search, statistics, subtasks, tags, attachments, activity) are stateless
- Each request is self-contained with JWT auth
- Recurring task generation handled via scheduled job (not in-memory state)
- Statistics cached in database, not in-memory

### Principle III: Security Propagation ✅ PASS
- All new models include `user_id` field
- All queries filter by `user_id` from JWT
- Category, Tag, Subtask, TaskActivity, Attachment models enforce user isolation
- File uploads scanned and validated before storage

### Principle IV: Conversation Persistence ✅ PASS
- AI chatbot enhancements preserve conversation history
- New commands (categories, priorities, dates, tags) logged in conversation

### Principle V: Atomic Operations ✅ PASS
- Each task update (priority, due date, category, tags) commits immediately
- Subtask creation/completion commits atomically
- Activity log entries created in same transaction as task changes

### Principle VIII: Type Safety & Validation ✅ PASS
- All new models use SQLModel with explicit types
- Pydantic models for request/response validation
- Priority enum: TaskPriority(str, Enum) = {Critical, High, Medium, Low}
- Recurrence pattern enum: RecurrencePattern(str, Enum) = {Daily, Weekly, Monthly, Custom}
- Tag name validation: 1-30 characters
- File type validation for attachments

### Principle IX: Natural Language Robustness ✅ PASS
- AI agent enhanced to parse:
  - Categories from context ("add work task" → category=Work)
  - Priority keywords (critical/high/urgent/important → High)
  - Dates (tomorrow, next Friday, 2025-12-31) using python-dateutil
  - Tags from hashtags (#urgent #meeting)
  - Recurrence patterns (daily, weekly, every Monday)
- Ambiguous commands prompt for clarification

### Principle X: Database Performance ✅ PASS
- Indexes added: `priority`, `due_date`, `category_id`
- Full-text search index: `search_vector` (tsvector) with GIN
- Pagination implemented (default 50, max 100)
- Eager loading for task.category, task.tags relationships
- Statistics queries optimized with aggregation
- Activity log soft-deletes after 1 year

### Principle XI: Modular Service Architecture ✅ PASS
- New services created:
  - `CategoryService` - CRUD for categories
  - `TagService` - Tag management
  - `SubtaskService` - Subtask operations
  - `SearchService` - Full-text search
  - `StatisticsService` - Analytics calculations
  - `AttachmentService` - File upload/download
  - `ActivityLogService` - Change tracking
- Existing `TaskService` extended with new fields
- Existing `ChatAgent` enhanced with new parsing logic

### Principle XII: Observability & Feedback Loops ✅ PASS
- All new endpoints log user_id, operation, duration
- Search queries logged for optimization
- File upload errors logged with file type, size, user
- Slow queries (>1s) logged for database optimization
- Statistics calculation time tracked

### Principle XIII: Scalability & Resource Management ✅ PASS
- File uploads to cloud storage (Cloudinary), not local filesystem
- Statistics cached (recalculated hourly or on-demand with cache invalidation)
- Search paginated (never return all tasks)
- Rate limiting on file uploads (10/hour/user)
- Background job for recurring task generation (APScheduler)
- Circuit breaker on Cloudinary API calls

**Constitution Compliance**: ✅ **PASS** - All 9 applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/004-intermediate-features/
├── spec.md              # Feature specification (DONE)
├── data-model.md        # Database schema (DONE)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Technology research (PENDING - Phase 0)
├── quickstart.md        # Setup guide (PENDING - Phase 1)
├── contracts/           # API contracts (PENDING - Phase 1)
│   └── api.yaml         # OpenAPI specification
└── tasks.md             # Implementation tasks (PENDING - Phase 2, /sp.tasks)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)

backend/
├── src/
│   ├── models/
│   │   ├── task.py           # MODIFY: Add priority, due_date, category_id, recurrence fields
│   │   ├── category.py       # NEW: Category model
│   │   ├── tag.py            # NEW: Tag model
│   │   ├── subtask.py        # NEW: Subtask model
│   │   ├── task_activity.py  # NEW: TaskActivity model
│   │   └── attachment.py     # NEW: Attachment model
│   │
│   ├── services/
│   │   ├── task_service.py        # MODIFY: Add priority, due_date, category methods
│   │   ├── category_service.py    # NEW: Category CRUD
│   │   ├── tag_service.py         # NEW: Tag management
│   │   ├── subtask_service.py     # NEW: Subtask operations
│   │   ├── search_service.py      # NEW: Full-text search
│   │   ├── statistics_service.py  # NEW: Analytics calculations
│   │   ├── attachment_service.py  # NEW: File upload/download
│   │   └── activity_log_service.py # NEW: Change tracking
│   │
│   ├── agent/
│   │   └── chat_agent.py      # MODIFY: Enhance with category/priority/date/tag parsing
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── tasks.py       # MODIFY: Add priority, due_date, category params
│   │       ├── categories.py  # NEW: Category endpoints
│   │       ├── search.py      # NEW: Search endpoint
│   │       ├── statistics.py  # NEW: Statistics endpoint
│   │       ├── subtasks.py    # NEW: Subtask endpoints
│   │       ├── tags.py        # NEW: Tag endpoints
│   │       └── attachments.py # NEW: File upload/download endpoints
│   │
│   └── utils/
│       ├── date_parser.py     # NEW: Natural language date parsing
│       ├── recurrence.py      # NEW: Recurring task logic
│       └── file_validator.py  # NEW: File type/size validation
│
└── tests/
    ├── unit/
    │   ├── test_category_service.py
    │   ├── test_tag_service.py
    │   ├── test_search_service.py
    │   ├── test_statistics_service.py
    │   ├── test_date_parser.py
    │   └── test_recurrence.py
    │
    └── integration/
        ├── test_categories_api.py
        ├── test_search_api.py
        ├── test_statistics_api.py
        └── test_attachments_api.py

frontend/
├── app/
│   ├── dashboard/
│   │   ├── page.tsx           # MODIFY: Add filters, search, sorting
│   │   ├── statistics/
│   │   │   └── page.tsx       # NEW: Statistics dashboard
│   │   └── categories/
│   │       └── page.tsx       # NEW: Category management
│   │
│   └── api/
│       ├── tasks/[id]/
│       │   ├── route.ts       # MODIFY: Add priority, due_date, category
│       │   ├── subtasks/
│       │   │   └── route.ts   # NEW: Subtask API
│       │   ├── tags/
│       │   │   └── route.ts   # NEW: Tag API
│       │   ├── attachments/
│       │   │   └── route.ts   # NEW: Attachment API
│       │   └── activity/
│       │       └── route.ts   # NEW: Activity log API
│       │
│       ├── categories/
│       │   └── route.ts       # NEW: Category API
│       ├── search/
│       │   └── route.ts       # NEW: Search API
│       └── statistics/
│           └── route.ts       # NEW: Statistics API
│
├── components/
│   ├── TaskFilters.tsx        # NEW: Category, priority, date filters
│   ├── SearchBar.tsx          # NEW: Real-time task search
│   ├── CategoryBadge.tsx      # NEW: Visual category indicator
│   ├── PriorityIndicator.tsx  # NEW: Priority icon/color
│   ├── DueDateDisplay.tsx     # NEW: Due date with warning colors
│   ├── SubtaskList.tsx        # NEW: Subtask management
│   ├── StatisticsChart.tsx    # NEW: Analytics visualizations (Recharts)
│   ├── TagInput.tsx           # NEW: Tag auto-complete input
│   ├── RecurrenceSelector.tsx # NEW: Recurrence pattern picker
│   └── ActivityLog.tsx        # NEW: Change history display
│
└── tests/
    └── components/
        ├── TaskFilters.test.tsx
        ├── SearchBar.test.tsx
        ├── StatisticsChart.test.tsx
        └── SubtaskList.test.tsx

database/
└── migrations/
    └── 004_add_intermediate_features.sql  # NEW: Database schema changes
```

**Structure Decision**: This feature follows the existing web application structure (frontend + backend). The backend is extended with 5 new models and 7 new services. The frontend adds 10 new components and 3 new pages. All new code is modular and follows the existing service layer architecture.

## Complexity Tracking

> **No violations** - All constitution principles pass without justification needed.

## Phase 0: Research & Technology Selection

### Research Tasks

1. **Date Parsing Library Evaluation**
   - **Question**: Which Python library best handles natural language dates ("tomorrow", "next Friday")?
   - **Options**: python-dateutil, parsedatetime, dateparser
   - **Criteria**: Accuracy, language support, performance, maintenance
   - **Output**: Recommendation in `research.md`

2. **Chart Library Selection (Frontend)**
   - **Question**: Which React chart library best fits our needs (bar charts, pie charts, statistics)?
   - **Options**: Recharts, Chart.js, Victory, Nivo
   - **Criteria**: TypeScript support, bundle size, customization, documentation
   - **Output**: Recommendation in `research.md`

3. **File Storage Provider Comparison**
   - **Question**: AWS S3 vs Cloudinary for file attachments?
   - **Criteria**: Pricing (free tier), image optimization, CDN, API simplicity
   - **Output**: Recommendation in `research.md`

4. **Full-Text Search Best Practices**
   - **Question**: How to implement efficient PostgreSQL full-text search with tsvector?
   - **Topics**: Index creation, query syntax, relevance ranking, performance tuning
   - **Output**: Implementation guide in `research.md`

5. **Recurring Task Generation Strategy**
   - **Question**: Background job (APScheduler) vs on-demand generation (when task completed)?
   - **Criteria**: Reliability, complexity, resource usage
   - **Output**: Recommendation in `research.md`

6. **Rich Text Editor Selection**
   - **Question**: Which markdown/rich text editor for task notes?
   - **Options**: React-Markdown, Tiptap, Slate, Draft.js
   - **Criteria**: Markdown support, bundle size, extensibility
   - **Output**: Recommendation in `research.md`

### Expected Research Outcomes

- **Date Parsing**: python-dateutil (standard library companion, well-maintained, handles timezones)
- **Charts**: Recharts (TypeScript-first, lightweight, great docs, composable)
- **File Storage**: Cloudinary (generous free tier, image optimization built-in, simple API)
- **Search**: PostgreSQL tsvector with GIN index (native, no external dependencies, proven at scale)
- **Recurring Tasks**: Background job with APScheduler (reliable, decoupled from user actions)
- **Rich Text**: React-Markdown (simple, lightweight, secure, good enough for task notes)

## Phase 1: Data Models & API Contracts

### Data Models (from data-model.md)

**New Models** (5):
1. `Category` - User-defined categories (Work, Personal, Shopping, etc.)
2. `Tag` - Flexible task tags (many-to-many with tasks)
3. `Subtask` - Child tasks with completion tracking
4. `TaskActivity` - Audit log for task changes
5. `Attachment` - File uploads linked to tasks

**Modified Models** (1):
- `Task` - Add `priority`, `due_date`, `category_id`, `recurrence_pattern`, `next_recurrence_date`

### API Contracts

**New Endpoints** (8 categories, ~25 endpoints total):

#### Categories
- `GET /api/categories` - List user's categories
- `POST /api/categories` - Create category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

#### Search
- `GET /api/tasks/search?q={query}&category={}&priority={}&status={}&tags={}` - Search tasks

#### Statistics
- `GET /api/statistics?from={date}&to={date}` - Get user statistics

#### Subtasks
- `POST /api/tasks/{id}/subtasks` - Add subtask
- `PUT /api/tasks/{task_id}/subtasks/{subtask_id}` - Update subtask
- `DELETE /api/tasks/{task_id}/subtasks/{subtask_id}` - Delete subtask
- `PUT /api/tasks/{task_id}/subtasks/{subtask_id}/complete` - Mark subtask complete

#### Tags
- `GET /api/tags` - List all user's tags
- `POST /api/tasks/{id}/tags` - Add tag to task
- `DELETE /api/tasks/{task_id}/tags/{tag_id}` - Remove tag from task

#### Attachments
- `POST /api/tasks/{id}/attachments` - Upload file
- `GET /api/tasks/{task_id}/attachments/{attachment_id}` - Download file
- `DELETE /api/tasks/{task_id}/attachments/{attachment_id}` - Delete file

#### Activity Log
- `GET /api/tasks/{id}/activity` - Get task change history

#### Modified Endpoints
- `POST /api/tasks` - Add priority, due_date, category_id, tags, recurrence_pattern params
- `PUT /api/tasks/{id}` - Add priority, due_date, category_id params
- `GET /api/tasks` - Add filters: priority, category, due_date_from, due_date_to, overdue, tags

### Quickstart Guide Topics

1. **Database Migration**
   - Run migration script to add new tables and columns
   - Create indexes for performance

2. **Install New Dependencies**
   - Backend: `python-dateutil`, `APScheduler`, `cloudinary`
   - Frontend: `recharts`, `react-markdown`

3. **Configure Environment Variables**
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

4. **Set Up Recurring Task Job**
   - Configure APScheduler to run every hour
   - Generate next occurrences for recurring tasks

5. **Test New Features**
   - Create categories
   - Assign priorities
   - Set due dates
   - Upload attachments
   - View statistics

## Phase 2: Implementation Tasks (Next Step: /sp.tasks)

The `/sp.tasks` command will generate detailed implementation tasks in `tasks.md` based on this plan. Tasks will be organized by milestone:

- **Milestone 1: Organization Features** (Categories, Priorities, Tags, Filters)
- **Milestone 2: Time Management** (Due Dates, Recurring Tasks)
- **Milestone 3: Advanced Features** (Subtasks, Search, Activity Log, Attachments)
- **Milestone 4: Analytics** (Statistics Dashboard, Charts)

---

**Plan Status**: ✅ Ready for Phase 0 Research
**Next Command**: Continue with research.md generation below, then `/sp.tasks` after research complete
