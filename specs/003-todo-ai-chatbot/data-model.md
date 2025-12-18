# Data Model: Todo AI Chatbot

**Feature**: 003-todo-ai-chatbot
**Date**: 2025-12-16
**Status**: Complete

## Overview

This document defines the data models for the AI chatbot feature, extending the existing Phase 2 schema with conversation and message entities.

## Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    User      │       │   Conversation   │       │   Message    │
│  (Phase 2)   │       │     (NEW)        │       │    (NEW)     │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id (PK)      │──┐    │ id (PK)          │──┐    │ id (PK)      │
│ email        │  │    │ user_id (FK) ────┼──┘    │ conv_id (FK)─┼──┐
│ password     │  │    │ created_at       │       │ role         │  │
│ created_at   │  │    └──────────────────┘       │ content      │  │
└──────────────┘  │                               │ created_at   │  │
                  │    ┌──────────────────┐       └──────────────┘  │
                  │    │      Task        │                         │
                  │    │    (Phase 2)     │       ┌─────────────────┘
                  │    ├──────────────────┤       │
                  └───▶│ id (PK)          │       │
                       │ user_id (FK) ────┼───────┘
                       │ title            │
                       │ description      │
                       │ is_completed     │
                       │ created_at       │
                       └──────────────────┘
```

## Entities

### Conversation (NEW)

Represents a chat session between a user and the AI assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, Auto-generated | Unique conversation identifier |
| user_id | String | FK to users.id, Indexed, NOT NULL | Owner of the conversation |
| created_at | Timestamp | Auto-generated, NOT NULL | When conversation was started |

**Relationships:**
- Belongs to one User (many-to-one)
- Has many Messages (one-to-many)

**Indexes:**
- `idx_conversations_user_id` on `user_id` (query by user)
- `idx_conversations_created_at` on `created_at` (sort by date)

### Message (NEW)

Represents a single message in a conversation (user or assistant).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, Auto-generated | Unique message identifier |
| conversation_id | UUID | FK to conversations.id, Indexed, NOT NULL | Parent conversation |
| role | Enum | 'user' \| 'assistant', NOT NULL | Message sender role |
| content | Text | NOT NULL | Message content |
| created_at | Timestamp | Auto-generated, NOT NULL | When message was created |

**Relationships:**
- Belongs to one Conversation (many-to-one)

**Indexes:**
- `idx_messages_conversation_id` on `conversation_id` (fetch by conversation)
- `idx_messages_created_at` on `created_at` (chronological ordering)
- Composite: `idx_messages_conv_created` on `(conversation_id, created_at)` (efficient history fetch)

### Task (Existing - Phase 2)

No changes to existing Task model. MCP tools interact via SQLModel.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique task identifier |
| user_id | String | FK to users.id, Indexed, NOT NULL | Task owner |
| title | String(200) | NOT NULL | Task title |
| description | Text | Nullable | Task description |
| is_completed | Boolean | Default: false | Completion status |
| created_at | Timestamp | Auto-generated | Creation timestamp |

## Database Schema (SQL)

```sql
-- Conversation table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- Message table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conv_created ON messages(conversation_id, created_at);
```

## SQLModel Definitions

### Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

### Message Model

```python
from enum import Enum

class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

## Validation Rules

### Conversation
- `user_id` must be a valid user ID from the users table
- `user_id` must match the JWT `sub` claim of the requesting user

### Message
- `conversation_id` must be a valid conversation ID
- `role` must be exactly 'user' or 'assistant'
- `content` must not be empty
- `content` maximum length: 10,000 characters (optional limit)

## Query Patterns

### Get User's Active Conversation

```sql
SELECT * FROM conversations
WHERE user_id = :user_id
ORDER BY created_at DESC
LIMIT 1;
```

### Get Last N Messages (Context Window)

```sql
SELECT * FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at DESC
LIMIT :n;
-- Then reverse in application for chronological order
```

### Get Chat History for Display (Last 50)

```sql
SELECT * FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at ASC
LIMIT 50;
```

## State Transitions

### Conversation States
- **Created**: New conversation started
- **Active**: Has messages, ongoing
- **Archived**: (Future) User archives conversation

### Message States
- Messages are immutable after creation
- No edit or delete operations on messages

## Data Integrity Rules

1. **User Isolation**: All queries must include `WHERE user_id = :current_user`
2. **Cascading Deletes**: Deleting a conversation deletes all its messages
3. **Timestamp Ordering**: Messages ordered by `created_at` for context
4. **Atomic Saves**: User message saved before AI processing, AI response saved after
