---
id: 0003
title: Phase 3 AI Chatbot Constitution
stage: constitution
date: 2025-12-16
surface: agent
model: claude-opus-4-5-20251101
feature: 003-todo-ai-chatbot
branch: 001-basic-todo-ops
user: user
command: /sp.constitution
labels: ["constitution", "phase3", "ai-chatbot", "mcp"]
links:
  spec: specs/003-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

/sp.constitution

**1. AI & MCP Architecture Principles**

*   **Stateless by Design:** The FastAPI server must remain stateless. Every chat request is an independent transaction: Fetch History -> Run Agent -> Save Response. Do not rely on in-memory agent state between requests.

*   **Tool Determinism:** MCP tools must be strictly typed. If the AI hallucinates an ID that doesn't exist, the tool must return a clear error, not crash.

*   **Security Propagation:** The `user_id` extracted from the JWT token at the API layer must be passed explicitly to the AI Agent, and then passed to every MCP Tool call. The AI is not allowed to guess the user ID.



**2. Data Integrity & Persistence**

*   **Conversation Persistence:** All chat messages (User and Assistant) must be stored in the `messages` table in Neon DB. Loss of history on server restart is not acceptable.

*   **Atomic Operations:** Task modifications via MCP tools (Add/Update/Delete) must commit to the database immediately.



**3. User Experience**

*  (incomplete - awaiting user input)

## Response snapshot

Constitution updated to v1.0.0 with Phase 3: Todo AI Chatbot principles:

1. **I. Stateless by Design** - FastAPI server stateless, each request independent
2. **II. Tool Determinism** - MCP tools strictly typed, graceful error handling
3. **III. Security Propagation** - user_id from JWT passed through entire chain
4. **IV. Conversation Persistence** - All messages stored in Neon DB
5. **V. Atomic Operations** - Immediate database commits for task modifications
6. **VI. User Experience** - TODO placeholder (awaiting user input)

Added sections: Data Integrity & Persistence, Development Workflow, Governance

## Outcome

- ✅ Impact: Constitution established for Phase 3 AI Chatbot with 5 core principles
- 🧪 Tests: N/A (documentation)
- 📁 Files: .specify/memory/constitution.md updated
- 🔁 Next prompts: Complete User Experience principle, update plan.md Constitution Check
- 🧠 Reflection: User input was incomplete for UX section; marked as TODO for follow-up

## Evaluation notes (flywheel)

- Failure modes observed: Incomplete user input (UX section cut off)
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Ask user to complete UX principles
