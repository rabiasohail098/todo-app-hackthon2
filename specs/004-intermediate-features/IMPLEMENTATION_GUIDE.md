# Phase 4: Intermediate Features - Implementation Guide

**Feature**: 004-intermediate-features
**Status**: Foundation Complete (16/110 tasks - 14.5%)
**Date**: 2025-12-31

---

## 📊 Progress Overview

### Completed: Phases 1-2 (Foundation) ✅

- ✅ **Phase 1: Setup** (5 tasks)
- ✅ **Phase 2: Foundational** (10 tasks) - **CRITICAL BLOCKER CLEARED**
- ✅ **Phase 3: Started** (1/10 tasks - Category model created)

### Remaining: Phases 3-13 (94 tasks)

**MVP Priority (P0)**: 36 tasks
**Enhanced Features (P1)**: 38 tasks
**Advanced Features (P2)**: 20 tasks

---

## 🎯 Implementation Strategy

### Option 1: MVP-First (Recommended)
Complete P0 user stories first for fastest value delivery:
1. **Phase 3**: US1 - Categories (9 remaining)
2. **Phase 4**: US2 - Priorities (7 tasks)
3. **Phase 5**: US3 - Due Dates (7 tasks)
4. **Phase 6**: US4 - Search (7 tasks)
5. **Phase 13**: Polish MVP subset (6 tasks)

**Total MVP**: 36 tasks → **Deployable product with core organization features**

### Option 2: Parallel Development
With multiple developers, implement user stories simultaneously:
- **Developer A**: US1 (Categories) + US2 (Priorities)
- **Developer B**: US3 (Due Dates) + US4 (Search)
- **Developer C**: US5 (Subtasks) + US6 (Statistics)
- **Developer D**: US7 (Tags) + US8 (Recurring Tasks)

### Option 3: Feature-by-Feature
Implement one complete user story at a time, test thoroughly, then move to next.

---

## 📋 Detailed Task Breakdown

### Phase 3: User Story 1 - Task Categories (9 remaining)

**Goal**: Users can create custom categories and organize tasks by category

**Completed**:
- ✅ T016: Category model created

**Remaining Backend** (4 tasks):
```
T017: Create CategoryService in backend/src/services/category_service.py
  - CRUD operations: create, read, update, delete
  - User isolation: filter by user_id
  - Unique constraint: no duplicate category names per user
  - Methods:
    * create_category(user_id, name, color, icon)
    * get_categories(user_id) → List[Category]
    * get_category_by_id(user_id, category_id) → Category
    * update_category(user_id, category_id, updates)
    * delete_category(user_id, category_id)
  - Return CategoryRead schema

T018: Create categories API routes in backend/src/api/routes/categories.py
  - GET /api/categories → List user's categories
  - POST /api/categories → Create category
  - PUT /api/categories/{id} → Update category
  - DELETE /api/categories/{id} → Delete category
  - All routes require JWT authentication
  - Validate request bodies with Pydantic schemas

T019: Update TaskService to support category_id filtering
  - Modify get_tasks() to accept category_id parameter
  - Add .filter(Task.category_id == category_id) when provided
  - Update task creation to accept category_id
  - Update task update to accept category_id

T020: Enhance ChatAgent to parse category from natural language
  - Keywords: "work", "personal", "shopping", "home", "urgent"
  - Pattern: "add [category] task [title]"
  - Example: "add work task deploy app" → category=Work
  - If category doesn't exist, create it automatically
  - Store category mapping in conversation context
```

**Remaining Frontend** (5 tasks):
```
T021 [P]: Create CategoryBadge component in frontend/components/CategoryBadge.tsx
  - Props: { category: { name, color, icon } }
  - Visual: Rounded badge with icon, name, colored border
  - Size variants: small, medium, large
  - Click handler for filtering

T022 [P]: Create categories API route in frontend/app/api/categories/route.ts
  - GET handler: fetch all categories from backend
  - POST handler: create new category
  - Forward requests to backend /api/categories

T023: Create category management page in frontend/app/dashboard/categories/page.tsx
  - List all categories in grid layout
  - "Add Category" button with modal/form
  - Edit category (click to edit inline or modal)
  - Delete category with confirmation
  - Color picker for category color
  - Emoji picker for category icon

T024: Add category filter to TaskFilters component
  - Create TaskFilters.tsx if not exists
  - Dropdown/checkbox list of categories
  - Multiple categories selectable
  - Update task list on selection

T025: Update task creation/editing to include category selection
  - Add category dropdown to task form
  - Show selected category with badge
  - Allow clearing category (set to null)
```

**Checkpoint**: Test category creation, assignment, and filtering end-to-end

---

### Phase 4: User Story 2 - Task Priority Levels (7 tasks)

**Goal**: Users can assign priority levels (Critical, High, Medium, Low) to tasks

**Backend** (3 tasks):
```
T026: Update TaskService to support priority filtering and sorting
  - Add get_tasks(priority=None, sort_by=None)
  - Filter: .filter(Task.priority == priority)
  - Sort: .order_by(Task.priority.desc()) for high→low
  - Priority order: critical > high > medium > low

T027: Update tasks API routes to accept priority parameter
  - GET /api/tasks?priority=high
  - GET /api/tasks?sort=priority
  - Validate priority values against TaskPriority enum

T028: Enhance ChatAgent to parse priority keywords
  - Keywords: "critical", "urgent", "high", "important", "low", "minor"
  - Pattern: "[priority] priority task [title]"
  - Example: "add high priority task fix bug"
  - Use TaskPriority.from_natural_language()
```

**Frontend** (4 tasks):
```
T029 [P]: Create PriorityIndicator component in frontend/components/PriorityIndicator.tsx
  - Visual: Icon + color coding
    * Critical: 🔴 Red
    * High: 🟠 Orange
    * Medium: 🟡 Yellow
    * Low: 🟢 Green
  - Size variants: icon-only, with-label

T030: Add priority filter to TaskFilters component
  - Checkbox group: Critical, High, Medium, Low
  - Multi-select supported

T031: Update task creation/editing forms to include priority selector
  - Dropdown or radio buttons
  - Default: Medium
  - Visual preview with PriorityIndicator

T032: Add priority sorting option to dashboard
  - Sort dropdown: "Priority (High to Low)", "Priority (Low to High)"
  - Apply sorting to task list
```

**Checkpoint**: Test priority assignment, filtering, and sorting

---

### Phase 5: User Story 3 - Due Dates & Reminders (7 tasks)

**Goal**: Users can set due dates for tasks and see overdue tasks highlighted

**Backend** (3 tasks):
```
T033: Update TaskService to support due_date filtering
  - Add filters: due_today, due_this_week, overdue
  - Use date_parser.get_due_this_week() for week range
  - Overdue: .filter(Task.due_date < datetime.utcnow(), Task.is_completed == False)

T034: Update tasks API routes to accept due_date filters
  - GET /api/tasks?due=today
  - GET /api/tasks?due=this_week
  - GET /api/tasks?overdue=true
  - GET /api/tasks?due_date_from=2025-01-01&due_date_to=2025-12-31

T035: Enhance ChatAgent to parse natural language dates
  - Use date_parser.parse_natural_date()
  - Patterns: "tomorrow", "next Friday", "in 3 days"
  - Example: "add task due tomorrow buy groceries"
  - Store parsed datetime in Task.due_date
```

**Frontend** (4 tasks):
```
T036 [P]: Create DueDateDisplay component in frontend/components/DueDateDisplay.tsx
  - Show formatted date
  - Color coding:
    * Overdue: Red background
    * Due today: Orange
    * Due this week: Yellow
    * Future: Gray
  - Show relative text: "due tomorrow", "overdue by 3 days"

T037: Add due date filters to TaskFilters component
  - Quick filters: Today, This Week, Overdue
  - Custom date range picker

T038: Update task creation/editing forms to include date picker
  - Date + time picker
  - Quick options: Tomorrow, Next Week, Custom
  - Clear button to remove due date

T039: Add due date sorting option
  - Sort: "Due Date (Soonest First)", "Due Date (Latest First)"
  - Show overdue tasks at top when sorted by soonest
```

**Checkpoint**: Test due date assignment, overdue detection, and date-based filtering

---

### Phase 6: User Story 4 - Task Search (7 tasks)

**Goal**: Users can search tasks by keywords in title/description with fuzzy matching

**Backend** (3 tasks):
```
T040: Create SearchService in backend/src/services/search_service.py
  - Method: search_tasks(user_id, query, filters)
  - Use PostgreSQL full-text search (tsvector already set up)
  - Query: Task.search_vector.op('@@')(func.to_tsquery('english', query))
  - Ranking: ORDER BY ts_rank(search_vector, query) DESC
  - Pagination: LIMIT 20 by default
  - Combine with other filters (category, priority, tags)

T041: Create search API route in backend/src/api/routes/search.py
  - GET /api/tasks/search?q={query}&category={}&priority={}
  - Return results sorted by relevance
  - Include highlighted snippets (ts_headline)

T042: Enhance ChatAgent to detect search intent
  - Keywords: "find", "search", "show me", "where is"
  - Pattern: "find tasks about [query]"
  - Example: "find tasks about meeting"
  - Call SearchService.search_tasks()
```

**Frontend** (4 tasks):
```
T043 [P]: Create SearchBar component in frontend/components/SearchBar.tsx
  - Input with search icon
  - Real-time search with debounce (300ms)
  - Clear button when text entered
  - Show search results count

T044: Create search API route in frontend/app/api/search/route.ts
  - GET handler: forward to backend /api/tasks/search
  - Pass query and filters

T045: Add SearchBar to dashboard header
  - Prominent position (top of page)
  - Keyboard shortcut: / to focus
  - ESC to clear

T046: Implement search results display with highlighted matches
  - Show matching tasks in list
  - Highlight query terms in title/description
  - Show relevance score or match count
  - "No results" state with suggestions
```

**Checkpoint**: Test search functionality with various queries and filters

---

### MVP Completion Checkpoint

**After completing Phases 3-6 (US1-US4):**

✅ Users can:
- Create and organize tasks into categories
- Assign priority levels (Critical/High/Medium/Low)
- Set due dates and view overdue tasks
- Search tasks by keywords with fuzzy matching

**Test thoroughly before moving to P1 features:**
1. Create tasks via UI and chatbot
2. Assign categories, priorities, due dates
3. Filter by each dimension
4. Search for tasks
5. Verify data persists and syncs correctly

---

### Phase 7: User Story 5 - Subtasks (9 tasks)

**Backend** (5 tasks):
```
T047 [P]: Create Subtask model in backend/src/models/subtask.py
  - Fields: id, parent_task_id, title, is_completed, order
  - Relationships: parent_task (Task)

T048: Create SubtaskService in backend/src/services/subtask_service.py
  - create_subtask(task_id, title, order)
  - get_subtasks(task_id) → List[Subtask]
  - update_subtask(subtask_id, updates)
  - toggle_completion(subtask_id)
  - delete_subtask(subtask_id)
  - calculate_progress(task_id) → {completed: int, total: int, percentage: float}

T049: Create subtasks API routes in backend/src/api/routes/subtasks.py
  - POST /api/tasks/{id}/subtasks
  - PUT /api/tasks/{task_id}/subtasks/{subtask_id}
  - DELETE /api/tasks/{task_id}/subtasks/{subtask_id}
  - PUT /api/tasks/{task_id}/subtasks/{subtask_id}/complete

T050: Update TaskService to calculate subtask progress
  - Add get_task_with_progress(task_id)
  - Include subtask completion percentage
  - Update TaskRead schema to include progress

T051: Enhance ChatAgent to handle subtask commands
  - Pattern: "add subtask to task [id]: [title]"
  - Pattern: "show subtasks of task [id]"
  - Pattern: "complete subtask [id]"
```

**Frontend** (4 tasks):
```
T052 [P]: Create SubtaskList component in frontend/components/SubtaskList.tsx
  - List of subtasks with checkboxes
  - Add new subtask inline input
  - Drag-and-drop reordering
  - Progress bar showing X/Y completed
  - Delete subtask button

T053 [P]: Create subtasks API route in frontend/app/api/tasks/[id]/subtasks/route.ts
  - POST, PUT, DELETE handlers

T054: Add subtasks section to task detail view
  - Expandable section in task card/modal
  - Show SubtaskList component
  - Real-time progress updates

T055: Implement subtask creation UI in task detail
  - "Add Subtask" button
  - Inline input field
  - Enter to save, ESC to cancel
```

---

### Phase 8: User Story 6 - Task Statistics (7 tasks)

**Backend** (2 tasks):
```
T056: Create StatisticsService in backend/src/services/statistics_service.py
  - get_user_statistics(user_id, from_date, to_date)
  - Metrics:
    * total_tasks, completed_tasks, completion_rate
    * tasks_completed_this_week
    * average_completion_time (created_at → completed_at)
    * most_productive_day (day of week with most completions)
    * tasks_by_priority {critical: N, high: N, ...}
    * tasks_by_category [{name, count}, ...]
    * completion_trend (daily counts for chart)

T057: Create statistics API route in backend/src/api/routes/statistics.py
  - GET /api/statistics?from=YYYY-MM-DD&to=YYYY-MM-DD
  - Default: last 30 days
  - Return JSON with all metrics
```

**Frontend** (5 tasks):
```
T058 [P]: Create StatisticsChart component in frontend/components/StatisticsChart.tsx
  - Use Recharts library
  - Chart types:
    * BarChart: Tasks completed per day
    * PieChart: Completion rate, tasks by priority
    * LineChart: Productivity trend over time
  - Responsive design

T059 [P]: Create statistics API route in frontend/app/api/statistics/route.ts
  - GET handler: fetch from backend

T060: Create statistics dashboard page in frontend/app/dashboard/statistics/page.tsx
  - Header with date range selector
  - Grid layout:
    * Summary cards (total, completed, rate)
    * Completion trend chart
    * Tasks by priority pie chart
    * Tasks by category bar chart
    * Most productive day badge

T061: Add statistics cards
  - Total tasks, Completed, Completion rate, Overdue count, Due today
  - Large numbers with icons
  - Color-coded

T062: Implement date range filter for statistics
  - Quick options: Last 7 days, Last 30 days, This month, Custom
  - Update all charts on selection
```

---

### Phase 9: User Story 7 - Task Tags (11 tasks)

**Backend** (6 tasks):
```
T063 [P]: Create Tag model in backend/src/models/tag.py
  - Fields: id, user_id, name
  - Unique constraint: (user_id, name)

T064 [P]: Create TaskTag join model in backend/src/models/task_tag.py
  - Many-to-many relationship
  - Fields: task_id, tag_id

T065: Create TagService in backend/src/services/tag_service.py
  - create_or_get_tag(user_id, name) → Tag
  - get_all_tags(user_id) → List[Tag]
  - add_tag_to_task(task_id, tag_name)
  - remove_tag_from_task(task_id, tag_id)
  - get_task_tags(task_id) → List[Tag]
  - suggest_tags(user_id, query) → List[Tag] (autocomplete)

T066: Create tags API routes in backend/src/api/routes/tags.py
  - GET /api/tags → List all user's tags
  - POST /api/tasks/{id}/tags → Add tag to task
  - DELETE /api/tasks/{task_id}/tags/{tag_id} → Remove tag

T067: Update TaskService to support tag filtering
  - get_tasks(tags=[]) → Filter by tags
  - Join through task_tags table

T068: Enhance ChatAgent to parse hashtags
  - Pattern: "#tagname" in message
  - Example: "add task #urgent #meeting schedule call"
  - Auto-create tags if not exists
```

**Frontend** (5 tasks):
```
T069 [P]: Create TagInput component in frontend/components/TagInput.tsx
  - Multi-select input with autocomplete
  - Show existing tags as chips
  - Type to search/create new tags
  - Remove tag by clicking X on chip

T070 [P]: Create tags API routes
  - frontend/app/api/tags/route.ts (GET)
  - frontend/app/api/tasks/[id]/tags/route.ts (POST, DELETE)

T071: Add tag filter to TaskFilters component
  - Show all user's tags
  - Multi-select checkboxes
  - Search/filter tags

T072: Update task creation/editing forms to include tag input
  - Show TagInput component
  - Save tags when task is created/updated

T073: Make tags clickable to filter by that tag
  - Click tag chip → filter tasks by tag
  - Show active tag filters
  - Clear filters button
```

---

### Phase 10: User Story 8 - Recurring Tasks (7 tasks)

**Backend** (4 tasks):
```
T074: Update TaskService to handle recurrence_pattern and next_recurrence_date
  - create_task() → Set next_recurrence_date if recurrence_pattern provided
  - Use recurrence.calculate_next_occurrence()

T075: Create recurring task generation job in backend/src/jobs/generate_recurring_tasks.py
  - Already configured in main.py (T015)
  - Refactor job logic to separate file
  - Add logging for each generated occurrence

T076: Register APScheduler job in backend/src/api/main.py
  - Already done in T015
  - Update to use refactored job file

T077: Enhance ChatAgent to parse recurrence patterns
  - Keywords: "daily", "weekly", "monthly", "every day", "every week"
  - Pattern: "[frequency] task [title]"
  - Example: "add daily task take vitamin"
  - Use RecurrencePattern.from_natural_language()
```

**Frontend** (3 tasks):
```
T078 [P]: Create RecurrenceSelector component in frontend/components/RecurrenceSelector.tsx
  - Dropdown: None, Daily, Weekly, Monthly
  - For weekly: select day of week
  - For monthly: select day of month
  - Interval input: "Every [N] [days/weeks/months]"

T079: Update task creation form to include recurrence selector
  - Show RecurrenceSelector when creating task
  - Preview next 5 occurrences

T080: Display next occurrence date for recurring tasks
  - Show in task detail view
  - Badge: "Recurs daily" with next date
  - Option to stop recurrence
```

---

### Phase 11: User Story 9 - Task Notes & Attachments (11 tasks)

**Backend** (5 tasks):
```
T081 [P]: Create Attachment model in backend/src/models/attachment.py
  - Fields: id, task_id, filename, file_path, file_size, mime_type

T082: Create AttachmentService in backend/src/services/attachment_service.py
  - upload_file(task_id, file, filename) → Attachment
    * Validate using file_validator
    * Upload to Cloudinary
    * Save metadata to database
  - delete_file(attachment_id)
    * Delete from Cloudinary
    * Delete from database
  - get_attachment_url(attachment_id) → Cloudinary URL

T083: Create attachments API routes in backend/src/api/routes/attachments.py
  - POST /api/tasks/{id}/attachments (multipart/form-data)
  - GET /api/tasks/{task_id}/attachments/{attachment_id} (redirect to Cloudinary)
  - DELETE /api/tasks/{task_id}/attachments/{attachment_id}

T084: Update Task model to include notes field
  - Already done in T009 (notes: Optional[str])
  - Update TaskUpdate schema

T085: Enhance ChatAgent to handle "add note to task X" commands
  - Pattern: "add note to task [id]: [note text]"
  - Support markdown in notes
```

**Frontend** (6 tasks):
```
T086 [P]: Add react-markdown support for rendering notes
  - Already installed in T002
  - Create MarkdownRenderer component

T087 [P]: Create attachments API routes in frontend/app/api/tasks/[id]/attachments/route.ts
  - POST (upload), GET (download), DELETE handlers

T088: Add markdown notes editor to task detail
  - Textarea for editing
  - Preview tab using react-markdown
  - Save button

T089: Implement file upload UI for attachments
  - Drag-and-drop zone
  - File picker button
  - Progress indicator during upload
  - File type/size validation client-side

T090: Display attached files with download links
  - List of files with icons (based on mime type)
  - Download button
  - Delete button with confirmation
  - File size display

T091: Add file type and size validation
  - Check before upload (10MB max)
  - Show error messages for invalid files
```

---

### Phase 12: User Story 10 - Activity Log (8 tasks)

**Backend** (5 tasks):
```
T092 [P]: Create TaskActivity model in backend/src/models/task_activity.py
  - Already created in migration
  - Create Pydantic schemas

T093: Create ActivityLogService in backend/src/services/activity_log_service.py
  - log_activity(task_id, user_id, action, field, old_value, new_value)
  - get_task_activities(task_id) → List[TaskActivity]
  - Cleanup old activities (>1 year)

T094: Create activity log API route in backend/src/api/routes/activity.py
  - GET /api/tasks/{id}/activity

T095: Add activity logging hooks to TaskService methods
  - Log on: create, update (track field changes), complete, delete
  - Call ActivityLogService.log_activity() after each operation

T096: Add activity logging hooks to SubtaskService methods
  - Log on: subtask added, subtask completed
```

**Frontend** (3 tasks):
```
T097 [P]: Create ActivityLog component in frontend/components/ActivityLog.tsx
  - Timeline view of changes
  - Show: timestamp, user, action, field changed, old→new values
  - Icon for each action type

T098 [P]: Create activity API route in frontend/app/api/tasks/[id]/activity/route.ts
  - GET handler

T099: Add activity log tab/section to task detail view
  - Expandable section
  - Show ActivityLog component
  - Load on expand (lazy)
```

---

### Phase 13: Polish & Cross-Cutting Concerns (11 tasks)

```
T100 [P]: Update main dashboard to integrate all filters
  - Sidebar with all filter options
  - Active filters display
  - Clear all filters button

T101 [P]: Add keyboard shortcuts for common actions
  - N → New task
  - / → Focus search
  - ESC → Close modals
  - Create shortcuts help modal (?)

T102 [P]: Implement pagination for task lists
  - Default: 50 tasks per page
  - Load more button / infinite scroll
  - Page indicator

T103 [P]: Add loading skeletons for async operations
  - Task list skeleton
  - Statistics skeleton
  - Smooth transitions

T104 [P]: Update README.md with Phase 4 features
  - Feature list
  - Setup instructions
  - API documentation

T105: Run full end-to-end test of all 10 user stories via AI chatbot
  - Test each feature through natural language
  - Verify responses
  - Document any issues

T106: Run database performance analysis
  - EXPLAIN ANALYZE on search queries
  - Check index usage
  - Optimize slow queries

T107 [P]: Add rate limiting for file uploads
  - 10 uploads per hour per user
  - Return 429 Too Many Requests
  - Client-side warning

T108 [P]: Configure CORS for production deployment
  - Update CORS_ORIGINS env variable
  - Add production domain

T109: Validate quickstart.md steps work from fresh install
  - Follow guide step-by-step
  - Update any outdated instructions

T110 [P]: Create production environment checklist
  - Environment variables
  - Database backups
  - Monitoring setup
  - Error tracking (Sentry)
```

---

## 🧪 Testing Strategy

### Unit Tests
- **Services**: Test each service method with mocked database
- **Utilities**: Test date parsing, file validation, recurrence calculation
- **Models**: Test validation and constraints

### Integration Tests
- **API Endpoints**: Test each endpoint with real database (test DB)
- **Chatbot**: Test natural language parsing for each feature
- **Background Jobs**: Test recurring task generation

### End-to-End Tests
- **User Flows**: Complete task lifecycle (create → edit → complete)
- **Feature Interactions**: Categories + priorities + due dates + search
- **Performance**: Test with 1000+ tasks

---

## 📦 Deployment Checklist

### Before Production Deploy

1. **Database**
   - [ ] Run migration on production DB
   - [ ] Verify all indexes created
   - [ ] Set up automated backups
   - [ ] Test rollback procedure

2. **Environment**
   - [ ] Set all environment variables
   - [ ] Configure Cloudinary production credentials
   - [ ] Update CORS_ORIGINS for production domain
   - [ ] Set up SSL/TLS certificates

3. **Services**
   - [ ] Verify APScheduler running
   - [ ] Test file uploads to Cloudinary
   - [ ] Test full-text search performance
   - [ ] Configure rate limiting

4. **Monitoring**
   - [ ] Set up error tracking (Sentry)
   - [ ] Configure logging (aggregation)
   - [ ] Database query monitoring
   - [ ] APScheduler job monitoring

5. **Testing**
   - [ ] Run full test suite
   - [ ] Load testing (1000+ tasks)
   - [ ] Test all chatbot commands
   - [ ] Verify search performance (<200ms)

---

## 💡 Implementation Tips

### Best Practices

1. **Commit Frequently**: After each task or logical group
2. **Test As You Go**: Don't wait until end to test
3. **Use Type Safety**: Leverage Pydantic and TypeScript
4. **Document As You Build**: Add docstrings and comments
5. **Handle Errors Gracefully**: Proper error messages for users

### Common Patterns

**Backend Service**:
```python
class ExampleService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: str, data: ExampleCreate) -> Example:
        obj = Example(**data.dict(), user_id=user_id)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, user_id: str, id: int) -> Optional[Example]:
        return self.session.query(Example).filter(
            Example.user_id == user_id,
            Example.id == id
        ).first()
```

**Backend API Route**:
```python
@router.post("/examples", response_model=ExampleRead)
async def create_example(
    data: ExampleCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    service = ExampleService(session)
    example = service.create(current_user.id, data)
    return example
```

**Frontend API Route**:
```typescript
export async function GET(request: Request) {
  const res = await fetch(`${BACKEND_URL}/api/examples`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return Response.json(await res.json());
}
```

**React Component**:
```typescript
export function ExampleComponent() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('/api/examples')
      .then(res => res.json())
      .then(setData);
  }, []);

  return <div>{data.map(item => ...)}</div>;
}
```

---

## 🚨 Troubleshooting

### Common Issues

**Database Migration Fails**:
- Check DATABASE_URL is correct
- Verify PostgreSQL version supports tsvector
- Run migration script directly with psql

**APScheduler Not Running**:
- Check logs for scheduler startup message
- Verify no port conflicts
- Test job manually: `generate_recurring_tasks()`

**Full-Text Search Not Working**:
- Verify GIN index created: `\d tasks` in psql
- Check search_vector column populated
- Run UPDATE to rebuild vectors

**File Upload Fails**:
- Verify Cloudinary credentials
- Check file size < 10MB
- Verify MIME type allowed

**Chatbot Not Parsing Correctly**:
- Add logging to chat_agent.py
- Test regex patterns individually
- Check AI model response format

---

## 📚 Resources

### Documentation
- [python-dateutil](https://dateutil.readthedocs.io/)
- [Recharts](https://recharts.org/)
- [Cloudinary Python SDK](https://cloudinary.com/documentation/python_integration)
- [APScheduler](https://apscheduler.readthedocs.io/)
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [React-Markdown](https://github.com/remarkjs/react-markdown)

### Files Reference
- **Spec**: `specs/004-intermediate-features/spec.md`
- **Data Model**: `specs/004-intermediate-features/data-model.md`
- **Plan**: `specs/004-intermediate-features/plan.md`
- **Research**: `specs/004-intermediate-features/research.md`
- **API Contract**: `specs/004-intermediate-features/contracts/api.yaml`
- **Quickstart**: `specs/004-intermediate-features/quickstart.md`
- **Tasks**: `specs/004-intermediate-features/tasks.md`

---

**Guide Status**: ✅ Complete
**Last Updated**: 2025-12-31
**Estimated Total Time**: 40-60 hours for full implementation
**MVP Time**: 15-20 hours (Phases 3-6 only)
