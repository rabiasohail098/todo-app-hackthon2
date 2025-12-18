# Quickstart: Todo AI Chatbot

**Feature**: 003-todo-ai-chatbot
**Date**: 2025-12-16
**Prerequisites**: Phase 2 Web App running and functional

## Overview

This guide walks you through setting up the AI chatbot feature that allows users to manage tasks via natural language conversation.

## Prerequisites

Before starting, ensure you have:

- [ ] Phase 2 Web App running (backend + frontend + database)
- [ ] Python 3.11+
- [ ] Node.js 18+
- [ ] OpenAI API key (with Agents SDK access)
- [ ] Neon PostgreSQL database (from Phase 2)

## Step 1: Environment Setup

### Backend Environment Variables

Add these to your backend `.env` file:

```bash
# Existing from Phase 2
DATABASE_URL=postgresql://...your-neon-connection-string...
JWT_SECRET=your-jwt-secret

# NEW for Phase 3
OPENAI_API_KEY=sk-your-openai-api-key
```

### Frontend Environment Variables

Add to your frontend `.env.local`:

```bash
# Existing from Phase 2
NEXT_PUBLIC_API_URL=http://localhost:8000

# No new frontend env vars needed for Phase 3
```

## Step 2: Install Dependencies

### Backend

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install new dependencies
pip install openai-agents-sdk mcp
```

### Frontend

```bash
cd frontend

# Install ChatKit and dependencies
npm install @openai/chatkit
```

## Step 3: Database Migration

Create the new tables for conversations and messages:

```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "Add conversation and message tables"

# Run migration
alembic upgrade head
```

Or run SQL directly:

```sql
-- Run in Neon console or via psql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conv_created ON messages(conversation_id, created_at);
```

## Step 4: Verify Setup

### Start Backend

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### Start Frontend

```bash
cd frontend
npm run dev
```

### Test Chat Endpoint

```bash
# Replace {user_id} and {token} with actual values
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me manage my tasks?"}'
```

Expected response:
```json
{
  "id": "uuid-here",
  "conversation_id": "uuid-here",
  "role": "assistant",
  "content": "Hello! I'd be happy to help you manage your tasks...",
  "created_at": "2025-12-16T..."
}
```

## Step 5: Test Core Flows

### Add Task via Chat

1. Open http://localhost:3000
2. Sign in with your account
3. Navigate to Chat page
4. Type: "Add a task to buy groceries"
5. Verify: AI confirms task creation, task appears in task list

### View Tasks via Chat

1. In chat, type: "Show me my tasks"
2. Verify: AI lists all your tasks with details

### Complete Task via Chat

1. In chat, type: "Mark task 1 as complete"
2. Verify: AI confirms completion, task status updated

### View Chat History

1. Refresh the page
2. Verify: Previous chat messages are still visible

## Verification Checklist

### Constitution Compliance

- [ ] **Stateless**: Server restart doesn't break chat (messages in DB)
- [ ] **Tool Determinism**: Invalid task ID returns error, not crash
- [ ] **Security Propagation**: Can't access other users' tasks via chat
- [ ] **Conversation Persistence**: Messages survive refresh
- [ ] **Atomic Operations**: Task changes commit immediately
- [ ] **User Experience**: Loading indicator shown during AI processing

### Functional Tests

- [ ] Add task via natural language
- [ ] List tasks (all, pending, completed)
- [ ] Complete task by ID or title
- [ ] Delete task by ID
- [ ] Update task title/description
- [ ] Chat history persists across sessions
- [ ] Error messages are user-friendly

### Security Tests

- [ ] Request without JWT returns 401
- [ ] Request with mismatched user_id returns 403
- [ ] Cannot access other users' tasks
- [ ] Cannot access other users' conversations

## Troubleshooting

### "OPENAI_API_KEY not set"

Ensure the API key is in your `.env` file and the backend is restarted.

### "AI service unavailable"

Check OpenAI API status and your API key validity.

### "Task not found" when it exists

Verify user_id isolation is working correctly. The task must belong to the current user.

### Messages not persisting

Check database connection and verify migrations ran successfully:
```sql
SELECT * FROM messages LIMIT 5;
```

### JWT validation failing

Ensure the JWT `sub` claim matches the `user_id` in the URL path.

## Next Steps

After verifying the quickstart:

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Implement features in priority order (P1 first)
3. Run tests after each user story
4. Validate constitution compliance at each checkpoint
