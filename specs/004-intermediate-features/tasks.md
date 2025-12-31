# Tasks: Intermediate Features

**Input**: Design documents from `/specs/004-intermediate-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.yaml, quickstart.md

**Tests**: Tests are optional per specification - focused on implementation tasks

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US10)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `frontend/`
- Backend: `backend/src/models/`, `backend/src/services/`, `backend/src/api/routes/`
- Frontend: `frontend/app/`, `frontend/components/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure environment

- [X] T001 Install backend dependencies: python-dateutil, APScheduler, cloudinary
- [X] T002 Install frontend dependencies: recharts, react-markdown
- [X] T003 [P] Configure Cloudinary environment variables in backend/.env
- [X] T004 [P] Update backend/requirements.txt with new dependencies
- [X] T005 [P] Update frontend/package.json with new dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema, migrations, and shared utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create database migration script: database/migrations/004_add_intermediate_features.sql
- [X] T007 [P] Add priority enum to backend: backend/src/models/enums.py (TaskPriority: critical, high, medium, low)
- [X] T008 [P] Add recurrence pattern enum to backend: backend/src/models/enums.py (RecurrencePattern: daily, weekly, monthly, custom)
- [X] T009 Update Task model: Add priority, due_date, category_id, recurrence_pattern, next_recurrence_date fields in backend/src/models/task.py
- [X] T010 [P] Create date parser utility: backend/src/utils/date_parser.py (parse natural language dates using python-dateutil)
- [X] T011 [P] Create file validator utility: backend/src/utils/file_validator.py (validate file types, sizes)
- [X] T012 [P] Create recurrence logic utility: backend/src/utils/recurrence.py (calculate next occurrence dates)
- [X] T013 Run database migration to add new tables and columns
- [X] T014 Create full-text search trigger: Add tsvector column and GIN index to tasks table
- [X] T015 [P] Configure APScheduler in backend/src/api/main.py (background job for recurring tasks)

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Categories (Priority: P0) 🎯 MVP

**Goal**: Users can create custom categories (Work, Personal, Shopping) and organize tasks by category

**Independent Test**: Create a category, assign it to a task, filter tasks by category

### Implementation for User Story 1

#### Backend

- [ ] T016 [P] [US1] Create Category model in backend/src/models/category.py (id, user_id, name, color, icon, created_at)
- [ ] T017 [US1] Create CategoryService in backend/src/services/category_service.py (CRUD operations)
- [ ] T018 [US1] Create categories API routes in backend/src/api/routes/categories.py (GET, POST, PUT, DELETE /api/categories)
- [ ] T019 [US1] Update TaskService to support category_id filtering in backend/src/services/task_service.py
- [ ] T020 [US1] Enhance ChatAgent to parse category from natural language in backend/src/agent/chat_agent.py

#### Frontend

- [ ] T021 [P] [US1] Create CategoryBadge component in frontend/components/CategoryBadge.tsx
- [ ] T022 [P] [US1] Create categories API route in frontend/app/api/categories/route.ts
- [ ] T023 [US1] Create category management page in frontend/app/dashboard/categories/page.tsx
- [ ] T024 [US1] Add category filter to TaskFilters component (create if not exists) in frontend/components/TaskFilters.tsx
- [ ] T025 [US1] Update task creation/editing to include category selection

**Checkpoint**: Users can create categories, assign tasks to categories, and filter by category

---

## Phase 4: User Story 2 - Task Priority Levels (Priority: P0)

**Goal**: Users can assign priority levels (Critical, High, Medium, Low) to tasks for importance tracking

**Independent Test**: Create task with high priority, filter tasks by priority, sort by priority

### Implementation for User Story 2

#### Backend

- [ ] T026 [US2] Update TaskService to support priority filtering and sorting in backend/src/services/task_service.py
- [ ] T027 [US2] Update tasks API routes to accept priority parameter in backend/src/api/routes/tasks.py
- [ ] T028 [US2] Enhance ChatAgent to parse priority keywords in backend/src/agent/chat_agent.py

#### Frontend

- [ ] T029 [P] [US2] Create PriorityIndicator component in frontend/components/PriorityIndicator.tsx (color-coded icons)
- [ ] T030 [US2] Add priority filter to TaskFilters component in frontend/components/TaskFilters.tsx
- [ ] T031 [US2] Update task creation/editing forms to include priority selector
- [ ] T032 [US2] Add priority sorting option to dashboard

**Checkpoint**: Users can assign priorities, filter by priority, and sort tasks by urgency

---

## Phase 5: User Story 3 - Due Dates & Reminders (Priority: P0)

**Goal**: Users can set due dates for tasks and see overdue tasks highlighted

**Independent Test**: Create task with due date tomorrow, view overdue tasks, filter by "due this week"

### Implementation for User Story 3

#### Backend

- [ ] T033 [US3] Update TaskService to support due_date filtering (today, this week, overdue) in backend/src/services/task_service.py
- [ ] T034 [US3] Update tasks API routes to accept due_date filters in backend/src/api/routes/tasks.py
- [ ] T035 [US3] Enhance ChatAgent to parse natural language dates in backend/src/agent/chat_agent.py (use date_parser utility)

#### Frontend

- [ ] T036 [P] [US3] Create DueDateDisplay component in frontend/components/DueDateDisplay.tsx (with overdue warning colors)
- [ ] T037 [US3] Add due date filters to TaskFilters component in frontend/components/TaskFilters.tsx (Today, This Week, Overdue)
- [ ] T038 [US3] Update task creation/editing forms to include date picker
- [ ] T039 [US3] Add due date sorting option (soonest first, latest first)

**Checkpoint**: Users can set due dates, view overdue tasks, and filter by date ranges

---

## Phase 6: User Story 4 - Task Search (Priority: P0)

**Goal**: Users can search tasks by keywords in title/description with fuzzy matching

**Independent Test**: Search for "meeting", verify matching tasks appear, test fuzzy matching ("milk" matches "Buy milk")

### Implementation for User Story 4

#### Backend

- [ ] T040 [US4] Create SearchService in backend/src/services/search_service.py (full-text search using PostgreSQL tsvector)
- [ ] T041 [US4] Create search API route in backend/src/api/routes/search.py (GET /api/tasks/search with query parameters)
- [ ] T042 [US4] Enhance ChatAgent to detect search intent in backend/src/agent/chat_agent.py

#### Frontend

- [ ] T043 [P] [US4] Create SearchBar component in frontend/components/SearchBar.tsx (real-time search with debounce)
- [ ] T044 [US4] Create search API route in frontend/app/api/search/route.ts
- [ ] T045 [US4] Add SearchBar to dashboard header
- [ ] T046 [US4] Implement search results display with highlighted matches

**Checkpoint**: Users can search tasks, see real-time results, and fuzzy matching works

---

## Phase 7: User Story 5 - Subtasks (Priority: P1)

**Goal**: Users can break down tasks into subtasks and track completion progress

**Independent Test**: Create task, add 3 subtasks, mark 2 complete, verify progress shows "2/3 complete"

### Implementation for User Story 5

#### Backend

- [ ] T047 [P] [US5] Create Subtask model in backend/src/models/subtask.py (id, parent_task_id, title, is_completed, order, created_at)
- [ ] T048 [US5] Create SubtaskService in backend/src/services/subtask_service.py (CRUD, completion tracking)
- [ ] T049 [US5] Create subtasks API routes in backend/src/api/routes/subtasks.py (POST/PUT/DELETE /api/tasks/{id}/subtasks)
- [ ] T050 [US5] Update TaskService to calculate subtask progress in backend/src/services/task_service.py
- [ ] T051 [US5] Enhance ChatAgent to handle subtask commands in backend/src/agent/chat_agent.py

#### Frontend

- [ ] T052 [P] [US5] Create SubtaskList component in frontend/components/SubtaskList.tsx (list with checkboxes, progress bar)
- [ ] T053 [P] [US5] Create subtasks API route in frontend/app/api/tasks/[id]/subtasks/route.ts
- [ ] T054 [US5] Add subtasks section to task detail view
- [ ] T055 [US5] Implement subtask creation UI in task detail

**Checkpoint**: Users can add subtasks, mark them complete, and see progress tracking

---

## Phase 8: User Story 6 - Task Statistics (Priority: P1)

**Goal**: Users can view productivity statistics and charts (completion rate, tasks per day, etc.)

**Independent Test**: View statistics dashboard, verify completion rate calculation, see tasks completed this week chart

### Implementation for User Story 6

#### Backend

- [ ] T056 [US6] Create StatisticsService in backend/src/services/statistics_service.py (calculate completion rate, tasks per day, most productive day)
- [ ] T057 [US6] Create statistics API route in backend/src/api/routes/statistics.py (GET /api/statistics with date range filters)

#### Frontend

- [ ] T058 [P] [US6] Create StatisticsChart component in frontend/components/StatisticsChart.tsx (using Recharts: bar chart, pie chart, line chart)
- [ ] T059 [P] [US6] Create statistics API route in frontend/app/api/statistics/route.ts
- [ ] T060 [US6] Create statistics dashboard page in frontend/app/dashboard/statistics/page.tsx
- [ ] T061 [US6] Add statistics cards (total tasks, completion rate, overdue count, due today count)
- [ ] T062 [US6] Implement date range filter for statistics

**Checkpoint**: Users can view productivity statistics with visual charts

---

## Phase 9: User Story 7 - Task Tags (Priority: P1)

**Goal**: Users can add multiple tags to tasks for flexible organization

**Independent Test**: Create task with tags "urgent" and "meeting", filter tasks by tag, auto-suggest existing tags

### Implementation for User Story 7

#### Backend

- [ ] T063 [P] [US7] Create Tag model in backend/src/models/tag.py (id, user_id, name, created_at)
- [ ] T064 [P] [US7] Create TaskTag join model in backend/src/models/task_tag.py (task_id, tag_id, many-to-many)
- [ ] T065 [US7] Create TagService in backend/src/services/tag_service.py (CRUD, tag suggestions)
- [ ] T066 [US7] Create tags API routes in backend/src/api/routes/tags.py (GET /api/tags, POST/DELETE /api/tasks/{id}/tags)
- [ ] T067 [US7] Update TaskService to support tag filtering in backend/src/services/task_service.py
- [ ] T068 [US7] Enhance ChatAgent to parse hashtags in backend/src/agent/chat_agent.py

#### Frontend

- [ ] T069 [P] [US7] Create TagInput component in frontend/components/TagInput.tsx (auto-complete, chip display)
- [ ] T070 [P] [US7] Create tags API routes in frontend/app/api/tags/route.ts and frontend/app/api/tasks/[id]/tags/route.ts
- [ ] T071 [US7] Add tag filter to TaskFilters component in frontend/components/TaskFilters.tsx
- [ ] T072 [US7] Update task creation/editing forms to include tag input
- [ ] T073 [US7] Make tags clickable to filter by that tag

**Checkpoint**: Users can add multiple tags, filter by tags, and get tag suggestions

---

## Phase 10: User Story 8 - Recurring Tasks (Priority: P1)

**Goal**: Users can create recurring tasks (daily, weekly, monthly) that auto-generate next occurrences

**Independent Test**: Create daily recurring task, wait for background job or manually trigger, verify next occurrence created

### Implementation for User Story 8

#### Backend

- [ ] T074 [US8] Update TaskService to handle recurrence_pattern and next_recurrence_date in backend/src/services/task_service.py
- [ ] T075 [US8] Create recurring task generation job in backend/src/jobs/generate_recurring_tasks.py (APScheduler job runs hourly)
- [ ] T076 [US8] Register APScheduler job in backend/src/main.py
- [ ] T077 [US8] Enhance ChatAgent to parse recurrence patterns in backend/src/agent/chat_agent.py

#### Frontend

- [ ] T078 [P] [US8] Create RecurrenceSelector component in frontend/components/RecurrenceSelector.tsx (dropdown with Daily/Weekly/Monthly options)
- [ ] T079 [US8] Update task creation form to include recurrence selector
- [ ] T080 [US8] Display next occurrence date for recurring tasks

**Checkpoint**: Users can create recurring tasks that auto-generate next occurrences

---

## Phase 11: User Story 9 - Task Notes & Attachments (Priority: P2)

**Goal**: Users can add markdown notes and file attachments to tasks

**Independent Test**: Add markdown note to task, upload PDF attachment, verify download works

### Implementation for User Story 9

#### Backend

- [ ] T081 [P] [US9] Create Attachment model in backend/src/models/attachment.py (id, task_id, filename, file_path, file_size, mime_type, created_at)
- [ ] T082 [US9] Create AttachmentService in backend/src/services/attachment_service.py (upload to Cloudinary, delete, download)
- [ ] T083 [US9] Create attachments API routes in backend/src/api/routes/attachments.py (POST/GET/DELETE /api/tasks/{id}/attachments)
- [ ] T084 [US9] Update Task model to include notes field (markdown text) in backend/src/models/task.py
- [ ] T085 [US9] Enhance ChatAgent to handle "add note to task X" commands in backend/src/agent/chat_agent.py

#### Frontend

- [ ] T086 [P] [US9] Add react-markdown support for rendering notes
- [ ] T087 [P] [US9] Create attachments API routes in frontend/app/api/tasks/[id]/attachments/route.ts
- [ ] T088 [US9] Add markdown notes editor to task detail (textarea with preview)
- [ ] T089 [US9] Implement file upload UI for attachments (drag-drop or file picker)
- [ ] T090 [US9] Display attached files with download links
- [ ] T091 [US9] Add file type and size validation (10MB max)

**Checkpoint**: Users can add markdown notes and upload file attachments

---

## Phase 12: User Story 10 - Activity Log (Priority: P2)

**Goal**: Users can view task change history (created, completed, priority changed, etc.)

**Independent Test**: Create task, change priority, mark complete, view activity log showing all changes with timestamps

### Implementation for User Story 10

#### Backend

- [ ] T092 [P] [US10] Create TaskActivity model in backend/src/models/task_activity.py (id, task_id, user_id, action, field, old_value, new_value, created_at)
- [ ] T093 [US10] Create ActivityLogService in backend/src/services/activity_log_service.py (log changes, retrieve history)
- [ ] T094 [US10] Create activity log API route in backend/src/api/routes/activity.py (GET /api/tasks/{id}/activity)
- [ ] T095 [US10] Add activity logging hooks to TaskService methods in backend/src/services/task_service.py
- [ ] T096 [US10] Add activity logging hooks to SubtaskService methods in backend/src/services/subtask_service.py

#### Frontend

- [ ] T097 [P] [US10] Create ActivityLog component in frontend/components/ActivityLog.tsx (timeline view of changes)
- [ ] T098 [P] [US10] Create activity API route in frontend/app/api/tasks/[id]/activity/route.ts
- [ ] T099 [US10] Add activity log tab/section to task detail view

**Checkpoint**: Users can view complete change history for tasks

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, testing, and polish across all user stories

- [ ] T100 [P] Update main dashboard to integrate all filters (categories, priority, due date, tags, search)
- [ ] T101 [P] Add keyboard shortcuts for common actions (N for new task, / for search)
- [ ] T102 [P] Implement pagination for task lists (default 50, max 100 per page)
- [ ] T103 [P] Add loading skeletons for async operations
- [ ] T104 [P] Update README.md with Phase 4 features and setup instructions
- [ ] T105 Run full end-to-end test of all 10 user stories via AI chatbot
- [ ] T106 Run database performance analysis (EXPLAIN ANALYZE on search queries)
- [ ] T107 [P] Add rate limiting for file uploads (10 per hour per user)
- [ ] T108 [P] Configure CORS for production deployment
- [ ] T109 Validate quickstart.md steps work from fresh install
- [ ] T110 [P] Create production environment checklist in quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-12)**: All depend on Foundational completion
  - US1-US4 (P0 priorities) can proceed in parallel after Foundational
  - US5-US8 (P1 priorities) can proceed in parallel
  - US9-US10 (P2 priorities) can proceed in parallel
- **Polish (Phase 13)**: Depends on all implemented user stories

### User Story Dependencies

**No blocking dependencies between user stories** - all designed to be independent:

- **US1 (Categories)**: Can start after Foundational - No dependencies
- **US2 (Priorities)**: Can start after Foundational - No dependencies
- **US3 (Due Dates)**: Can start after Foundational - No dependencies
- **US4 (Search)**: Can start after Foundational - No dependencies
- **US5 (Subtasks)**: Can start after Foundational - No dependencies
- **US6 (Statistics)**: Can start after Foundational - No dependencies
- **US7 (Tags)**: Can start after Foundational - No dependencies
- **US8 (Recurring Tasks)**: Can start after Foundational - No dependencies
- **US9 (Attachments)**: Can start after Foundational - No dependencies
- **US10 (Activity Log)**: Can start after Foundational - Optionally logs US5 subtask changes

### Within Each User Story

- Backend models before services
- Services before API routes
- Frontend API routes can be parallel with backend routes
- Frontend components can be parallel
- Integration happens after all components ready

### Parallel Opportunities

- **Setup Phase**: T003, T004, T005 can run in parallel
- **Foundational Phase**: T007, T008, T010, T011, T012, T015 can run in parallel
- **Within each User Story**: Most backend and frontend tasks marked [P] can run in parallel
- **Across User Stories**: After Foundational phase, all 10 user stories can be worked on in parallel by different developers

---

## Parallel Example: User Story 1 (Categories)

```bash
# Launch backend models and frontend components together:
Task: "T016 [P] [US1] Create Category model in backend/src/models/category.py"
Task: "T021 [P] [US1] Create CategoryBadge component in frontend/components/CategoryBadge.tsx"
Task: "T022 [P] [US1] Create categories API route in frontend/app/api/categories/route.ts"

# Then services and routes:
Task: "T017 [US1] Create CategoryService (depends on T016)"
Task: "T018 [US1] Create categories API routes (depends on T017)"
```

---

## Implementation Strategy

### MVP First (P0 User Stories: US1-US4)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T015) - **CRITICAL BLOCKER**
3. Complete Phase 3-6: US1 (Categories), US2 (Priorities), US3 (Due Dates), US4 (Search)
4. **STOP and VALIDATE**: Test all P0 features independently via chatbot
5. Deploy/demo MVP with core organization features

### Incremental Delivery (Add P1 Features)

1. MVP complete (US1-US4)
2. Add Phase 7: US5 (Subtasks) → Test → Deploy
3. Add Phase 8: US6 (Statistics) → Test → Deploy
4. Add Phase 9: US7 (Tags) → Test → Deploy
5. Add Phase 10: US8 (Recurring Tasks) → Test → Deploy

### Full Feature Set (Add P2 Features)

1. All P0 + P1 complete
2. Add Phase 11: US9 (Attachments) → Test → Deploy
3. Add Phase 12: US10 (Activity Log) → Test → Deploy
4. Complete Phase 13: Polish → Final testing → Production deploy

### Parallel Team Strategy

With 4 developers after Foundational phase:

- **Developer A**: US1 (Categories) + US2 (Priorities)
- **Developer B**: US3 (Due Dates) + US4 (Search)
- **Developer C**: US5 (Subtasks) + US6 (Statistics)
- **Developer D**: US7 (Tags) + US8 (Recurring Tasks)

Each developer delivers independently testable features.

---

## Task Summary

**Total Tasks**: 110 tasks across 13 phases

**Tasks per Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 10 tasks (CRITICAL BLOCKER)
- Phase 3 (US1 - Categories): 10 tasks
- Phase 4 (US2 - Priorities): 7 tasks
- Phase 5 (US3 - Due Dates): 7 tasks
- Phase 6 (US4 - Search): 7 tasks
- Phase 7 (US5 - Subtasks): 9 tasks
- Phase 8 (US6 - Statistics): 7 tasks
- Phase 9 (US7 - Tags): 11 tasks
- Phase 10 (US8 - Recurring): 7 tasks
- Phase 11 (US9 - Attachments): 11 tasks
- Phase 12 (US10 - Activity Log): 8 tasks
- Phase 13 (Polish): 11 tasks

**Parallel Tasks**: 42 tasks marked [P] can run in parallel within their phase

**MVP Scope** (Recommended): Phases 1-6 (US1-US4, 51 tasks) delivers core organization features

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Foundational phase (T006-T015) is CRITICAL and BLOCKS all user stories
- AI chatbot enhancements span multiple phases for natural language support
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are explicit for implementation clarity
