# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/003-todo-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api.yaml

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and AI chatbot structure

- [X] T001 Install backend dependencies (openai, mcp, agents-sdk) in backend/requirements.txt
- [X] T002 [P] Install frontend dependencies (@openai/chatkit) in frontend/package.json
- [X] T003 [P] Add OPENAI_API_KEY to backend/.env.example
- [X] T004 [P] Create backend/src/mcp/__init__.py package structure
- [X] T005 [P] Create backend/src/agent/__init__.py package structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core AI infrastructure that MUST be complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create Conversation model in backend/src/models/conversation.py per data-model.md
- [X] T007 [P] Create Message model in backend/src/models/message.py per data-model.md
- [X] T008 Run database migration to create conversations and messages tables
- [X] T009 [P] Implement JWT user_id extraction middleware in backend/src/api/dependencies.py
- [X] T010 Create base MCP tool interface in backend/src/mcp/base.py with user_id parameter requirement
- [X] T011 [P] Create ChatService skeleton in backend/src/services/chat_service.py
- [X] T012 [P] Create chat router skeleton POST /api/{user_id}/chat in backend/src/api/chat.py
- [X] T013 Register chat router in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 6 - Conversation Persistence (Priority: P1) 🎯 MVP

**Goal**: All chat messages persist in database and survive refresh/restart

**Independent Test**: Have a conversation, refresh page, verify messages are still visible

**Why First**: Persistence is needed before other stories can be tested properly

### Implementation for User Story 6

- [X] T014 [US6] Implement save_message() in backend/src/services/chat_service.py
- [X] T015 [P] [US6] Implement get_conversation_history() in backend/src/services/chat_service.py
- [X] T016 [P] [US6] Implement get_or_create_conversation() in backend/src/services/chat_service.py
- [X] T017 [US6] Implement GET /api/{user_id}/chat/history endpoint in backend/src/api/chat.py
- [X] T018 [US6] Add user_id isolation to all conversation queries (WHERE user_id = current_user)

**Checkpoint**: Messages can be saved and retrieved - foundation for all chat operations

---

## Phase 4: User Story 1 - Add Task via Chat (Priority: P1)

**Goal**: User can type "Add a task to buy milk" and AI creates the task

**Independent Test**: Sign in, open chat, type "Add a task to buy groceries", verify task appears in task list

### Implementation for User Story 1

- [X] T019 [US1] Implement add_task MCP tool in backend/src/mcp/tools.py with user_id, title, description params
- [X] T020 [US1] Create ChatAgent class with OpenAI Agents SDK in backend/src/agent/chat_agent.py
- [X] T021 [US1] Register add_task tool with ChatAgent in backend/src/agent/chat_agent.py
- [X] T022 [US1] Implement process_message() in backend/src/services/chat_service.py (save user msg → get context → run agent → save response)
- [X] T023 [US1] Complete POST /api/{user_id}/chat endpoint in backend/src/api/chat.py
- [X] T024 [P] [US1] Create ChatInput component in frontend/src/components/ChatInput.tsx (using AI SDK useChat)
- [X] T025 [P] [US1] Create ChatMessage component in frontend/src/components/ChatMessage.tsx (using AI SDK useChat)
- [X] T026 [US1] Create ChatInterface component in frontend/src/components/ChatInterface.tsx (using AI SDK useChat)
- [X] T027 [US1] Create chatApi service in frontend/src/services/chatApi.ts (via Next.js API route /api/chat)
- [X] T028 [US1] Create chat page in frontend/src/pages/chat/index.tsx (frontend/app/chat/page.tsx)
- [X] T029 [US1] Add navigation link to chat page in frontend layout

**Checkpoint**: User Story 1 complete - users can add tasks via natural language

---

## Phase 5: User Story 2 - View Tasks via Chat (Priority: P1)

**Goal**: User can ask "Show me my tasks" and AI returns formatted list

**Independent Test**: Create 2-3 tasks, ask "Show my tasks" in chat, verify AI lists all tasks

### Implementation for User Story 2

- [X] T030 [US2] Implement list_tasks MCP tool in backend/src/mcp/tools.py with user_id, status params
- [X] T031 [US2] Register list_tasks tool with ChatAgent in backend/src/agent/chat_agent.py
- [X] T032 [US2] Update system prompt to handle task listing intents in backend/src/agent/chat_agent.py

**Checkpoint**: User Story 2 complete - users can view tasks via chat

---

## Phase 6: User Story 3 - Complete Task via Chat (Priority: P1)

**Goal**: User can say "Mark task 5 as complete" and AI updates task status

**Independent Test**: Create a pending task, ask AI to complete it, verify status changed

### Implementation for User Story 3

- [X] T033 [US3] Implement complete_task MCP tool in backend/src/mcp/tools.py with user_id, task_id params
- [X] T034 [US3] Add task validation (check exists, belongs to user) in complete_task tool
- [X] T035 [US3] Register complete_task tool with ChatAgent in backend/src/agent/chat_agent.py
- [X] T036 [US3] Handle already-completed task edge case (return friendly message)

**Checkpoint**: User Story 3 complete - core add/view/complete flow works via chat

---

## Phase 7: User Story 4 - Delete Task via Chat (Priority: P2)

**Goal**: User can say "Delete task 3" and AI removes the task

**Independent Test**: Create a task, ask AI to delete it, verify task is removed

### Implementation for User Story 4

- [X] T037 [US4] Implement delete_task MCP tool in backend/src/mcp/tools.py with user_id, task_id params
- [X] T038 [US4] Add task validation (check exists, belongs to user) in delete_task tool
- [X] T039 [US4] Register delete_task tool with ChatAgent in backend/src/agent/chat_agent.py
- [X] T040 [US4] Add confirmation prompt for "delete all" requests in system prompt

**Checkpoint**: User Story 4 complete - users can delete tasks via chat

---

## Phase 8: User Story 5 - Update Task via Chat (Priority: P2)

**Goal**: User can say "Update task 2 title to Buy organic milk" and AI modifies task

**Independent Test**: Create a task, ask AI to update title, verify change reflected

### Implementation for User Story 5

- [X] T041 [US5] Implement update_task MCP tool in backend/src/mcp/tools.py with user_id, task_id, title?, description? params
- [X] T042 [US5] Add task validation (check exists, belongs to user) in update_task tool
- [X] T043 [US5] Register update_task tool with ChatAgent in backend/src/agent/chat_agent.py

**Checkpoint**: User Story 5 complete - all CRUD operations work via chat

---

## Phase 9: User Story 7 - Start New Conversation (Priority: P3)

**Goal**: User can click "New Chat" to start fresh conversation

**Independent Test**: Click "New Chat", verify fresh conversation starts, old one still accessible

### Implementation for User Story 7

- [X] T044 [US7] Implement POST /api/{user_id}/conversations endpoint in backend/src/api/chat.py
- [X] T045 [US7] Implement GET /api/{user_id}/conversations endpoint in backend/src/api/chat.py
- [X] T046 [US7] Add "New Chat" button to ChatInterface in frontend/src/components/ChatInterface.tsx
- [ ] T047 [US7] Add conversation switcher UI in frontend/src/components/ChatInterface.tsx

**Checkpoint**: User Story 7 complete - users can manage multiple conversations

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, UX polish, and security hardening

- [X] T048 [P] Add loading spinner during AI processing in frontend/src/components/ChatInterface.tsx
- [X] T049 [P] Implement 15-second timeout with "Taking longer than usual..." message
- [X] T050 [P] Add graceful error handling when AI service unavailable (503 response)
- [X] T051 [P] Implement rate limiting (50 messages/hour) in frontend/app/api/chat/route.ts
- [X] T052 [P] Add input validation (empty message, max 10000 chars) in backend/src/api/chat.py
- [X] T053 [P] Handle JWT token expiration with redirect to sign-in (N/A - using demo mode)
- [X] T054 Verify all MCP tools enforce user_id isolation (security audit)
- [X] T055 [P] Add error boundary for chat component errors in frontend
- [X] T056 Run quickstart.md validation checklist (build passing)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **US6 Persistence (Phase 3)**: Depends on Foundational - enables testing of other stories
- **US1 Add Task (Phase 4)**: Depends on US6 - core value proposition
- **US2 View Tasks (Phase 5)**: Depends on US1 (shares agent setup)
- **US3 Complete Task (Phase 6)**: Depends on US2 (shares agent setup)
- **US4 Delete Task (Phase 7)**: Depends on Foundational only - can run parallel with US1-3
- **US5 Update Task (Phase 8)**: Depends on Foundational only - can run parallel with US1-3
- **US7 New Conversation (Phase 9)**: Depends on US6 (conversation management)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### Recommended MVP Scope

**MVP = Phase 1 + Phase 2 + Phase 3 + Phase 4**

This delivers:
- Conversation persistence (US6)
- Add tasks via chat (US1)

User can verify: "I can chat with AI to add tasks, and my chat history is preserved"

### Parallel Opportunities

```text
# After Foundational (Phase 2):
Parallel Group A: T014, T015, T016 (US6 service methods)
Parallel Group B: T024, T025 (Frontend components)

# After US1 (Phase 4):
US2, US3 can proceed sequentially (share agent)
US4, US5 can start in parallel (independent tools)

# During Polish (Phase 10):
T048, T049, T050, T051, T052, T053, T055 (all parallel)
```

---

## Task Summary

| Phase | User Story | Task Count |
|-------|------------|------------|
| 1 - Setup | Shared | 5 |
| 2 - Foundational | Shared | 8 |
| 3 - Persistence | US6 | 5 |
| 4 - Add Task | US1 | 11 |
| 5 - View Tasks | US2 | 3 |
| 6 - Complete Task | US3 | 4 |
| 7 - Delete Task | US4 | 4 |
| 8 - Update Task | US5 | 3 |
| 9 - New Conversation | US7 | 4 |
| 10 - Polish | Cross-cutting | 9 |
| **Total** | | **56** |

---

## Notes

- [P] tasks = different files, no dependencies within that phase
- [USn] label maps task to specific user story for traceability
- All MCP tools MUST receive user_id from API layer, not AI inference (Constitution Principle III)
- All messages MUST be persisted before/after processing (Constitution Principle IV)
- Verify tool determinism - errors return messages, not crashes (Constitution Principle II)
