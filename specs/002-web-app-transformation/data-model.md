# Data Model: Web Application Transformation

**Feature**: 002-web-app-transformation
**Date**: 2025-12-10

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│              User                   │
│  (Managed by Better Auth)           │
├─────────────────────────────────────┤
│  id: UUID (PK)                      │
│  email: VARCHAR(255) UNIQUE         │
│  password_hash: VARCHAR(255)        │
│  created_at: TIMESTAMP              │
│  updated_at: TIMESTAMP              │
└─────────────────────────────────────┘
                │
                │ 1:N
                ▼
┌─────────────────────────────────────┐
│              Task                   │
├─────────────────────────────────────┤
│  id: SERIAL (PK)                    │
│  user_id: UUID (FK → User.id) [IDX] │
│  title: VARCHAR(200) NOT NULL       │
│  description: TEXT NULL             │
│  is_completed: BOOLEAN DEFAULT FALSE│
│  created_at: TIMESTAMP DEFAULT NOW  │
└─────────────────────────────────────┘
```

## Entities

### User (Managed by Better Auth)

Better Auth manages the User entity with its own schema. We reference it via `user_id` foreign key.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt-hashed password |
| created_at | TIMESTAMP | DEFAULT NOW | Account creation time |
| updated_at | TIMESTAMP | DEFAULT NOW | Last profile update |

**Notes**:
- Better Auth handles password hashing and validation
- Additional fields may be added by Better Auth (name, image, etc.)
- We only interact with `id` for foreign key relationships

### Task

The core entity for todo items, isolated per user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | SERIAL | PK | Auto-incrementing task ID |
| user_id | UUID | FK(User.id), INDEX, NOT NULL | Owner of the task |
| title | VARCHAR(200) | NOT NULL | Task title (max 200 chars) |
| description | TEXT | NULL | Optional task description |
| is_completed | BOOLEAN | DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | DEFAULT NOW | Task creation time |

**Indexes**:
- `idx_tasks_user_id` on `user_id` - Primary query filter
- `idx_tasks_created_at` on `created_at DESC` - Ordering support

## SQLModel Definitions

### Task Model (Python)

```python
from datetime import datetime
from sqlmodel import SQLModel, Field
from uuid import UUID

class TaskBase(SQLModel):
    """Base model for Task - shared fields for create/update."""
    title: str = Field(max_length=200)
    description: str | None = None
    is_completed: bool = False

class Task(TaskBase, table=True):
    """Database model for Task entity."""
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    """Schema for creating a task (user_id assigned by server)."""
    pass

class TaskUpdate(SQLModel):
    """Schema for updating a task (all fields optional)."""
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    is_completed: bool | None = None

class TaskRead(TaskBase):
    """Schema for reading a task (includes server-assigned fields)."""
    id: int
    user_id: UUID
    created_at: datetime
```

## TypeScript Interfaces (Frontend)

```typescript
// frontend/src/types/index.ts

/**
 * Task entity matching backend Pydantic model.
 */
export interface Task {
  id: number;
  user_id: string;  // UUID as string
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;  // ISO 8601 timestamp
}

/**
 * Payload for creating a new task.
 * user_id is assigned by backend from JWT.
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
}

/**
 * Payload for updating an existing task.
 * All fields optional (PATCH semantics).
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  is_completed?: boolean;
}

/**
 * User entity (minimal, from Better Auth).
 */
export interface User {
  id: string;  // UUID
  email: string;
}
```

## Validation Rules

### Task.title
- Required (non-empty)
- Maximum 200 characters
- No leading/trailing whitespace (trimmed on save)

### Task.description
- Optional (nullable)
- No maximum length (TEXT type)
- Empty string treated as null

### Task.is_completed
- Required (defaults to false)
- Boolean only

### Task.user_id
- Required (assigned from JWT, never from client)
- Must reference valid User.id
- Immutable after creation

## State Transitions

```
Task Lifecycle:

[Created] ──────────────────────────────────────────┐
    │                                               │
    │ POST /api/tasks                               │
    ▼                                               │
┌─────────┐                                         │
│ Pending │ ◄───────────────────────────────────────┤
│is_completed: false│                               │
└─────────┘                                         │
    │                                               │
    │ PATCH /api/tasks/{id} {is_completed: true}    │
    ▼                                               │
┌───────────┐                                       │
│ Completed │                                       │
│is_completed: true │                               │
└───────────┘                                       │
    │                                               │
    │ PATCH /api/tasks/{id} {is_completed: false}   │
    └───────────────────────────────────────────────┘

    │ DELETE /api/tasks/{id}
    ▼
[Deleted] (permanent, no soft delete)
```

## Database Migrations

### Initial Migration (Alembic)

```python
# backend/src/db/migrations/versions/001_create_tasks_table.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'], postgresql_using='btree')

def downgrade():
    op.drop_index('idx_tasks_created_at', table_name='tasks')
    op.drop_index('idx_tasks_user_id', table_name='tasks')
    op.drop_table('tasks')
```

## Query Patterns

### Get User's Tasks (Newest First)

```python
from sqlmodel import select

def get_tasks_for_user(session: Session, user_id: UUID) -> list[Task]:
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    )
    return session.exec(statement).all()
```

### Create Task with User Isolation

```python
def create_task(session: Session, user_id: UUID, task_create: TaskCreate) -> Task:
    task = Task(
        user_id=user_id,  # From JWT, not client
        title=task_create.title.strip(),
        description=task_create.description,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Update Task (with Ownership Check)

```python
def update_task(
    session: Session,
    user_id: UUID,
    task_id: int,
    task_update: TaskUpdate
) -> Task | None:
    statement = (
        select(Task)
        .where(Task.id == task_id)
        .where(Task.user_id == user_id)  # Golden Rule
    )
    task = session.exec(statement).first()
    if not task:
        return None

    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Delete Task (with Ownership Check)

```python
def delete_task(session: Session, user_id: UUID, task_id: int) -> bool:
    statement = (
        select(Task)
        .where(Task.id == task_id)
        .where(Task.user_id == user_id)  # Golden Rule
    )
    task = session.exec(statement).first()
    if not task:
        return False

    session.delete(task)
    session.commit()
    return True
```
