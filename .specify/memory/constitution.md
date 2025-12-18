<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.1.0
Bump rationale: MINOR - User Experience principle completed with 5 sub-rules

Added/Updated sections:
- AI & MCP Architecture Principles (Stateless, Tool Determinism, Security Propagation)
- Data Integrity & Persistence (Conversation Persistence, Atomic Operations)
- User Experience (Responsive Feedback, Error Clarity, Conversation Context, Real-time Feel, Graceful Degradation)
- Governance rules

Templates status:
- .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
- .specify/templates/spec-template.md: ✅ Compatible
- .specify/templates/tasks-template.md: ✅ Compatible

Follow-up TODOs: None
-->

# Todo AI Chatbot Constitution

## Core Principles

### I. Stateless by Design

The FastAPI server MUST remain stateless. Every chat request is an independent transaction following this flow:

1. Fetch conversation history from database
2. Run AI Agent with context
3. Save response to database

**Non-negotiable rules:**
- Do NOT rely on in-memory agent state between requests
- Each request MUST be self-contained and repeatable
- Server restart MUST NOT affect conversation continuity

**Rationale:** Stateless design enables horizontal scaling, simplifies debugging, and ensures reliability across deployments.

### II. Tool Determinism

MCP tools MUST be strictly typed with predictable behavior.

**Non-negotiable rules:**
- All tool inputs MUST be validated before execution
- If the AI hallucinates an ID that doesn't exist, the tool MUST return a clear error message, NOT crash
- Tool responses MUST be structured and parseable
- Invalid operations MUST fail gracefully with actionable error messages

**Rationale:** Deterministic tools prevent cascading failures and provide clear feedback for AI self-correction.

### III. Security Propagation

The `user_id` extracted from the JWT token at the API layer MUST be passed explicitly through the entire request chain.

**Non-negotiable rules:**
- user_id MUST be extracted from JWT at API layer
- user_id MUST be passed explicitly to the AI Agent
- user_id MUST be passed to every MCP Tool call
- The AI is NOT allowed to guess, infer, or fabricate the user ID
- All database queries MUST include `WHERE user_id = current_user` clause

**Rationale:** Explicit security propagation prevents privilege escalation and ensures strict multi-tenant data isolation.

### IV. Conversation Persistence

All chat messages (User and Assistant) MUST be stored in the `messages` table in Neon DB.

**Non-negotiable rules:**
- Every user message MUST be persisted before processing
- Every assistant response MUST be persisted after generation
- Loss of history on server restart is NOT acceptable
- Messages MUST be linked to correct user_id with timestamp ordering

**Rationale:** Persistent conversations enable context continuity and provide audit trail for debugging.

### V. Atomic Operations

Task modifications via MCP tools MUST commit to the database immediately.

**Non-negotiable rules:**
- ADD operations MUST commit immediately upon success
- UPDATE operations MUST commit immediately upon success
- DELETE operations MUST commit immediately upon success
- No partial or uncommitted state is acceptable
- Failed operations MUST NOT leave orphaned or inconsistent data

**Rationale:** Atomic operations ensure data integrity and prevent race conditions in concurrent environments.

### VI. User Experience

The AI chatbot MUST provide a seamless, responsive user experience.

**Non-negotiable rules:**
- **Responsive Feedback:** Loading states MUST be shown during AI processing to indicate activity
- **Error Clarity:** Error messages MUST be user-friendly and actionable, not technical stack traces
- **Conversation Context:** Chat history MUST be visible on page load, fetched from database
- **Real-time Feel:** Responses SHOULD feel natural with appropriate timing (streaming preferred)
- **Graceful Degradation:** If AI service is unavailable, system MUST show clear status message

**Rationale:** Good UX builds user trust and encourages adoption. Users must never feel lost or confused about system state.

## Data Integrity & Persistence

This section consolidates data handling requirements across the AI chatbot system.

**Database Requirements:**
- Neon PostgreSQL for all persistent storage
- messages table for chat history with user_id foreign key
- tasks table modifications via MCP tools only
- All tables MUST have appropriate indexes for query performance

**Consistency Guarantees:**
- Read-after-write consistency for all operations
- No stale data served from cache without validation
- Transaction isolation for concurrent modifications

## Development Workflow

**Code Quality Gates:**
- All MCP tools MUST have type hints and validation
- API endpoints MUST validate JWT before processing
- Error responses MUST follow consistent format
- Logging MUST include request context (user_id, request_id)

**Testing Requirements:**
- MCP tools MUST have unit tests for success and error cases
- API endpoints MUST have integration tests
- Security propagation MUST be verified in tests

## Governance

This constitution supersedes all other development practices for the Todo AI Chatbot project.

**Amendment Procedure:**
1. Propose changes via PR with rationale
2. Review impact on existing code and templates
3. Update version following semantic versioning
4. Document changes in Sync Impact Report

**Versioning Policy:**
- MAJOR: Backward incompatible principle changes or removals
- MINOR: New principles added or materially expanded guidance
- PATCH: Clarifications, wording fixes, non-semantic refinements

**Compliance:**
- All PRs MUST verify compliance with constitution principles
- Violations MUST be documented and justified if unavoidable
- Regular audits of codebase against constitution rules

**Version**: 1.1.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
