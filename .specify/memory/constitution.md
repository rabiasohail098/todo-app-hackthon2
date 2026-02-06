<!--
SYNC IMPACT REPORT
==================
Version change: 2.0.0 → 2.1.0
Bump rationale: MINOR - Added 6 new principles for scalability, robustness, and performance to support Phase 4 intermediate features

Modified sections:
- None (existing principles unchanged)

Added sections:
- Principle VIII: Type Safety & Validation
- Principle IX: Natural Language Robustness
- Principle X: Database Performance
- Principle XI: Modular Service Architecture
- Principle XII: Observability & Feedback Loops
- Principle XIII: Scalability & Resource Management

Removed sections:
- None

Templates status:
- .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
- .specify/templates/spec-template.md: ✅ Compatible
- .specify/templates/tasks-template.md: ✅ Compatible

Follow-up TODOs:
- None (principles are additive and support upcoming Phase 4 features)

Previous version change: 1.1.0 → 2.0.0 (2025-12-30)
- MAJOR - Architectural shift from OpenAI Agents SDK + MCP to OpenRouter direct integration
-->

# Todo AI Chatbot Constitution

**Project**: Todo Application - Phase 3: AI-Powered Chatbot Interface
**Version**: 2.1.0
**Ratified**: 2025-12-16
**Last Amended**: 2025-12-31

## Purpose

This constitution defines the non-negotiable principles for building an AI-powered chatbot interface that enables natural language task management using OpenRouter API for LLM capabilities and Chat Kit for the frontend UI.

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | OpenAI Chat Kit |
| Backend | Python FastAPI |
| AI Provider | OpenRouter API (meta-llama/llama-3.2-3b-instruct:free) |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth (JWT) |

## Core Principles

### I. Stateless by Design

The FastAPI server MUST remain stateless. Every chat request is an independent transaction following this flow:

1. Extract user_id from JWT token
2. Fetch conversation history from database (last N messages for context)
3. Call OpenRouter API with user message + context
4. Parse AI response and execute any task operations
5. Save both user message and AI response to database
6. Return response to client

**Non-negotiable rules:**
- Do NOT rely on in-memory session state between requests
- Each request MUST be self-contained and repeatable
- Server restart MUST NOT affect conversation continuity
- All conversation state MUST persist in the database

**Rationale:** Stateless design enables horizontal scaling, simplifies debugging, and ensures reliability across deployments.

### II. OpenRouter Integration

The chatbot MUST use OpenRouter API for AI inference with proper error handling and fallback strategies.

**Non-negotiable rules:**
- API key MUST be stored in environment variables, never hardcoded
- Base URL and model name MUST be configurable via environment variables
- API requests MUST have timeout limits (30 seconds max)
- Failed API calls MUST return user-friendly error messages, not crash
- Rate limiting and quota errors MUST be handled gracefully
- Response parsing MUST handle both plain text and structured outputs

**Rationale:** OpenRouter provides free-tier LLM access with proper abstraction, enabling cost-effective AI capabilities while maintaining flexibility to switch models.

### III. Security Propagation

The `user_id` extracted from the JWT token at the API layer MUST be passed explicitly through the entire request chain.

**Non-negotiable rules:**
- user_id MUST be extracted from JWT at API layer (via get_current_user dependency)
- user_id MUST be used in all database queries for tasks and conversations
- The AI is NOT allowed to guess, infer, or fabricate the user ID
- All database queries MUST include `WHERE user_id = current_user` clause
- Task operations MUST verify task ownership before modifications

**Rationale:** Explicit security propagation prevents privilege escalation and ensures strict multi-tenant data isolation.

### IV. Conversation Persistence

All chat messages (user and assistant) MUST be stored in the database to enable context continuity.

**Non-negotiable rules:**
- Every user message MUST be persisted BEFORE processing
- Every assistant response MUST be persisted AFTER generation
- Messages MUST be linked to correct user_id and conversation_id
- Timestamps MUST be recorded for message ordering
- Loss of history on server restart is NOT acceptable
- Chat history MUST be fetchable for context window (last 10 messages recommended)

**Rationale:** Persistent conversations enable context continuity, improve AI responses, and provide audit trail for debugging.

### V. Atomic Operations

Task modifications via chat commands MUST commit to the database immediately and atomically.

**Non-negotiable rules:**
- CREATE operations MUST commit immediately upon success
- UPDATE operations MUST commit immediately upon success
- DELETE operations MUST commit immediately upon success
- COMPLETE operations MUST commit immediately upon success
- No partial or uncommitted state is acceptable
- Failed operations MUST NOT leave orphaned or inconsistent data
- Database transactions MUST be used for multi-step operations

**Rationale:** Atomic operations ensure data integrity and prevent race conditions in concurrent environments.

### VI. User Experience with Chat Kit

The chatbot frontend MUST use Chat Kit to provide a seamless, responsive conversational interface.

**Non-negotiable rules:**
- **Chat Kit Integration:** Frontend MUST use OpenAI Chat Kit components for UI
- **Responsive Feedback:** Loading states MUST be shown during AI processing
- **Error Clarity:** Error messages MUST be user-friendly and actionable, not technical stack traces
- **Conversation Context:** Chat history MUST load on page open (last 50 messages)
- **Message Display:** Both user and assistant messages MUST be displayed with clear role distinction
- **Real-time Feel:** Messages MUST appear smoothly without jarring UI shifts
- **Graceful Degradation:** If AI service unavailable, show clear status message with retry option
- **Input Validation:** Empty messages MUST be prevented, long messages (>10000 chars) MUST be truncated or rejected

**Rationale:** Chat Kit provides battle-tested UI patterns for conversational interfaces, ensuring professional UX that users expect from modern chat applications.

### VII. Intent Recognition and Action Execution

The AI agent MUST correctly interpret natural language commands and execute appropriate task operations.

**Non-negotiable rules:**
- AI responses MAY include structured action data (JSON format) for task operations
- Supported actions: create_task, list_tasks, complete_task, delete_task, update_task
- Each action MUST validate required parameters before execution
- Task operations MUST use TaskService for database interactions
- Successful actions MUST return confirmation with task details
- Failed actions MUST return clear error messages
- Ambiguous commands SHOULD prompt for clarification before executing destructive operations

**Rationale:** Clear intent recognition and deterministic execution ensure users can reliably manage tasks through natural language without frustration.

### VIII. Type Safety & Validation

All data entering and leaving the system MUST be validated and type-safe to prevent runtime errors and security vulnerabilities.

**Non-negotiable rules:**
- All API request bodies MUST use Pydantic models for validation
- All API response bodies MUST use Pydantic models for serialization
- Database models MUST use SQLModel with explicit type annotations
- Frontend-backend contracts MUST have matching TypeScript/Python types
- Input validation MUST happen at API boundary before processing
- Validation errors MUST return 422 status with clear field-level errors
- No `Any` types allowed in production code without explicit justification
- Optional fields MUST be marked explicitly with `Optional[T]` or `T | None`
- String lengths MUST be validated (task title max 200 chars, message max 10,000 chars)
- Enum types MUST be used for fixed sets (priority levels, recurrence patterns)

**Rationale:** Strong typing catches bugs at development time, prevents invalid data from corrupting the database, and provides clear API contracts that self-document the system.

### IX. Natural Language Robustness

The AI agent MUST handle diverse natural language inputs gracefully, including ambiguity, multilingual content, and malformed requests.

**Non-negotiable rules:**
- Language detection MUST be automatic or explicitly provided by user
- Multilingual support MUST include translation fallback for non-English queries
- Ambiguous commands MUST prompt for clarification (e.g., "which task?" when multiple match)
- Unrecognized intents MUST respond with helpful suggestions, not errors
- Date parsing MUST handle natural formats ("tomorrow", "next Friday", "in 3 days")
- Task references MUST accept both IDs (#5) and fuzzy title matching ("milk task")
- AI responses MUST be consistent in format (use structured output when possible)
- Failed LLM calls MUST have fallback responses ("I'm having trouble connecting...")
- Prompt engineering MUST include few-shot examples for consistency
- Context window limits MUST be respected (last 10 messages for context)

**Rationale:** Natural language is inherently ambiguous; robust handling ensures users don't get frustrated by the AI misunderstanding common inputs or edge cases.

### X. Database Performance

Database queries MUST be optimized for performance as the dataset grows, with proper indexing and query patterns.

**Non-negotiable rules:**
- All foreign keys MUST have indexes (`user_id`, `conversation_id`, `category_id`, `task_id`)
- Frequently filtered columns MUST have indexes (`priority`, `due_date`, `is_completed`)
- Full-text search MUST use PostgreSQL `tsvector` with GIN indexes
- Pagination MUST be implemented for list endpoints (default 50, max 100 per page)
- N+1 query problems MUST be avoided (use eager loading with `selectinload`)
- Soft deletes MUST be considered for audit trail (add `deleted_at` instead of hard delete)
- Database connection pooling MUST be configured (SQLAlchemy pool settings)
- Expensive queries (statistics, search) MUST have query timeouts (5 seconds max)
- Query complexity MUST be analyzed with `EXPLAIN ANALYZE` during development
- Bulk operations MUST use batch inserts/updates (not individual queries in loop)

**Rationale:** Performance degrades non-linearly as data grows; proper indexing and query patterns ensure the app remains responsive with 10,000+ tasks.

### XI. Modular Service Architecture

Business logic MUST be organized in service layers separate from API routes and database models.

**Non-negotiable rules:**
- API routes MUST only handle HTTP concerns (request/response, auth, validation)
- Business logic MUST live in service classes (`TaskService`, `ChatService`, `CategoryService`)
- Database operations MUST be abstracted in service methods (not in routes)
- Services MUST accept `db: Session` and `user_id: str` as explicit parameters
- Services MUST return domain objects or raise domain-specific exceptions
- Cross-service dependencies MUST be injected (not imported directly)
- Each service MUST have a clear single responsibility
- Utility functions MUST be pure and stateless (in `utils/` directory)
- AI agent logic MUST be isolated in `ChatAgent` class (not mixed with service)
- File organization MUST follow: `api/routes/`, `services/`, `models/`, `agent/`, `utils/`

**Rationale:** Modular architecture enables easier testing (mock services), clearer separation of concerns, and allows swapping implementations without affecting routes.

### XII. Observability & Feedback Loops

The system MUST provide visibility into operations and errors to enable debugging and monitoring.

**Non-negotiable rules:**
- All API requests MUST log: timestamp, user_id, endpoint, status_code, duration
- All errors MUST log: exception type, message, stack trace, request context
- LLM API calls MUST log: model, prompt length, response length, latency, cost (if tracked)
- Database queries MUST log slow queries (>1 second)
- Structured logging MUST be used (JSON format) with correlation IDs
- User-facing errors MUST NOT leak implementation details or stack traces
- Health check endpoint MUST exist (`GET /health`) checking database connectivity
- Metrics MUST be collectable: request rate, error rate, p95 latency, active users
- Background jobs (if any) MUST report status and progress
- Deployment logs MUST include version number and changelog reference

**Rationale:** Observability enables proactive issue detection, faster debugging, and data-driven optimization decisions.

### XIII. Scalability & Resource Management

The system MUST be designed to handle increased load without degradation or resource exhaustion.

**Non-negotiable rules:**
- Stateless request handling MUST allow horizontal scaling (multiple server instances)
- File uploads (attachments) MUST use cloud storage (S3/Cloudinary), not local filesystem
- Large responses MUST be paginated (never return all 10,000 tasks at once)
- Rate limiting MUST be implemented (10 requests/second per user for write operations)
- LLM API calls MUST have circuit breakers (pause requests if error rate >50%)
- Background processing MUST be used for heavy tasks (bulk imports, file scanning)
- Caching MUST be used for expensive reads (statistics: cache for 1 hour)
- Database connections MUST be pooled and limited (max 20 connections per instance)
- Memory limits MUST be set for request processing (max 100MB per request)
- Graceful degradation MUST occur under load (return cached data if DB slow)

**Rationale:** Scalability ensures the app remains responsive and reliable as user base and data volume grow, without requiring complete rewrites.

## Data Models

### Conversation Model

```python
class Conversation:
    id: int (PK)
    user_id: str (FK, indexed)
    created_at: datetime
    updated_at: datetime
```

### Message Model

```python
class Message:
    id: int (PK)
    conversation_id: int (FK, indexed)
    user_id: str (FK, indexed)
    role: str (enum: "user", "assistant")
    content: str (text)
    created_at: datetime
```

### Task Model (existing from Phase 2)

```python
class Task:
    id: int (PK)
    user_id: str (FK, indexed)
    title: str (max 200 chars)
    description: str | None (text)
    is_completed: bool (default False)
    created_at: datetime
    updated_at: datetime
```

## API Endpoints

### Chat Endpoint

**POST /api/chat**

Request:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": 123  // optional, creates new if omitted
}
```

Response:
```json
{
  "conversation_id": 123,
  "response": "✓ Created task: Buy groceries",
  "type": "task_created",  // message | task_created | task_list | error
  "task": {  // optional, included when relevant
    "id": 45,
    "title": "Buy groceries",
    "is_completed": false
  }
}
```

### Conversation History

**GET /api/conversations/{id}/messages**

Response:
```json
{
  "messages": [
    {"role": "user", "content": "Add task...", "created_at": "2025-12-30T10:00:00Z"},
    {"role": "assistant", "content": "✓ Created task...", "created_at": "2025-12-30T10:00:01Z"}
  ]
}
```

## Natural Language Commands

The chatbot MUST understand and respond to:

| User Input | Expected Action |
|------------|----------------|
| "Add a task to buy groceries" | create_task with title="Buy groceries" |
| "Show me my tasks" | list_tasks with status="all" |
| "What's pending?" | list_tasks with status="pending" |
| "Mark task 3 as complete" | complete_task with task_id=3 |
| "Delete task 5" | delete_task with task_id=5 |
| "Change task 1 to 'Call mom tonight'" | update_task with new title |
| "What have I completed?" | list_tasks with status="completed" |

## Development Workflow

### Code Quality Gates

- All API endpoints MUST have type hints and Pydantic models
- Database operations MUST use SQLModel ORM (no raw SQL)
- Error handling MUST be comprehensive with specific error types
- Logging MUST include request context (user_id, conversation_id, timestamp)
- Environment variables MUST be validated on startup

### Testing Requirements

- Chat endpoint MUST have integration tests
- TaskService operations MUST have unit tests
- Security isolation MUST be verified (user A cannot access user B's data)
- Error scenarios MUST be tested (API timeout, invalid task ID, etc.)
- Happy path MUST be tested (create → list → complete → delete)

### Configuration Management

Required environment variables:

```env
# Database
DATABASE_URL=postgresql://...

# Authentication
JWT_SECRET=...
JWT_EXPIRATION=86400

# OpenRouter
OPENROUTER_API_KEY=...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free

# CORS
CORS_ORIGINS=http://localhost:3000
```

## Governance

This constitution supersedes all other development practices for the Todo AI Chatbot project (Phase 3).

### Amendment Procedure

1. Propose changes via Pull Request with rationale
2. Review impact on existing code, specs, and templates
3. Update version following semantic versioning rules
4. Document changes in Sync Impact Report (HTML comment at top)
5. Update dependent templates and documentation

### Versioning Policy

- **MAJOR (X.0.0)**: Backward incompatible architectural changes or principle removals
- **MINOR (X.Y.0)**: New principles added or materially expanded guidance
- **PATCH (X.Y.Z)**: Clarifications, wording fixes, non-semantic refinements

### Compliance

- All Pull Requests MUST verify compliance with constitution principles
- Code reviews MUST check for user_id isolation, statelessness, and error handling
- Violations MUST be documented and justified if unavoidable (with migration plan)
- Regular audits of codebase against constitution rules (quarterly)

### Conflict Resolution

If principles conflict in practice:
1. Security (Principle III) takes precedence over all others
2. Data integrity (Principles IV, V) takes precedence over UX
3. Statelessness (Principle I) takes precedence over performance optimizations
4. Document the trade-off in an ADR and seek team consensus

---

**Version**: 2.1.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-31
