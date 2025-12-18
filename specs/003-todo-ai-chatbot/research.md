# Research: Todo AI Chatbot

**Feature**: 003-todo-ai-chatbot
**Date**: 2025-12-16
**Status**: Complete

## Overview

Research findings for implementing AI chatbot functionality using OpenAI Agents SDK and Model Context Protocol (MCP).

## Technology Decisions

### 1. AI Agent Framework

**Decision**: OpenAI Agents SDK

**Rationale**:
- User requirement specified OpenAI Agents SDK
- Native tool/function calling support
- Mature ecosystem with extensive documentation
- Built-in conversation context management

**Alternatives Considered**:
- LangChain: More complex, unnecessary abstraction for this use case
- Direct OpenAI API: Lower level, would need to build agent logic manually
- Claude API: Different ecosystem, user specified OpenAI

### 2. Tool Protocol

**Decision**: Model Context Protocol (MCP)

**Rationale**:
- User requirement specified MCP
- Standardized interface for AI-tool communication
- Strict typing prevents tool misuse
- Clear error handling patterns

**Alternatives Considered**:
- Custom function definitions: Less standardized, harder to maintain
- OpenAI native functions: Tied to single provider

### 3. Frontend Chat UI

**Decision**: OpenAI ChatKit

**Rationale**:
- User requirement specified ChatKit
- Pre-built chat components optimized for AI interactions
- Handles streaming responses natively
- Easy integration with Next.js

**Alternatives Considered**:
- Custom chat UI: More development time
- Other chat libraries: Less optimized for AI use case

### 4. Backend Architecture

**Decision**: Stateless FastAPI with per-request agent instantiation

**Rationale**:
- Constitution Principle I: Stateless by Design
- Horizontal scalability
- No session affinity required
- Simpler debugging and testing

**Pattern**:
```
Request → Validate JWT → Fetch History → Create Agent → Process → Save → Response
```

### 5. Security Model

**Decision**: Explicit user_id propagation from JWT through entire chain

**Rationale**:
- Constitution Principle III: Security Propagation
- Prevents AI from guessing/fabricating user IDs
- Enforces multi-tenant isolation at every layer
- All MCP tools require user_id parameter

**Implementation**:
1. API extracts user_id from JWT `sub` claim
2. API passes user_id to chat service
3. Chat service passes user_id to agent context
4. Agent passes user_id to every MCP tool call
5. MCP tools use user_id in all DB queries

### 6. Data Persistence

**Decision**: Neon PostgreSQL with SQLModel ORM

**Rationale**:
- Phase 2 already uses Neon PostgreSQL
- SQLModel provides type safety with Pydantic
- Constitution Principle IV: Conversation Persistence
- Serverless-friendly connection pooling

**New Tables**:
- `conversations`: Chat session metadata
- `messages`: Individual chat messages

## Best Practices Research

### OpenAI Agents SDK

- Use `Runner` class for stateless agent execution
- Define tools with strict type hints
- Handle tool errors gracefully
- Implement retry logic for rate limits

### MCP Tools

- All inputs must be validated before execution
- Return structured responses (JSON-serializable)
- Include error field in response schema
- Log all tool invocations for debugging

### Chat Context Management

- Fetch last N messages (10 recommended) for context
- Include system prompt with user_id context
- Order messages by timestamp ascending
- Trim context if token limit approached

## Integration Patterns

### Frontend-Backend Communication

```
POST /api/{user_id}/chat
Headers: Authorization: Bearer <JWT>
Body: { message: string, conversation_id?: string }
Response: { response: string, tool_calls?: array }
```

### Agent-Tool Communication (MCP)

```python
@mcp_tool
def add_task(user_id: str, title: str, description: str = None) -> dict:
    # Validate inputs
    # Execute DB operation
    # Return result or error
```

## Performance Considerations

- Connection pooling for database (SQLAlchemy pooling)
- Async endpoints for non-blocking I/O
- Streaming responses for better UX (if supported)
- Cache conversation history for repeated requests

## Security Considerations

- JWT validation on every request
- user_id in URL must match JWT sub claim
- Never trust user_id from request body
- SQL injection prevention via ORM
- Rate limiting per user (future enhancement)

## References

- OpenAI Agents SDK Documentation
- Model Context Protocol Specification
- FastAPI Best Practices
- SQLModel Documentation
- Next.js App Router Documentation
