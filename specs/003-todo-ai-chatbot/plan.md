# Implementation Plan: Todo AI Chatbot

**Branch**: `003-todo-ai-chatbot` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-todo-ai-chatbot/spec.md`

## Summary

Transform the Phase 2 Todo Web Application into an AI-powered chatbot where users manage tasks via natural language. The system uses OpenAI Agents SDK with Model Context Protocol (MCP) tools to connect the AI to the existing task database. Key flow: ChatKit UI → FastAPI → AI Agent → MCP Tools → SQLModel → Neon PostgreSQL.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, MCP Python SDK, SQLModel, Next.js 16+, OpenAI ChatKit
**Storage**: Neon PostgreSQL (existing from Phase 2) + new Conversation/Message tables
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: Web application (browser-based)
**Project Type**: Web (frontend + backend)
**Performance Goals**: <5s task creation via chat, <3s task list via chat, <2s history load
**Constraints**: Stateless backend, JWT auth required, user_id isolation mandatory
**Scale/Scope**: Same user base as Phase 2, single conversation per user initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. Stateless by Design | FastAPI server stateless, no in-memory agent state | ✅ PASS |
| II. Tool Determinism | MCP tools strictly typed, return errors not crashes | ✅ PASS |
| III. Security Propagation | user_id from JWT → Agent → MCP Tools | ✅ PASS |
| IV. Conversation Persistence | All messages in Neon DB, survives restart | ✅ PASS |
| V. Atomic Operations | Task modifications commit immediately | ✅ PASS |
| VI. User Experience | Loading states, error clarity, graceful degradation | ✅ PASS |

**Gate Status**: ✅ ALL GATES PASS - Proceed to implementation

## Project Structure

### Documentation (this feature)

```text
specs/003-todo-ai-chatbot/
├── constitution.md      # Feature-specific constitution
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research output
├── data-model.md        # Data model definitions
├── quickstart.md        # Setup and run guide
├── contracts/           # API contracts
│   └── api.yaml
├── checklists/          # Quality checklists
│   └── requirements.md
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py          # Existing from Phase 2
│   │   ├── user.py          # Existing from Phase 2
│   │   ├── conversation.py  # NEW: Chat conversation model
│   │   └── message.py       # NEW: Chat message model
│   ├── services/
│   │   ├── task_service.py  # Existing from Phase 2
│   │   └── chat_service.py  # NEW: Chat orchestration
│   ├── api/
│   │   ├── tasks.py         # Existing from Phase 2
│   │   ├── auth.py          # Existing from Phase 2
│   │   └── chat.py          # NEW: Chat endpoints
│   ├── mcp/
│   │   ├── __init__.py      # NEW: MCP package
│   │   ├── server.py        # NEW: MCP server setup
│   │   └── tools.py         # NEW: MCP tool definitions
│   └── agent/
│       ├── __init__.py      # NEW: Agent package
│       └── chat_agent.py    # NEW: OpenAI agent wrapper
└── tests/
    ├── unit/
    │   └── test_mcp_tools.py    # NEW: MCP tool tests
    ├── integration/
    │   └── test_chat_api.py     # NEW: Chat API tests
    └── contract/

frontend/
├── src/
│   ├── components/
│   │   ├── TaskList.tsx         # Existing from Phase 2
│   │   ├── ChatInterface.tsx    # NEW: Main chat component
│   │   ├── ChatMessage.tsx      # NEW: Message bubble component
│   │   └── ChatInput.tsx        # NEW: Message input component
│   ├── pages/
│   │   ├── dashboard/           # Existing from Phase 2
│   │   └── chat/                # NEW: Chat page
│   │       └── index.tsx
│   └── services/
│       ├── taskApi.ts           # Existing from Phase 2
│       └── chatApi.ts           # NEW: Chat API client
└── tests/
```

**Structure Decision**: Web application structure extending Phase 2 with new backend MCP/Agent modules and frontend chat components.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │     │   Backend       │     │   Database      │
│   (Next.js)     │     │   (FastAPI)     │     │   (Neon)        │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ ChatInterface   │────▶│ POST /chat      │     │ conversations   │
│ ChatKit UI      │     │                 │     │ messages        │
│                 │◀────│ JWT Validation  │     │ tasks           │
└─────────────────┘     │       │         │     │ users           │
                        │       ▼         │     └─────────────────┘
                        │ ┌───────────┐   │            ▲
                        │ │ AI Agent  │   │            │
                        │ │ (OpenAI)  │   │            │
                        │ └─────┬─────┘   │            │
                        │       │         │            │
                        │       ▼         │            │
                        │ ┌───────────┐   │            │
                        │ │ MCP Tools │───┼────────────┘
                        │ │ (5 tools) │   │   SQLModel
                        │ └───────────┘   │
                        └─────────────────┘
```

## Data Flow (Per Chat Request)

1. **Frontend** sends message via POST /api/{user_id}/chat
2. **API Layer** validates JWT, extracts user_id
3. **Chat Service** saves user message to DB
4. **Chat Service** fetches last 10 messages for context
5. **AI Agent** receives message + context + user_id
6. **AI Agent** calls MCP tools as needed (with user_id)
7. **MCP Tools** execute DB operations atomically
8. **AI Agent** generates response
9. **Chat Service** saves assistant response to DB
10. **API Layer** returns response to frontend

## MCP Tools Specification

| Tool | Parameters | Returns | DB Operation |
|------|------------|---------|--------------|
| `add_task` | user_id, title, description? | Task object | INSERT |
| `list_tasks` | user_id, status? | Task[] | SELECT |
| `complete_task` | user_id, task_id | Task object | UPDATE |
| `delete_task` | user_id, task_id | Success/Error | DELETE |
| `update_task` | user_id, task_id, title?, description? | Task object | UPDATE |

**Critical**: All tools receive `user_id` from API layer, NOT from AI inference.

## Complexity Tracking

> No constitution violations identified. Design follows all 6 principles.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Agent Framework | OpenAI Agents SDK | User requirement, mature ecosystem |
| Tool Protocol | MCP | User requirement, standardized interface |
| State Management | Stateless per request | Constitution Principle I |
| Security | Explicit user_id propagation | Constitution Principle III |

## Risk Mitigations

| Risk | Mitigation | Implementation |
|------|------------|----------------|
| AI hallucination | Tool validation | MCP tools validate all IDs before DB ops |
| Rate limiting | Queue + feedback | Show loading states, queue requests |
| Cost overrun | Monitoring | Log API calls, set up alerts |
| Security bypass | Explicit user_id | Never infer user_id from AI context |

## Dependencies

### External Services

- **OpenAI API**: AI agent inference (API key required)
- **Neon PostgreSQL**: Data persistence (connection string from Phase 2)

### Internal Dependencies

- **Phase 2 Auth**: JWT token validation, user management
- **Phase 2 Tasks**: Existing task CRUD operations, database schema

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement in priority order (P1 user stories first)
3. Validate against constitution after each phase
