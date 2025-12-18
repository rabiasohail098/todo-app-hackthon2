# Feature Specification: Todo AI Chatbot

**Feature Branch**: `003-todo-ai-chatbot`
**Created**: 2025-12-16
**Status**: Draft
**Input**: User description: "Transform Phase 2 Web App into AI-powered Chatbot using Model Context Protocol (MCP) for natural language task management"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chat with AI to Add Task (Priority: P1)

An authenticated user wants to add a new task by typing a natural language message like "Add a task to buy milk" instead of filling out a form. The AI understands the intent and creates the task automatically.

**Why this priority**: This is the core value proposition of the AI chatbot. If users cannot create tasks through chat, the feature has no value. This demonstrates the fundamental AI-to-database flow.

**Independent Test**: Can be fully tested by signing in, opening the chat interface, typing "Add a task to buy groceries", and verifying: (1) AI acknowledges the request, (2) task appears in the task list, (3) message history is preserved.

**Acceptance Scenarios**:

1. **Given** an authenticated user in the chat interface, **When** they type "Add a task to buy milk", **Then** AI creates the task and responds with confirmation including task details
2. **Given** an authenticated user in the chat interface, **When** they type "Create a task called Review PR with description Check feature branch", **Then** AI creates task with both title and description
3. **Given** an authenticated user in the chat interface, **When** they type an ambiguous message like "milk", **Then** AI asks for clarification before creating a task
4. **Given** an authenticated user, **When** they add a task via chat, **Then** the task is immediately visible in their task list (same as Phase 2 dashboard)

---

### User Story 2 - Chat with AI to View Tasks (Priority: P1)

An authenticated user wants to ask the AI about their tasks using natural language like "Show me my tasks" or "What's on my todo list?" and receive a formatted response.

**Why this priority**: Viewing tasks is essential for task management. Users need to see their tasks through the chat interface without switching to the traditional dashboard.

**Independent Test**: Can be fully tested by creating 2-3 tasks via any method, then asking "Show my tasks" in chat and verifying the AI lists all tasks with correct details.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 3 tasks (2 pending, 1 complete), **When** they ask "Show me my tasks", **Then** AI responds with a list of all 3 tasks showing title, status, and description
2. **Given** an authenticated user, **When** they ask "Show my pending tasks", **Then** AI responds with only pending tasks filtered by status
3. **Given** an authenticated user, **When** they ask "Show my completed tasks", **Then** AI responds with only completed tasks
4. **Given** an authenticated user with no tasks, **When** they ask "What's on my list?", **Then** AI responds with a friendly message indicating no tasks found

---

### User Story 3 - Chat with AI to Complete Task (Priority: P1)

An authenticated user wants to mark a task as complete by telling the AI "Mark task 1 as done" or "Complete the grocery task".

**Why this priority**: Completing tasks is the primary workflow outcome. Users need to mark progress through natural language.

**Independent Test**: Can be fully tested by creating a pending task, asking AI to mark it complete, and verifying the task status changes to completed.

**Acceptance Scenarios**:

1. **Given** an authenticated user with pending task ID 5, **When** they say "Mark task 5 as complete", **Then** AI marks the task done and confirms the update
2. **Given** an authenticated user with task titled "Buy groceries", **When** they say "Complete the groceries task", **Then** AI identifies the correct task and marks it complete
3. **Given** an authenticated user, **When** they try to complete a task that doesn't exist, **Then** AI responds with a clear error message "Task not found"
4. **Given** an authenticated user, **When** they try to complete an already completed task, **Then** AI informs them the task is already done

---

### User Story 4 - Chat with AI to Delete Task (Priority: P2)

An authenticated user wants to remove a task by telling the AI "Delete task 3" or "Remove the milk task".

**Why this priority**: Deletion is useful for list maintenance but secondary to add/view/complete flow. Users can manage without it initially.

**Independent Test**: Can be fully tested by creating a task, asking AI to delete it, and verifying the task is removed from the list.

**Acceptance Scenarios**:

1. **Given** an authenticated user with task ID 3, **When** they say "Delete task 3", **Then** AI deletes the task and confirms removal
2. **Given** an authenticated user, **When** they try to delete a non-existent task, **Then** AI responds with "Task not found" error
3. **Given** an authenticated user, **When** they say "Remove all my tasks", **Then** AI asks for confirmation before proceeding (safety check)

---

### User Story 5 - Chat with AI to Update Task (Priority: P2)

An authenticated user wants to modify an existing task's title or description through chat like "Update task 2 title to Buy organic milk".

**Why this priority**: Updating is a convenience feature. Users can delete and recreate as a workaround.

**Independent Test**: Can be fully tested by creating a task, asking AI to update its title, and verifying the change is reflected.

**Acceptance Scenarios**:

1. **Given** an authenticated user with task ID 2 titled "Buy milk", **When** they say "Change task 2 title to Buy organic milk", **Then** AI updates the title and confirms
2. **Given** an authenticated user, **When** they say "Add description 'Check expiry date' to task 2", **Then** AI updates the description field
3. **Given** an authenticated user, **When** they try to update a non-existent task, **Then** AI responds with "Task not found" error

---

### User Story 6 - Conversation History Persistence (Priority: P1)

An authenticated user wants their chat history to be preserved across sessions. When they return to the app, they can see previous conversations.

**Why this priority**: Persistence is critical for user trust and continuity. Users expect chat history to survive page refresh and logout.

**Independent Test**: Can be fully tested by having a conversation, refreshing the page, and verifying all messages are still visible.

**Acceptance Scenarios**:

1. **Given** an authenticated user with previous chat messages, **When** they refresh the page, **Then** chat history loads and displays all previous messages
2. **Given** an authenticated user, **When** they log out and log back in, **Then** their conversation history is preserved
3. **Given** an authenticated user, **When** the server restarts, **Then** no chat history is lost (persistence to database)
4. **Given** User A is signed in, **When** they view chat history, **Then** they see ONLY their own messages (not User B's)

---

### User Story 7 - Start New Conversation (Priority: P3)

An authenticated user wants to start a fresh conversation while optionally preserving old ones.

**Why this priority**: Nice-to-have for organization. Users can work with a single continuous conversation initially.

**Independent Test**: Can be fully tested by clicking "New Chat" and verifying a fresh conversation starts.

**Acceptance Scenarios**:

1. **Given** an authenticated user with existing conversation, **When** they click "New Conversation", **Then** a new empty chat session starts
2. **Given** an authenticated user, **When** they start a new conversation, **Then** the previous conversation is still accessible

---

### Edge Cases

- What happens when AI service is unavailable? System MUST show "AI service temporarily unavailable. Please try again." message
- What happens when user sends empty message? System MUST ignore or prompt for input
- What happens when user sends very long message (>10000 chars)? System MUST truncate or reject with clear feedback
- What happens when AI hallucinates a task ID that doesn't exist? MCP tool MUST return clear error, not crash
- What happens when JWT token expires during chat? System MUST redirect to sign-in with "Session expired" message
- What happens when database connection fails? System MUST show user-friendly error and retry option
- What happens when User A tries to access User B's tasks via chat? System MUST return only User A's tasks (user_id isolation enforced at MCP tool level)
- What happens when AI response takes too long? System MUST timeout after 15 seconds and show "Taking longer than usual..." message with retry option
- What happens when user exceeds rate limit? System MUST return 429 Too Many Requests with "You've sent too many messages. Please wait a few minutes." (50 messages/hour limit)

## Requirements *(mandatory)*

### Functional Requirements

#### Chat Interface

- **FR-001**: System MUST provide a chat interface where users can type natural language messages
- **FR-002**: System MUST display AI responses in a conversational format (chat bubbles)
- **FR-003**: System MUST show loading indicator while AI is processing
- **FR-004**: System MUST display chat history on page load (last 50 messages)
- **FR-005**: System MUST allow users to scroll through conversation history

#### AI Agent & MCP Tools

- **FR-006**: System MUST process natural language input and determine user intent
- **FR-007**: System MUST provide `add_task(user_id, title, description)` tool that creates a task and returns task details
- **FR-008**: System MUST provide `list_tasks(user_id, status)` tool that returns tasks filtered by status ("all", "pending", "completed")
- **FR-009**: System MUST provide `complete_task(user_id, task_id)` tool that marks task as completed
- **FR-010**: System MUST provide `delete_task(user_id, task_id)` tool that removes the task
- **FR-011**: System MUST provide `update_task(user_id, task_id, title, description)` tool that modifies task fields
- **FR-012**: All MCP tools MUST require user_id parameter (passed from API layer, not AI-generated)
- **FR-013**: All MCP tools MUST return clear error messages for invalid operations (not crash)

#### Chat API Endpoint

- **FR-014**: System MUST provide POST /api/{user_id}/chat endpoint for sending messages
- **FR-015**: System MUST validate JWT token and ensure `sub` claim matches `{user_id}` in URL
- **FR-016**: System MUST save user message to database before processing
- **FR-017**: System MUST fetch last 10 messages as context for AI
- **FR-018**: System MUST save AI response to database after generation
- **FR-019**: System MUST return AI response with any tool call information

#### Data Persistence

- **FR-020**: System MUST store all messages in Conversation and Message tables
- **FR-021**: System MUST link messages to correct user via user_id
- **FR-022**: System MUST preserve message order via timestamps
- **FR-023**: System MUST NOT lose messages on server restart
- **FR-029**: System MUST auto-delete conversations older than 90 days (data retention policy)

#### Security

- **FR-024**: System MUST reject requests without valid JWT token (401 Unauthorized)
- **FR-025**: System MUST reject requests where JWT user_id doesn't match URL user_id (403 Forbidden)
- **FR-026**: System MUST enforce user_id isolation in all MCP tool operations
- **FR-027**: System MUST NOT allow AI to access or modify other users' tasks
- **FR-028**: System MUST enforce rate limiting of 50 messages per hour per user, returning 429 when exceeded

### Key Entities

- **Conversation**: Represents a chat session with id (unique identifier), user_id (owner reference), created_at (timestamp)
- **Message**: Represents a single chat message with id, conversation_id (parent reference), role (user or assistant), content (message text), created_at (timestamp)
- **Task**: Existing entity from Phase 2 - id, user_id, title, description, is_completed, created_at

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a task via chat in under 5 seconds from message send to confirmation
- **SC-002**: Users can view their task list via chat in under 3 seconds
- **SC-003**: Chat history loads on page open in under 2 seconds (50 messages)
- **SC-004**: 100% of chat messages are persisted (zero message loss on refresh/restart)
- **SC-005**: 100% of MCP tool operations enforce user isolation (no cross-user data access)
- **SC-006**: AI correctly interprets user intent for task operations 90%+ of the time
- **SC-007**: All invalid task IDs return clear error messages (no crashes)
- **SC-008**: System shows loading state during AI processing (no frozen UI)
- **SC-009**: Users can complete add/view/complete task flow entirely through chat without using traditional UI

## Clarifications

### Session 2025-12-16

- Q: What happens when user message is ambiguous? → A: AI should ask for clarification
- Q: How many messages to keep as context? → A: Last 10 messages
- Q: Should old conversations be accessible? → A: Yes, via conversation selection (P3)
- Q: What status filter options for list_tasks? → A: "all", "pending", "completed"
- Q: What happens if AI takes too long to respond? → A: Timeout after 15 seconds, show "Taking longer than usual..." message
- Q: Should users have message rate limits? → A: Yes, 50 messages per hour per user
- Q: How long should conversation history be retained? → A: 90 days, auto-delete older conversations

## Assumptions

- Users have completed Phase 2 registration and have valid JWT tokens
- Phase 2 task database schema remains unchanged (tasks table with user_id isolation)
- AI service (OpenAI) is generally available with standard rate limits
- Users are comfortable with natural language chat interfaces
- Single conversation per user initially; multiple conversations are P3 enhancement
- Message context window of 10 messages is sufficient for most interactions
- Task IDs are integers that users can reference in chat

## Out of Scope (Phase 3)

- Voice input/output
- File attachments in chat
- Task sharing via chat
- Reminders or scheduled notifications
- Multi-language support (English only)
- Chat export functionality
- AI conversation analytics
- Custom AI personality/tone settings
- Integration with external calendars
- Bulk task operations via single command

## Dependencies

- **Phase 2**: User authentication (JWT), Task CRUD API, Neon PostgreSQL database
- **External**: OpenAI API access for AI agent capabilities
- **External**: MCP protocol compatibility for tool standardization

## Risks

1. **AI Intent Misinterpretation**: AI may misunderstand user requests
   - Mitigation: Implement confirmation for destructive actions, provide "Did you mean..." suggestions
2. **Rate Limiting**: OpenAI API rate limits may affect response times
   - Mitigation: Implement request queuing, show clear feedback during delays
3. **Cost Management**: High chat volume may increase API costs
   - Mitigation: Monitor usage, implement reasonable message limits if needed
