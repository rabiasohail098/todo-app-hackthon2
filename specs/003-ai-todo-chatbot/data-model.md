# Data Model: AI-Powered Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Created**: 2025-12-30
**Database**: Neon Serverless PostgreSQL
**ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic)

## Overview

This document defines the database schema for the AI-powered chatbot feature. The data model extends Phase 2 by adding conversation and message tracking while preserving the existing task schema.

**Design Principles**:
1. **User Isolation**: Every table has `user_id` for multi-tenant security
2. **Immutability**: Messages are append-only (no updates/deletes)
3. **Timestamps**: All entities track creation time for ordering and auditing
4. **Indexes**: Optimize queries on user_id and foreign keys

---

## Entity Relationship Diagram

```
┌─────────────────────┐
│       User          │  (Not stored - handled by Better Auth)
│  - user_id (str)    │
└──────────┬──────────┘
           │ 1
           │
           │ *
    ┌──────┴───────────────────┬───────────────────┐
    │                          │                   │
    ▼                          ▼                   ▼
┌──────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│   Conversation   │   │       Task       │   │    Message      │
│                  │   │                  │   │                 │
│  - id (PK)       │   │  - id (PK)       │   │  - id (PK)      │
│  - user_id       │   │  - user_id       │   │  - conv_id (FK) │
│  - created_at    │   │  - title         │   │  - role         │
│  - updated_at    │   │  - description   │   │  - content      │
└────────┬─────────┘   │  - completed     │   │  - created_at   │
         │ 1           │  - created_at    │   └─────────────────┘
         │             └──────────────────┘
         │ *
         │
         └──────────────────────┐
                                │
                    (Conversation has many Messages)
```

---

## Table 1: Task (Existing from Phase 2)

**Purpose**: Store user's todo tasks

**SQLModel Definition**:
```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**SQL Schema**:
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
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

**Constraints**:
- `user_id`: Required, indexed for fast user-specific queries
- `title`: Required, max 200 characters
- `completed`: Defaults to False
- `created_at`: Auto-set on creation

**Business Rules**:
- All queries MUST filter by user_id (user isolation)
- Title cannot be empty string
- Tasks are soft-deleted (future enhancement: add deleted_at column)

---

## Table 2: Conversation (New for Phase 3)

**Purpose**: Group chat messages into conversations

**SQLModel Definition**:
```python
from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**SQL Schema**:
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

**Constraints**:
- `user_id`: Required, indexed for fast user lookup
- `created_at`: Auto-set on creation
- `updated_at`: Auto-set on creation, manually updated when new message added

**Business Rules**:
- One user can have multiple conversations (future: conversation switcher UI)
- Currently: one active conversation per user (Phase 3 MVP)
- Conversations auto-deleted after 90 days (data retention policy)
- All queries MUST filter by user_id

---

## Table 3: Message (New for Phase 3)

**Purpose**: Store all chat messages (user and assistant)

**SQLModel Definition**:
```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

**SQL Schema**:
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

**Constraints**:
- `conversation_id`: Required, foreign key to conversations table
- `role`: Required, enum ("user" or "assistant")
- `content`: Required, no max length (can be long AI responses)
- `created_at`: Auto-set, used for ordering messages
- `ON DELETE CASCADE`: If conversation deleted, all messages deleted

**Business Rules**:
- Messages are immutable (append-only, no updates/deletes)
- User messages saved BEFORE AI processing
- Assistant messages saved AFTER AI response generated
- Messages ordered by created_at for conversation history
- Context window: fetch last 10 messages for AI agent

---

## Migrations (Alembic)

### Migration 1: Create conversations table

```bash
alembic revision --autogenerate -m "Add conversations table"
alembic upgrade head
```

### Migration 2: Create messages table

```bash
alembic revision --autogenerate -m "Add messages table"
alembic upgrade head
```

---

**Version**: 1.0.0 | **Created**: 2025-12-30 | **Status**: Ready for Implementation
