# Implementation Plan: AI-Powered Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Created**: 2025-12-30
**Status**: Planning
**Prerequisites**: Phase 2 (Web App with Authentication) must be complete

## Executive Summary

This plan describes the implementation of an AI-powered conversational interface for task management using a **stateless architecture**. The server holds no memory between requests—all state is persisted in Neon PostgreSQL. The AI agent uses MCP (Model Context Protocol) tools to interact with the database, ensuring deterministic and secure task operations.

**Key Architecture Decision**: Stateless design enables horizontal scaling, simplifies debugging, and ensures conversation continuity across server restarts.

## Architecture Overview

```
┌─────────────────────┐
│   Next.js Frontend  │
│   (OpenAI ChatKit)  │
└──────────┬──────────┘
           │ HTTP POST /api/chat
           │ {user_id, message}
           ▼
┌────────────────────────────────────────┐
│         FastAPI Backend                │
│  ┌──────────────────────────────────┐  │
│  │   POST /api/chat Handler         │  │
│  │   1. Validate JWT → extract user │  │
│  │   2. Save user message to DB     │  │
│  │   3. Fetch last 10 messages      │  │
│  │   4. Initialize AI Agent + Tools │  │
│  │   5. Run agent with context      │  │
│  │   6. Save assistant response     │  │
│  │   7. Return response to client   │  │
│  │   8. *** Forget everything ***   │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │   OpenAI Agents SDK              │  │
│  │   - GPT-4o Model                 │  │
│  │   - Interpret natural language   │  │
│  │   - Execute MCP tools            │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │   MCP Tools (Official SDK)       │  │
│  │   - add_task()                   │  │
│  │   - list_tasks()                 │  │
│  │   - complete_task()              │  │
│  │   - delete_task()                │  │
│  │   - update_task()                │  │
│  └──────────────────────────────────┘  │
└────────────────┬───────────────────────┘
                 │
                 ▼
      ┌─────────────────────┐
      │  Neon PostgreSQL    │
      │  - tasks            │
      │  - conversations    │
      │  - messages         │
      └─────────────────────┘
```

## Core Principles

### 1. Stateless by Design (The Golden Rule)

**Principle**: The FastAPI server MUST NOT hold any state between requests.

**Implementation**:
- Every request to `/api/chat` is independent and self-contained
- Agent is initialized fresh for each request (no persistent agent instances)
- Conversation context is fetched from database on every request
- After response is returned, server forgets everything

**Benefit**: Any server instance can handle any request (horizontal scaling), server restarts don't affect conversations, simpler debugging.

**Code Contract**:
```python
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, user_id: str = Depends(get_current_user)):
    # 1. Fetch history from DB
    # 2. Initialize agent (fresh instance)
    # 3. Run agent
    # 4. Save response to DB
    # 5. Return and forget
    pass
```

### 2. Security Propagation

**Principle**: `user_id` extracted from JWT at API layer MUST be passed explicitly through entire chain.

**Implementation**:
```
JWT Token → get_current_user() → user_id string
    → API Handler → Agent → MCP Tools → Database Queries
```

**Never Allowed**: AI generating/guessing user_id values

**Code Contract**:
```python
# MCP Tool signature - user_id is REQUIRED parameter
async def add_task(user_id: str, title: str, description: Optional[str] = None):
    # Database query MUST include: WHERE user_id = user_id
    pass
```

### 3. MCP Tool Determinism

**Principle**: MCP tools MUST behave predictably with clear error handling.

**Implementation**:
- All inputs validated before execution
- Invalid task IDs return `{"error": "Task not found"}`, NOT crash
- Structured responses: `{"success": bool, "data": {...}, "error": Optional[str]}`

**Code Contract**:
```python
async def complete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    task = await db.get_task(user_id, task_id)
    if not task:
        return {"success": False, "error": "Task not found"}
    task.completed = True
    await db.commit()
    return {"success": True, "data": task.dict()}
```

## Technology Stack Decisions

### Backend: FastAPI

**Why**:
- Native async/await support (required for DB operations)
- Fast performance for stateless request handling
- Built-in OpenAPI documentation
- Easy JWT middleware integration

**Alternatives Considered**:
- Flask: No native async support
- Django: Too heavyweight for stateless API

### Database: Neon Serverless PostgreSQL

**Why**:
- Already used in Phase 2 (existing infrastructure)
- Serverless auto-scaling matches stateless architecture
- Connection pooling handles concurrent requests
- Free tier sufficient for development/testing

**Connection Strategy**: Use SQLModel with connection pooling, `pool_pre_ping=True` for serverless

### ORM: SQLModel

**Why**:
- Combines SQLAlchemy (powerful ORM) + Pydantic (validation)
- Type hints for IDE autocomplete and error checking
- Async support via SQLAlchemy 2.0
- Consistent with Python 3.10+ type system

**Models**: Task (existing), Conversation (new), Message (new)

### AI: OpenAI Agents SDK + GPT-4o

**Why**:
- Agents SDK provides tool calling abstraction
- GPT-4o has strong tool-use capabilities and reliability
- Official SDK handles retries and error cases
- Good balance of cost and performance

**Alternatives Considered**:
- Claude API: No agents SDK equivalent
- Open source models: Lower reliability for tool calling

**Configuration**:
```python
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

agent = client.beta.assistants.create(
    model="gpt-4o",
    tools=[add_task_tool, list_tasks_tool, ...],
    instructions="You are a task management assistant..."
)
```

### MCP SDK: Official Python MCP SDK

**Why**:
- Standardized protocol for tool definitions
- Type-safe tool registration
- Clear separation between AI logic and database operations

**Tool Definition Pattern**:
```python
from mcp import Tool, Parameter

add_task_tool = Tool(
    name="add_task",
    description="Create a new task for the user",
    parameters=[
        Parameter(name="user_id", type="string", required=True),
        Parameter(name="title", type="string", required=True),
        Parameter(name="description", type="string", required=False)
    ]
)
```

### Frontend: Next.js + OpenAI ChatKit

**Why**:
- ChatKit provides pre-built chat UI components
- Next.js already used in Phase 2
- API routes for chat endpoint
- Server-side rendering for initial chat history load

## Database Schema Design

### Existing: Task Table (Phase 2)
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

**No changes to existing table**

### New: Conversation Table
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

**Purpose**: Group messages into conversations (future: allow multiple conversations per user)

### New: Message Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

**Purpose**: Store all chat messages for conversation history and context

### Data Isolation Strategy

**Rule**: Every query MUST filter by user_id

```python
# Good: User isolation enforced
tasks = await session.execute(
    select(Task).where(Task.user_id == current_user_id)
)

# Bad: Security violation - can access other users' data
tasks = await session.execute(select(Task))  # ❌ NO!
```

## API Design

### Endpoint: POST /api/chat

**Purpose**: Handle chat message submission and return AI response

**Request**:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": 123  // Optional: creates new if omitted
}
```

**Response**:
```json
{
  "conversation_id": 123,
  "message_id": 456,
  "response": "✓ Created task: Buy groceries (ID: 789)",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"title": "Buy groceries"},
      "result": {"id": 789, "title": "Buy groceries", "completed": false}
    }
  ]
}
```

**Flow**:
1. Extract `user_id` from JWT token (via `get_current_user` dependency)
2. Save user message to database
3. Fetch last 10 messages for context
4. Initialize OpenAI Agent with MCP tools
5. Run agent with (history + new message)
6. Agent executes tools (e.g., `add_task`)
7. Save assistant response to database
8. Return response to client
9. **Garbage collect agent instance** (stateless)

### Authentication

**Method**: JWT tokens from Phase 2 (Better Auth)

**Validation**: FastAPI dependency `get_current_user()`
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid authentication")
    return user_id
```

## MCP Tools Implementation

### Tool 1: add_task

**Signature**: `add_task(user_id: str, title: str, description: Optional[str] = None)`

**Logic**:
1. Validate inputs (title not empty)
2. Create Task instance with user_id
3. Save to database
4. Return task details

**Return**: `{"id": int, "title": str, "completed": bool}`

### Tool 2: list_tasks

**Signature**: `list_tasks(user_id: str, status: str = "all")`

**Logic**:
1. Query tasks with `WHERE user_id = user_id`
2. Apply status filter:
   - "all": return all tasks
   - "pending": `WHERE completed = False`
   - "completed": `WHERE completed = True`
3. Order by created_at DESC
4. Return list of tasks

**Return**: `[{"id": int, "title": str, "completed": bool}, ...]`

### Tool 3: complete_task

**Signature**: `complete_task(user_id: str, task_id: int)`

**Logic**:
1. Fetch task with `WHERE id = task_id AND user_id = user_id`
2. If not found: return error
3. Set `completed = True`
4. Update `updated_at` timestamp
5. Commit to database
6. Return updated task

**Return**: `{"id": int, "title": str, "completed": True}`

### Tool 4: delete_task

**Signature**: `delete_task(user_id: str, task_id: int)`

**Logic**:
1. Fetch task with `WHERE id = task_id AND user_id = user_id`
2. If not found: return error
3. Delete from database
4. Commit transaction
5. Return confirmation

**Return**: `{"success": True, "message": "Task deleted"}`

### Tool 5: update_task

**Signature**: `update_task(user_id: str, task_id: int, title: Optional[str], description: Optional[str])`

**Logic**:
1. Fetch task with `WHERE id = task_id AND user_id = user_id`
2. If not found: return error
3. Update fields that are provided (not None)
4. Update `updated_at` timestamp
5. Commit to database
6. Return updated task

**Return**: `{"id": int, "title": str, "description": str}`

## Agent Configuration

### System Prompt

```
You are a helpful task management assistant. You help users manage their todo tasks through natural language.

When a user asks to:
- Create/add a task → use add_task tool
- Show/list tasks → use list_tasks tool
- Complete/finish a task → use complete_task tool
- Delete/remove a task → use delete_task tool
- Update/change a task → use update_task tool

Always confirm actions to the user. If a task ID is mentioned, use it directly. If a task title is mentioned, first use list_tasks to find the ID.

Be friendly and concise. Acknowledge successful operations with ✓ emoji.
```

### Context Window

**Size**: Last 10 messages (5 user + 5 assistant)

**Rationale**:
- Sufficient for task context (e.g., "Delete that task" referring to previously created task)
- Keeps token usage reasonable (GPT-4o pricing)
- Balances context vs. performance

**Implementation**:
```python
async def get_conversation_context(conversation_id: int, limit: int = 10):
    messages = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    return messages.scalars().all()[::-1]  # Reverse to chronological order
```

## Error Handling Strategy

### OpenAI API Errors

**Scenario**: API rate limit exceeded, timeout, service unavailable

**Handling**:
- Catch `openai.RateLimitError`, `openai.Timeout`, `openai.APIError`
- Return user-friendly message: "AI service temporarily unavailable. Please try again in a moment."
- Log error with context for monitoring
- Return HTTP 503 Service Unavailable

**Code**:
```python
try:
    response = await agent.run(...)
except openai.RateLimitError:
    return JSONResponse(
        status_code=503,
        content={"error": "AI service is busy. Please try again shortly."}
    )
```

### Database Errors

**Scenario**: Connection lost, query timeout, constraint violation

**Handling**:
- Catch `sqlalchemy.exc.SQLAlchemyError`
- Retry transient errors (connection issues) up to 3 times
- Return error message: "Database temporarily unavailable. Please retry."
- Log error with query details

**Code**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def save_message(message: Message):
    async with get_session() as session:
        session.add(message)
        await session.commit()
```

### MCP Tool Errors

**Scenario**: Invalid task ID, task not found, validation failure

**Handling**:
- Return structured error in tool response: `{"success": False, "error": "Task not found"}`
- Agent interprets error and rephrases for user: "I couldn't find that task. Please check the task ID."
- Never crash or return stack traces

## Performance Considerations

### Database Query Optimization

**Indexes**:
- `tasks(user_id)` - for filtering user's tasks
- `conversations(user_id)` - for fetching user's conversations
- `messages(conversation_id)` - for fetching conversation history
- `messages(created_at)` - for ordering messages chronologically

**Query Strategy**:
- Use SELECT with specific columns (avoid SELECT *)
- Limit conversation history to 10 messages (context window)
- Use connection pooling for concurrent requests

### Caching Strategy

**Decision**: No caching at application level

**Rationale**: Stateless architecture means no in-memory cache. Database is source of truth. Neon PostgreSQL has internal caching.

**Alternative**: Could add Redis for conversation history caching in future if performance issues arise.

### Async/Await

**Requirement**: All database operations MUST use async/await

**Benefit**: Non-blocking I/O allows server to handle multiple requests concurrently while waiting for database or OpenAI API

**Example**:
```python
async def create_task(user_id: str, title: str):
    async with get_async_session() as session:
        task = Task(user_id=user_id, title=title)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task
```

## Testing Strategy

### Unit Tests

**Scope**: MCP tools in isolation

**Tests**:
- `test_add_task_success()` - Create task with valid inputs
- `test_add_task_empty_title()` - Reject empty title
- `test_list_tasks_filters()` - Verify status filtering works
- `test_complete_task_not_found()` - Return error for invalid ID
- `test_user_isolation()` - User A cannot access User B's tasks

**Framework**: pytest with pytest-asyncio

### Integration Tests

**Scope**: Full API endpoint with database

**Tests**:
- `test_chat_endpoint_create_task()` - End-to-end task creation via chat
- `test_conversation_persistence()` - Messages survive across requests
- `test_jwt_auth_required()` - Endpoint rejects unauthenticated requests
- `test_stateless_behavior()` - Two identical requests produce same result

### Manual Testing Checklist

1. Create task via chat: "Add a task to buy milk"
2. List tasks: "Show me my tasks"
3. Complete task: "Mark task 1 as done"
4. Update task: "Change task 1 to 'Buy organic milk'"
5. Delete task: "Delete task 1"
6. Refresh page → verify chat history loads
7. Restart server → verify no data loss

## Deployment Considerations

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Auth (from Phase 2)
JWT_SECRET=...
JWT_EXPIRATION=86400

# API
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Migration Strategy

**Phase 2 → Phase 3 Migration**:
1. Create new tables: `conversations`, `messages`
2. Existing `tasks` table unchanged (no downtime)
3. Deploy new backend with chat endpoint
4. Deploy frontend with ChatKit UI
5. Users can use both old UI and new chat interface

**Rollback Plan**: Disable chat endpoint, revert to Phase 2 frontend. No data loss (task table unchanged).

## Future Enhancements (Out of Scope for Phase 3)

- Multiple conversations per user (conversation switcher UI)
- Task categories and tags via chat
- Natural language date parsing ("Add task due tomorrow")
- Voice input/output
- Conversation export
- AI-suggested tasks based on history
- Bulk operations ("Complete all tasks")

---

**Version**: 1.0.0 | **Created**: 2025-12-30 | **Status**: Ready for Implementation
