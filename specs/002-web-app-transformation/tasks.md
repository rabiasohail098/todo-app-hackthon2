---

description: "Task list for Web Application Transformation feature implementation"

---

# Tasks: Web Application Transformation

**Input**: Design documents from `specs/002-web-app-transformation/`
**Prerequisites**: spec.md, plan.md, data-model.md, contracts/api.yaml, research.md, quickstart.md

**Tests**: No automated tests in initial implementation - focus on manual testing via API clients and browser. Contract tests can be added in future phases.

**Organization**: Tasks are grouped by phase: Setup → Foundational → User Stories (P1 first, then P2) → Polish. Each phase represents independently testable functionality.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1-US8) - only for story phases
- Include exact file paths in descriptions

## Path Conventions

- **Web application**: `backend/src/`, `frontend/src/` at repository root
- Backend: Python with FastAPI + SQLModel
- Frontend: TypeScript with Next.js 16+ App Router
- Paths shown below are based on plan.md structure

---

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Initialize backend and frontend project structures, dependencies, and configuration

- [x] T001 Create backend directory structure: backend/src/{models,services,api/routes,db/migrations}, backend/tests/{unit,integration}
- [x] T002 Create frontend directory structure using create-next-app: frontend/src/app/{auth,dashboard}, frontend/src/{components,lib,types}
- [x] T003 [P] Create backend/pyproject.toml with dependencies: FastAPI 0.109+, SQLModel 0.0.14+, uvicorn, psycopg2-binary, python-jose, python-dotenv, alembic, pytest
- [x] T004 [P] Create frontend/package.json with dependencies: Next.js 16+, better-auth, TypeScript, Tailwind CSS, React
- [x] T005 [P] Create backend/.env.example with DATABASE_URL, JWT_SECRET, CORS_ORIGINS placeholders
- [x] T006 [P] Create frontend/.env.local.example with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET placeholders
- [x] T007 [P] Configure Tailwind CSS in frontend/tailwind.config.ts with custom theme colors
- [x] T008 Create .gitignore entries for backend/.env and frontend/.env.local

---

## Phase 2: Foundational (Core Infrastructure - BLOCKS ALL USER STORIES)

**Purpose**: Database connection, authentication framework, API infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Foundation

- [x] T009 Create backend/src/db/session.py with Neon PostgreSQL connection using SQLAlchemy engine (pool_pre_ping=True, pool_recycle=300)
- [x] T010 Initialize Alembic in backend/src/db/migrations/ with alembic.ini configuration pointing to Neon DATABASE_URL
- [x] T011 Create backend/src/models/task.py with SQLModel Task entity: id (SERIAL PK), user_id (UUID FK, indexed), title (VARCHAR 200), description (TEXT nullable), is_completed (BOOLEAN default false), created_at (TIMESTAMP)

### API Foundation

- [x] T012 Create backend/src/api/main.py with FastAPI app initialization, CORS middleware configuration (allow_origins from env, allow_credentials=True)
- [x] T013 Create backend/src/api/deps.py with get_db() dependency (database session management) and get_current_user() dependency (JWT validation, extracts user_id from token)
- [x] T014 Create backend/src/api/routes/__init__.py to organize route modules
- [x] T015 [P] Add health check endpoint GET /health in backend/src/api/routes/health.py (no authentication required, returns {status: ok, timestamp})

### Frontend Foundation

- [x] T016 [P] Create frontend/lib/api.ts with fetch wrapper function that automatically attaches Authorization header from Better Auth session
- [x] T017 [P] Create frontend/lib/auth.ts with Better Auth configuration (JWT secret from env, 24-hour expiration)
- [x] T018 [P] Create frontend/types/index.ts with TypeScript interfaces: Task, TaskCreate, TaskUpdate, User (matching backend Pydantic models)

**Checkpoint**: Foundation ready - database connected, API running, frontend configured, JWT framework in place

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: New users can create accounts with email/password; system validates input and prevents duplicates

**Independent Test**: Navigate to sign-up page, enter email "test@example.com" and password "password123", submit, verify: (1) user record created in database, (2) JWT token issued, (3) redirected to dashboard

### Frontend Implementation

- [x] T019 [US1] Create frontend/src/app/auth/sign-up/page.tsx with sign-up form UI (email input, password input, submit button)
- [x] T020 [US1] Implement client-side validation in sign-up form: email format validation (regex), password minimum 8 characters, display inline error messages
- [x] T021 [US1] Integrate Better Auth sign-up flow in frontend/src/app/auth/sign-up/page.tsx (call Better Auth createUser, handle success/error responses)

### Backend Integration

- [ ] T022 [US1] Configure Better Auth to use Neon PostgreSQL for user storage (users table with id UUID, email unique, password_hash)
- [ ] T023 [US1] Test registration flow end-to-end: submit valid credentials → verify user created in database → JWT token returned → token contains user_id claim

**Checkpoint**: User Story 1 complete - users can register with validation and receive JWT

---

## Phase 4: User Story 2 - User Sign-In (Priority: P1) 🎯 MVP

**Goal**: Registered users can authenticate with email/password and receive JWT for accessing protected resources

**Independent Test**: With existing user "test@example.com", navigate to sign-in page, enter correct credentials, verify: (1) JWT issued, (2) token stored in httpOnly cookie, (3) redirected to dashboard

### Frontend Implementation

- [x] T024 [US2] Create frontend/src/app/auth/sign-in/page.tsx with sign-in form UI (email input, password input, submit button, link to sign-up)
- [x] T025 [US2] Implement Better Auth sign-in flow in sign-in page (call Better Auth signIn method, handle invalid credentials error with generic message)
- [x] T026 [US2] Configure session persistence: JWT stored in httpOnly cookie, automatic header attachment via api.ts wrapper

### Backend JWT Verification

- [ ] T027 [US2] Implement JWT verification in backend/src/api/deps.py get_current_user(): extract token from Authorization header, verify signature using JWT_SECRET, check expiration, extract user_id claim
- [ ] T028 [US2] Add error handling for invalid JWT: return 401 Unauthorized for missing/expired/malformed tokens with error message "Invalid or expired token"
- [ ] T029 [US2] Test sign-in flow end-to-end: submit correct credentials → JWT issued → token verified by backend → user_id extracted

**Checkpoint**: User Stories 1 & 2 complete - full authentication loop working (register → sign in → JWT → verification)

---

## Phase 5: User Story 3 - Create Task (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can add tasks with title and optional description; tasks are isolated per user

**Independent Test**: Sign in, click "Add Task", enter title "Buy groceries", submit, verify: (1) task appears in list, (2) task stored in database with correct user_id, (3) created_at timestamp set

### Backend API

- [x] T030 [US3] Create backend/src/services/task_service.py with create_task(session, user_id, task_create) function: validates title non-empty, assigns user_id from JWT (not request body), saves to database
- [x] T031 [US3] Create POST /api/tasks endpoint in backend/src/api/routes/tasks.py: requires authentication (depends on get_current_user), accepts TaskCreate schema, calls task_service.create_task(), returns 201 with created Task
- [x] T032 [US3] Add input validation in POST /api/tasks: title required (non-empty), title max 200 chars, description optional (nullable), return 400 Bad Request with validation errors

### Frontend UI

- [x] T033 [US3] Create frontend/src/components/TaskForm.tsx with controlled form inputs: title (required), description (optional textarea), submit button
- [x] T034 [US3] Implement form submission in TaskForm: call POST /api/tasks via api.ts wrapper, handle validation errors (display inline), handle success (clear form, show success message)
- [x] T035 [US3] Add TaskForm component to dashboard page (frontend/src/app/dashboard/page.tsx)

### Database Migration

- [x] T036 [US3] Create Alembic migration in backend/src/db/migrations/versions/001_create_tasks_table.py: CREATE TABLE tasks with all columns, CREATE INDEX idx_tasks_user_id, CREATE INDEX idx_tasks_created_at

**Checkpoint**: User Story 3 complete - users can create tasks that are automatically isolated by user_id

---

## Phase 6: User Story 4 - View Tasks (Priority: P1) 🎯 MVP

**Goal**: Authenticated users see all their tasks in a clean list with visual distinction for completed vs pending

**Independent Test**: Sign in as user with 5 tasks (3 pending, 2 completed), view dashboard, verify: (1) all 5 tasks displayed, (2) completed tasks have strikethrough styling, (3) NO tasks from other users shown

### Backend API

- [x] T037 [US4] Implement get_tasks_for_user(session, user_id) in backend/src/services/task_service.py: query with WHERE user_id = current_user (Golden Rule), ORDER BY created_at DESC
- [x] T038 [US4] Create GET /api/tasks endpoint in backend/src/api/routes/tasks.py: requires authentication, calls task_service.get_tasks_for_user() with user_id from JWT, returns list of TaskRead schemas

### Frontend UI

- [x] T039 [US4] Create frontend/src/components/TaskItem.tsx to display single task: title, description (if present), completion checkbox, created_at timestamp
- [x] T040 [US4] Create frontend/src/components/TaskList.tsx to display array of tasks: map over tasks array, render TaskItem for each, handle empty state "No tasks yet. Add your first task!"
- [x] T041 [US4] Implement data fetching in frontend/src/app/dashboard/page.tsx: call GET /api/tasks on mount, store in React state, pass to TaskList component
- [x] T042 [US4] Add conditional styling in TaskItem: apply line-through (strikethrough) text decoration when is_completed is true, normal styling when false

**Checkpoint**: User Stories 1-4 complete - users can register, sign in, create tasks, and view their task list (MVP core functionality ready)

---

## Phase 7: User Story 5 - Toggle Task Completion (Priority: P1) 🎯 MVP

**Goal**: Users can mark tasks as complete/incomplete with immediate visual feedback

**Independent Test**: View task "Buy groceries" (pending), click completion checkbox, verify: (1) is_completed changes to true in database, (2) strikethrough styling applied immediately, (3) toggle reversible

### Backend API

- [x] T043 [US5] Implement update_task(session, user_id, task_id, task_update) in backend/src/services/task_service.py: query with WHERE task_id AND user_id (ownership check), update fields from TaskUpdate schema, return updated Task or None
- [x] T044 [US5] Create PATCH /api/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py: requires authentication, accepts TaskUpdate schema, calls task_service.update_task(), returns 200 with updated Task or 404 if not found/wrong user

### Frontend UI

- [x] T045 [US5] Add completion toggle handler to TaskItem component: onClick event for checkbox, call PATCH /api/tasks/{id} with {is_completed: !current}, optimistic UI update (update state immediately)
- [x] T046 [US5] Implement error handling for toggle: on API failure, rollback optimistic update, display error toast/message
- [ ] T047 [US5] Test toggle behavior: pending → completed (strikethrough applied), completed → pending (strikethrough removed), verify database persists changes

**Checkpoint**: All P1 user stories complete - full MVP ready (authentication + task CRUD + completion tracking)

---

## Phase 8: User Story 6 - Update Task (Priority: P2)

**Goal**: Users can edit existing task title and description

**Independent Test**: Click edit on task "Buy groceries", change title to "Buy groceries and cook", save, verify: (1) title updated in UI, (2) changes persisted to database, (3) ownership enforced (cannot edit other users' tasks)

### Frontend UI

- [x] T048 [US6] Add edit mode state to TaskItem component: toggle between view mode and edit mode, show text inputs when editing
- [x] T049 [US6] Create inline edit form in TaskItem: prefill current title/description, save button, cancel button
- [x] T050 [US6] Implement update submission: call PATCH /api/tasks/{id} with new title/description, validate title non-empty client-side, handle 403 Forbidden (ownership violation)

### Backend Validation

- [x] T051 [US6] Add ownership check in update_task service: return None if task.user_id != current_user_id (prevents cross-user updates)
- [ ] T052 [US6] Test update flow: valid update succeeds, empty title rejected (400), updating other user's task returns 403

**Checkpoint**: User Story 6 complete - users can edit task details

---

## Phase 9: User Story 7 - Delete Task (Priority: P2)

**Goal**: Users can permanently remove tasks with confirmation

**Independent Test**: Click delete on task "Buy groceries", confirm deletion, verify: (1) task removed from UI, (2) task removed from database, (3) ownership enforced

### Backend API

- [x] T053 [US7] Implement delete_task(session, user_id, task_id) in backend/src/services/task_service.py: query with WHERE task_id AND user_id, delete if found, return True/False
- [x] T054 [US7] Create DELETE /api/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py: requires authentication, calls task_service.delete_task(), returns 204 No Content or 404

### Frontend UI

- [x] T055 [US7] Add delete button to TaskItem component with confirmation dialog: "Are you sure you want to delete this task?"
- [x] T056 [US7] Implement delete handler: call DELETE /api/tasks/{id}, remove from local state on success, handle 403/404 errors
- [ ] T057 [US7] Test deletion: successful delete removes task, deleting other user's task returns 403

**Checkpoint**: User Story 7 complete - users can delete tasks

---

## Phase 10: User Story 8 - User Logout (Priority: P2)

**Goal**: Users can log out securely, clearing session and redirecting to landing page

**Independent Test**: Click "Log Out" button, verify: (1) JWT removed from storage, (2) redirected to landing page, (3) accessing /dashboard redirects to sign-in

### Frontend Implementation

- [x] T058 [US8] Add logout button to dashboard navigation in frontend/src/app/dashboard/page.tsx
- [x] T059 [US8] Implement logout handler: call Better Auth signOut method, clear session storage, redirect to landing page (/)
- [x] T060 [US8] Add route protection middleware in frontend/src/middleware.ts: check for valid session, redirect unauthenticated users from /dashboard to /auth/sign-in

### Testing

- [ ] T061 [US8] Test logout flow: sign in → navigate to dashboard → log out → verify JWT cleared → attempt to access /dashboard → redirected to sign-in
- [ ] T062 [US8] Test browser back button after logout: cannot access protected content (session fully invalidated)

**Checkpoint**: All user stories complete - full feature set implemented

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, UI improvements, documentation, security hardening

### Error Handling

- [x] T063 [P] Implement global error handler in backend/src/api/main.py: catch all exceptions, return appropriate HTTP status codes, log errors without exposing internals
- [ ] T064 [P] Add error toast notifications in frontend: create Toast component in frontend/src/components/Toast.tsx, integrate with API error responses

### UI/UX Improvements

- [x] T065 [P] Create landing page in frontend/src/app/page.tsx: hero section, "Sign Up" and "Sign In" buttons, feature highlights
- [ ] T066 [P] Add loading states to all forms: spinner during API calls, disable submit buttons to prevent double submission
- [ ] T067 [P] Implement responsive design: test on mobile (320px width), tablet (768px), desktop (1024px+), adjust Tailwind classes

### Security

- [ ] T068 [P] Audit all API endpoints for user isolation: verify every task query includes WHERE user_id = current_user
- [ ] T069 [P] Add rate limiting consideration notes in backend/src/api/main.py (deferred to future phase but documented)
- [ ] T070 Test JWT expiration handling: wait 24 hours or manually expire token, verify frontend redirects to sign-in with message "Session expired"

### Documentation

- [x] T071 [P] Create backend/README.md: setup instructions (uv sync, .env configuration, alembic upgrade), running development server (uvicorn), running tests (pytest)
- [x] T072 [P] Create frontend/README.md: setup instructions (npm install, .env.local configuration), running development server (npm run dev), building for production (npm run build)
- [x] T073 Update root README.md: project overview, architecture diagram (backend ↔ frontend ↔ database), quick start links to backend and frontend READMEs

### Testing

- [ ] T074 Manual end-to-end test: complete user journey (sign up → sign in → create 3 tasks → mark 1 complete → update 1 → delete 1 → view remaining → log out)
- [ ] T075 Security test: attempt to access other user's tasks via API manipulation (direct curl with different user_id), verify 403 Forbidden returned

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-10)**: All depend on Foundational phase completion
  - P1 stories (US1-US5) should be completed first in sequence
  - P2 stories (US6-US8) can follow after P1 complete
  - Within P1 or P2, some stories can proceed in parallel (different developers)
- **Polish (Phase 11)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Registration)**: No dependencies on other stories - can start after Foundational
- **US2 (Sign-In)**: Depends on US1 (needs user accounts to exist)
- **US3 (Create Task)**: Depends on US2 (needs authentication) - tasks table depends on Foundational
- **US4 (View Tasks)**: Depends on US3 (needs tasks to view)
- **US5 (Toggle Completion)**: Depends on US3, US4 (needs tasks to toggle and view changes)
- **US6 (Update Task)**: Depends on US3, US4, US5 (independent after MVP but builds on core CRUD)
- **US7 (Delete Task)**: Depends on US3, US4 (independent after MVP)
- **US8 (Logout)**: Depends on US2 (needs sign-in to sign out from)

### Within Each User Story

- Backend service layer before API endpoints
- API endpoints before frontend UI
- Frontend UI before end-to-end testing
- Database migrations early (Foundational or start of story)

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T003 (backend pyproject.toml), T004 (frontend package.json), T005 (backend .env), T006 (frontend .env), T007 (Tailwind config) can run in parallel

**Foundational Phase (Phase 2)**:
- T009 (DB session), T011 (Task model) must be sequential
- T012 (FastAPI app), T013 (deps), T014 (routes init), T015 (health endpoint) can run after T009
- T016 (api.ts), T017 (auth.ts), T018 (types) can run in parallel (frontend foundation)

**User Story Phases**:
- Backend and frontend tasks within a story can be parallelized (different developers)
- Example US3: T030, T031, T032 (backend) can run parallel to T033, T034, T035 (frontend)

---

## Parallel Example: User Story 3 (Create Task)

```bash
# Backend Developer:
Task: "Create backend/src/services/task_service.py with create_task function"
Task: "Create POST /api/tasks endpoint with validation"

# Frontend Developer (simultaneously):
Task: "Create frontend/src/components/TaskForm.tsx with form inputs"
Task: "Implement form submission calling POST /api/tasks"

# Database (prerequisite):
Task: "Create Alembic migration for tasks table" (must complete before both above)
```

---

## Implementation Strategy

### MVP First (User Stories 1-5 Only - P1)

For fastest MVP delivery:

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T018) - **CRITICAL BLOCKER**
3. Complete Phase 3: US1 - Registration (T019-T023)
4. Complete Phase 4: US2 - Sign-In (T024-T029)
5. Complete Phase 5: US3 - Create Task (T030-T036)
6. Complete Phase 6: US4 - View Tasks (T037-T042)
7. Complete Phase 7: US5 - Toggle Completion (T043-T047)
8. **STOP and DEMO**: Complete authentication + task management loop
9. User testing: sufficient value? Continue to P2 stories or iterate

### Incremental Delivery (Recommended)

1. Phases 1-2: Setup & Foundation (T001-T018) → infrastructure ready
2. Phase 3: US1 - Registration (T019-T023) → **Demo: User sign-up**
3. Phase 4: US2 - Sign-In (T024-T029) → **Demo: Authentication loop**
4. Phase 5: US3 - Create Task (T030-T036) → **Demo: Add tasks**
5. Phase 6: US4 - View Tasks (T037-T042) → **Demo: Task list**
6. Phase 7: US5 - Toggle Completion (T043-T047) → **Demo: Track progress** 🎯 MVP READY
7. Phase 8: US6 - Update Task (T048-T052) → **Demo: Edit tasks**
8. Phase 9: US7 - Delete Task (T053-T057) → **Demo: Remove tasks**
9. Phase 10: US8 - Logout (T058-T062) → **Demo: Secure sign-out**
10. Phase 11: Polish (T063-T075) → Production ready

### Parallel Team Strategy

With multiple developers (recommend 3-4 for this size):

1. All complete Phases 1-2 together (shared foundation critical)
2. After Foundational complete:
   - Developer A (Backend): US1, US2 backend (T022, T027-T029)
   - Developer B (Frontend): US1, US2 frontend (T019-T021, T024-T026)
   - Developer C: Database migrations (T036) + documentation prep
3. P1 User Stories (US3-US5):
   - Developer A: Backend APIs (T030-T032, T037-T038, T043-T044)
   - Developer B: Frontend UI (T033-T035, T039-T042, T045-T047)
   - Developer C: Testing + integration validation
4. P2 User Stories (US6-US8):
   - Developer A: US6, US7 backend
   - Developer B: US6, US7 frontend
   - Developer C: US8 + Polish tasks
5. All: Phase 11 Polish together (testing, documentation, security audit)

---

## Summary

**Total Tasks**: 75 tasks across 11 phases

**Task Breakdown by Phase**:
- **Phase 1 - Setup**: 8 tasks (project structure, dependencies, config)
- **Phase 2 - Foundational**: 10 tasks (database, API, auth framework) ⚠️ BLOCKS all stories
- **Phase 3 - US1 (Registration, P1)**: 5 tasks (sign-up flow)
- **Phase 4 - US2 (Sign-In, P1)**: 6 tasks (authentication loop)
- **Phase 5 - US3 (Create Task, P1)**: 7 tasks (add tasks with user isolation)
- **Phase 6 - US4 (View Tasks, P1)**: 6 tasks (display task list)
- **Phase 7 - US5 (Toggle Completion, P1)**: 5 tasks (mark complete/incomplete)
- **Phase 8 - US6 (Update Task, P2)**: 5 tasks (edit task details)
- **Phase 9 - US7 (Delete Task, P2)**: 5 tasks (remove tasks)
- **Phase 10 - US8 (Logout, P2)**: 5 tasks (secure sign-out)
- **Phase 11 - Polish**: 13 tasks (error handling, UI/UX, docs, security)

**MVP Scope** (Recommended): Phases 1-7 (47 tasks)
- Setup + Foundational + User Stories 1-5 (P1 only)
- Delivers complete authentication + task CRUD + completion tracking
- Minimal viable feature set for user testing

**Parallel Opportunities**:
- **18 tasks** marked [P] can run in parallel within their phases
- Backend and frontend tasks within each user story can be parallelized (different developers)
- After Foundational phase, multiple user stories can proceed in parallel if staffed

**Independent Test Criteria**:
- Each user story has clear "Independent Test" description
- Manual end-to-end test paths defined
- Checkpoints after each phase confirming deliverable value

**Critical Path**:
1. Setup (8 tasks) → 2. Foundational (10 tasks) → 3-7. P1 User Stories (29 tasks) = **47 tasks to MVP**

---

## Notes

- [P] tasks = different files or components, no dependencies on incomplete tasks
- [Story] label = maps task to specific user story (US1-US8)
- Each phase has checkpoint: can stop and demo at each checkpoint
- All file paths follow plan.md structure: backend/src/, frontend/src/
- Backend uses Python 3.13+ with FastAPI + SQLModel + Neon PostgreSQL
- Frontend uses TypeScript with Next.js 16+ App Router + Better Auth + Tailwind
- **Golden Rule**: Every task query MUST include `WHERE user_id = current_user`
- JWT tokens have 24-hour expiration, stored in httpOnly cookies
- Database migrations use Alembic
- No automated tests initially - manual testing via browser and API clients
- Constitution update required before implementation (Phase 2 architecture changes)
