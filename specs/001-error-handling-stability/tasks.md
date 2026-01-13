# Tasks: Error Handling and Stability Improvements

**Input**: Design documents from `/specs/001-error-handling-stability/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated tests requested - manual validation via quickstart.md scenarios

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `frontend/components/`, `frontend/lib/`, `frontend/types/`
- All file paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

**Status**: ✅ No setup needed - using existing project structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T001 [P] Add ErrorState<T> interface to frontend/types/index.ts
- [X] T002 [P] Add ComponentErrorProps interface to frontend/types/index.ts
- [X] T003 [P] Add API_URL default fallback and validation to frontend/lib/api.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Frontend Loads Without Errors (Priority: P1) 🎯 MVP

**Goal**: Fix infinite render loops in TagInput, TaskFilters, and TaskForm components by correcting useEffect dependency arrays

**Independent Test**: Open http://localhost:3000, check React DevTools Profiler shows components render exactly once, verify no console errors

### Implementation for User Story 1

- [X] T004 [P] [US1] Fix TagInput.tsx useEffect dependency array to empty [] for mount-only tag fetching in frontend/components/TagInput.tsx
- [X] T005 [P] [US1] Fix TaskFilters.tsx useEffect dependency array to empty [] for mount-only data fetching in frontend/components/TaskFilters.tsx
- [X] T006 [P] [US1] Fix TaskForm.tsx useEffect dependency array to empty [] for mount-only category fetching in frontend/components/TaskForm.tsx
- [X] T007 [US1] Verify no infinite loops using React DevTools Profiler (manual test from quickstart.md Scenario 1)
- [X] T008 [US1] Verify 0 ESLint exhaustive-deps warnings by running npm run lint in frontend directory

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - frontend loads without errors

---

## Phase 4: User Story 2 - Graceful API Error Handling (Priority: P1)

**Goal**: Add loading states, error states, and retry buttons to frontend components for user-friendly error handling

**Independent Test**: Stop backend server, load frontend, verify user-friendly error messages appear with retry buttons (not crashes or blank screens)

### Implementation for User Story 2

- [X] T009 [US2] Add loading state (isLoading: boolean) to TagInput.tsx component state in frontend/components/TagInput.tsx
- [X] T010 [US2] Add error state (error: string | null) to TagInput.tsx component state in frontend/components/TagInput.tsx
- [X] T011 [US2] Add try-catch block to TagInput.tsx fetch() call with user-friendly error mapping in frontend/components/TagInput.tsx
- [X] T012 [US2] Add empty array fallback when TagInput.tsx fetch fails to prevent null errors in frontend/components/TagInput.tsx
- [X] T013 [US2] Add retry button to TagInput.tsx error state UI in frontend/components/TagInput.tsx
- [X] T014 [US2] Add loading state (isLoading: boolean) to TaskFilters.tsx component state in frontend/components/TaskFilters.tsx
- [X] T015 [US2] Add error state (error: string | null) to TaskFilters.tsx component state in frontend/components/TaskFilters.tsx
- [X] T016 [US2] Add try-catch blocks to TaskFilters.tsx fetch() calls with user-friendly error mapping in frontend/components/TaskFilters.tsx
- [X] T017 [US2] Add empty array fallbacks when TaskFilters.tsx fetches fail to prevent null errors in frontend/components/TaskFilters.tsx
- [X] T018 [US2] Add retry button to TaskFilters.tsx error state UI in frontend/components/TaskFilters.tsx
- [X] T019 [US2] Add loading state (isLoading: boolean) to TaskForm.tsx component state in frontend/components/TaskForm.tsx
- [X] T020 [US2] Add error state (error: string | null) to TaskForm.tsx component state in frontend/components/TaskForm.tsx
- [X] T021 [US2] Add try-catch block to TaskForm.tsx fetch() call with user-friendly error mapping in frontend/components/TaskForm.tsx
- [X] T022 [US2] Add empty array fallback when TaskForm.tsx fetch fails to prevent null errors in frontend/components/TaskForm.tsx
- [X] T023 [US2] Add retry button to TaskForm.tsx error state UI in frontend/components/TaskForm.tsx
- [X] T024 [US2] Verify retry buttons work by stopping backend and clicking retry (manual test from quickstart.md Scenario 3)
- [X] T025 [US2] Verify user-friendly error messages appear when backend is down (manual test from quickstart.md Scenario 2)
- [X] T026 [US2] Verify no technical details (stack traces, HTTP codes) are exposed to users (manual test from quickstart.md Scenario 7)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - frontend loads and handles errors gracefully

---

## Phase 5: User Story 3 - Reliable Backend Startup (Priority: P2)

**Goal**: Add database connection retry logic with exponential backoff and environment variable validation

**Independent Test**: Start backend with invalid DATABASE_URL, observe retry logs showing 3 attempts with 1s, 2s, 4s delays, verify clear error messages

### Implementation for User Story 3

- [X] T027 [US3] Add environment variable validation for DATABASE_URL to backend/src/api/main.py
- [X] T028 [US3] Add environment variable validation for JWT_SECRET to backend/src/api/main.py
- [X] T029 [US3] Add environment variable validation for CORS_ORIGINS to backend/src/api/main.py
- [X] T030 [US3] Add connect_with_retry() function with max 3 retries to backend/src/db/session.py
- [X] T031 [US3] Add exponential backoff logic (delay = 2^(attempt-1)) to backend/src/db/session.py
- [X] T032 [US3] Add 10-second connection timeout per attempt to backend/src/db/session.py
- [X] T033 [US3] Add retry attempt logging with attempt number and delay to backend/src/db/session.py
- [X] T034 [US3] Add clear error message on final retry failure to backend/src/db/session.py
- [X] T035 [US3] Verify database retry logic with simulated connection failure (manual test from quickstart.md Scenario 4)
- [X] T036 [US3] Verify environment variable validation shows clear errors (manual test from quickstart.md Scenario 5)
- [X] T037 [US3] Verify backend starts within 15 seconds even with 2 retries (manual test from quickstart.md performance benchmark)

**Checkpoint**: All user stories should now be independently functional - complete error handling and stability system

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T038 [P] Verify all fetch() calls are wrapped in try-catch blocks (code review for FR-008 compliance)
- [X] T039 [P] Verify all error messages are user-friendly with no stack traces (code review for FR-009 compliance)
- [X] T040 [P] Verify all retry buttons are disabled during requests (code review for FR-022 compliance)
- [ ] T041 Run complete quickstart.md validation suite (all 7 test scenarios)
- [ ] T042 Verify all 10 success criteria pass (SC-001 through SC-010 from spec.md)
- [ ] T043 [P] Update AUTHENTICATION_FIX.md if error handling revealed additional auth issues
- [X] T044 [P] Add inline code comments explaining exponential backoff formula in backend/src/db/session.py
- [X] T045 [P] Add inline code comments explaining empty dependency array rationale in fixed components

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ✅ Complete (no setup needed)
- **Foundational (Phase 2)**: No dependencies - BLOCKS all user stories until complete
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1) can proceed in parallel with User Story 2 (P1) after Foundational
  - User Story 3 (P2) can proceed in parallel with US1/US2 (different codebase: backend vs frontend)
- **Polish (Phase 6)**: Depends on all user stories (US1, US2, US3) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but logically builds on US1 fixes)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent backend work)

### Within Each User Story

**User Story 1** (T004-T008):
- T004, T005, T006 can run in parallel (different files)
- T007, T008 run after T004-T006 complete (validation tasks)

**User Story 2** (T009-T026):
- T009-T013 (TagInput changes) are sequential (same file)
- T014-T018 (TaskFilters changes) are sequential (same file)
- T019-T023 (TaskForm changes) are sequential (same file)
- BUT: TagInput tasks (T009-T013) can run in parallel with TaskFilters tasks (T014-T018) and TaskForm tasks (T019-T023)
- T024-T026 run after all implementation tasks complete (validation tasks)

**User Story 3** (T027-T037):
- T027-T029 are sequential (same file: main.py)
- T030-T034 are sequential (same file: session.py)
- BUT: main.py tasks (T027-T029) can run in parallel with session.py tasks (T030-T034)
- T035-T037 run after all implementation tasks complete (validation tasks)

### Parallel Opportunities

**Foundational Phase (Phase 2)**:
- T001, T002, T003 can ALL run in parallel (different files)

**User Story 1 (Phase 3)**:
- T004, T005, T006 can ALL run in parallel (different files)

**User Story 2 (Phase 4)**:
- TagInput group (T009-T013), TaskFilters group (T014-T018), TaskForm group (T019-T023) can run in parallel with each other (different files)

**User Story 3 (Phase 5)**:
- main.py group (T027-T029) can run in parallel with session.py group (T030-T034) (different files)

**Polish Phase (Phase 6)**:
- T038, T039, T040, T043, T044, T045 can ALL run in parallel (code review and documentation tasks)

**Cross-Phase Parallelism**:
- After Foundational (Phase 2) completes:
  - User Story 1 (Phase 3) can run in parallel with User Story 2 (Phase 4) and User Story 3 (Phase 5)
  - Frontend work (US1, US2) is completely independent from backend work (US3)

---

## Parallel Example: Foundational Phase

```bash
# Launch all foundational tasks together:
Task: "Add ErrorState<T> interface to frontend/types/index.ts"
Task: "Add ComponentErrorProps interface to frontend/types/index.ts"
Task: "Add API_URL default fallback and validation to frontend/lib/api.ts"
```

---

## Parallel Example: User Story 1

```bash
# Launch all component fixes together:
Task: "Fix TagInput.tsx useEffect dependency array to empty [] for mount-only tag fetching"
Task: "Fix TaskFilters.tsx useEffect dependency array to empty [] for mount-only data fetching"
Task: "Fix TaskForm.tsx useEffect dependency array to empty [] for mount-only category fetching"
```

---

## Parallel Example: User Story 2

```bash
# Launch component error handling in parallel (different files):
# Group 1: TagInput
Task: "Add loading/error state to TagInput.tsx"
Task: "Add try-catch to TagInput.tsx fetch()"
Task: "Add retry button to TagInput.tsx"

# Group 2: TaskFilters (runs in parallel with Group 1)
Task: "Add loading/error state to TaskFilters.tsx"
Task: "Add try-catch to TaskFilters.tsx fetch()"
Task: "Add retry button to TaskFilters.tsx"

# Group 3: TaskForm (runs in parallel with Groups 1 and 2)
Task: "Add loading/error state to TaskForm.tsx"
Task: "Add try-catch to TaskForm.tsx fetch()"
Task: "Add retry button to TaskForm.tsx"
```

---

## Parallel Example: User Story 3

```bash
# Launch backend fixes in parallel (different files):
# Group 1: Environment validation (main.py)
Task: "Add environment variable validation for DATABASE_URL to backend/src/api/main.py"
Task: "Add environment variable validation for JWT_SECRET to backend/src/api/main.py"
Task: "Add environment variable validation for CORS_ORIGINS to backend/src/api/main.py"

# Group 2: Database retry (session.py) - runs in parallel with Group 1
Task: "Add connect_with_retry() function with max 3 retries to backend/src/db/session.py"
Task: "Add exponential backoff logic to backend/src/db/session.py"
Task: "Add 10-second connection timeout per attempt to backend/src/db/session.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (T001-T003)
2. Complete Phase 3: User Story 1 (T004-T008)
3. **STOP and VALIDATE**: Test that frontend loads without infinite loops (quickstart.md Scenario 1)
4. If passing, you have a working MVP: application loads successfully

### Incremental Delivery

1. Complete Foundational (Phase 2) → Types and API defaults ready
2. Add User Story 1 (Phase 3) → Test independently → Frontend loads without errors (MVP!)
3. Add User Story 2 (Phase 4) → Test independently → Error handling with retry buttons works
4. Add User Story 3 (Phase 5) → Test independently → Backend startup is reliable with retries
5. Complete Polish (Phase 6) → Validate all criteria pass

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Foundational (Phase 2) together (3 quick tasks: T001-T003)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Frontend infinite loop fixes: T004-T008)
   - **Developer B**: User Story 2 (Frontend error handling: T009-T026)
   - **Developer C**: User Story 3 (Backend reliability: T027-T037)
3. Stories complete and integrate independently
4. Team converges on Polish (Phase 6) for final validation

### Single Developer Strategy

1. Complete Foundational (Phase 2): T001-T003 (can run in parallel with 3 tool calls)
2. Complete User Story 1 (Phase 3): T004-T008
   - Run T004-T006 in parallel (3 tool calls)
   - Run T007-T008 sequentially (validation)
3. Complete User Story 2 (Phase 4): T009-T026
   - Run 3 groups in parallel: TagInput (T009-T013), TaskFilters (T014-T018), TaskForm (T019-T023)
   - Run T024-T026 sequentially (validation)
4. Complete User Story 3 (Phase 5): T027-T037
   - Run 2 groups in parallel: main.py (T027-T029), session.py (T030-T034)
   - Run T035-T037 sequentially (validation)
5. Complete Polish (Phase 6): T038-T045
   - Run T038-T040, T043-T045 in parallel (6 tool calls)
   - Run T041-T042 sequentially (final validation)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No automated tests requested - use manual validation from quickstart.md
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend work (US1, US2) is completely independent from backend work (US3)
- All components get fixed with same pattern: empty dependency array [] + error handling
- All validation tasks reference specific scenarios from quickstart.md
