# Data Model: Intermediate Features

**Feature**: 004-intermediate-features
**Database**: PostgreSQL (Neon)
**ORM**: SQLModel
**Created**: 2025-12-31

---

## Overview

This document defines the database schema for intermediate features including categories, priorities, due dates, tags, subtasks, and activity logging.

---

## Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Category   │───┐   │     Task     │───┐   │   Subtask    │
│              │   │   │              │   │   │              │
│ id           │   └──<│ category_id  │   └──<│parent_task_id│
│ user_id      │       │ user_id      │       │ title        │
│ name         │       │ title        │       │ is_completed │
│ color        │       │ priority     │       │ order        │
│ icon         │       │ due_date     │       └──────────────┘
└──────────────┘       │ recurrence   │
                       └──────────────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
          ┌──────▼─────┐ ┌───▼────────┐ ┌▼──────────────┐
          │  TaskTag   │ │TaskActivity│ │  Attachment   │
          │            │ │            │ │               │
          │ task_id    │ │ task_id    │ │ task_id       │
          │ tag_id     │ │ action     │ │ filename      │
          └────────────┘ │ field      │ │ file_path     │
                 │       │ old_value  │ │ file_size     │
                 │       │ new_value  │ └───────────────┘
                 │       └────────────┘
          ┌──────▼─────┐
          │    Tag     │
          │            │
          │ id         │
          │ user_id    │
          │ name       │
          └────────────┘
```

---

## Models

### 1. Category Model

**Purpose**: Organize tasks into user-defined categories (Work, Personal, etc.)

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)  # UUID string
    name: str = Field(max_length=50, nullable=False)
    color: str = Field(max_length=7, default="#8B5CF6")  # Hex color
    icon: Optional[str] = Field(max_length=10, default="📁")  # Emoji
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="category")
```

**Constraints**:
- `UNIQUE(user_id, name)` - No duplicate category names per user
- `CHECK(LENGTH(name) >= 1)` - Name cannot be empty
- `CHECK(color LIKE '#%')` - Color must be hex format

**Indexes**:
```sql
CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE UNIQUE INDEX idx_categories_user_name ON categories(user_id, name);
```

---

### 2. Tag Model

**Purpose**: Flexible labeling system for tasks (multiple tags per task)

```python
class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    name: str = Field(max_length=30, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (many-to-many via TaskTag)
    tasks: List["Task"] = Relationship(
        back_populates="tags",
        link_model="TaskTag"
    )
```

**Constraints**:
- `UNIQUE(user_id, name)` - No duplicate tags per user
- `CHECK(name NOT LIKE '% %')` - No spaces in tag names

**Indexes**:
```sql
CREATE INDEX idx_tags_user_id ON tags(user_id);
CREATE UNIQUE INDEX idx_tags_user_name ON tags(user_id, LOWER(name));
```

---

### 3. Task Model (Updated)

**Purpose**: Enhanced task with priority, due date, category, and recurrence

```python
from enum import Enum

class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"  # For cron-like patterns

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Existing fields
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # NEW fields for Phase 4
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[datetime] = Field(default=None, index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")

    # Recurring task fields
    recurrence_pattern: Optional[RecurrencePattern] = Field(default=None)
    recurrence_interval: Optional[int] = Field(default=1)  # Every N days/weeks
    next_recurrence_date: Optional[datetime] = Field(default=None)
    parent_recurrence_id: Optional[int] = Field(default=None)  # Original recurring task

    # Relationships
    category: Optional[Category] = Relationship(back_populates="tasks")
    subtasks: List["Subtask"] = Relationship(back_populates="parent_task")
    tags: List[Tag] = Relationship(
        back_populates="tasks",
        link_model="TaskTag"
    )
    activities: List["TaskActivity"] = Relationship(back_populates="task")
    attachments: List["Attachment"] = Relationship(back_populates="task")
```

**Migration**:
```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP NULL;
ALTER TABLE tasks ADD COLUMN category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL;
ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(50) NULL;
ALTER TABLE tasks ADD COLUMN recurrence_interval INTEGER DEFAULT 1;
ALTER TABLE tasks ADD COLUMN next_recurrence_date TIMESTAMP NULL;
ALTER TABLE tasks ADD COLUMN parent_recurrence_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL;

CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_category_id ON tasks(category_id);
```

---

### 4. Subtask Model

**Purpose**: Break down tasks into smaller actionable items

```python
class Subtask(SQLModel, table=True):
    __tablename__ = "subtasks"

    id: int = Field(default=None, primary_key=True)
    parent_task_id: int = Field(foreign_key="tasks.id", nullable=False)
    title: str = Field(max_length=200, nullable=False)
    is_completed: bool = Field(default=False)
    order: int = Field(default=0)  # For custom ordering
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    parent_task: Task = Relationship(back_populates="subtasks")
```

**Constraints**:
- `CHECK(LENGTH(title) >= 1)`
- Cascade delete: When parent task deleted, subtasks deleted

**Indexes**:
```sql
CREATE INDEX idx_subtasks_parent_task ON subtasks(parent_task_id);
CREATE INDEX idx_subtasks_order ON subtasks(parent_task_id, "order");
```

---

### 5. TaskTag Model (Join Table)

**Purpose**: Many-to-many relationship between tasks and tags

```python
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Constraints**:
- Cascade delete: When task or tag deleted, association removed

**Indexes**:
```sql
CREATE INDEX idx_task_tags_task ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag ON task_tags(tag_id);
```

---

### 6. TaskActivity Model

**Purpose**: Audit log for task changes

```python
class TaskActivity(SQLModel, table=True):
    __tablename__ = "task_activities"

    id: int = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", nullable=False)
    user_id: str = Field(nullable=False)
    action: str = Field(max_length=50, nullable=False)  # created, updated, completed
    field: Optional[str] = Field(max_length=50)  # title, priority, due_date
    old_value: Optional[str] = Field(max_length=500)
    new_value: Optional[str] = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    task: Task = Relationship(back_populates="activities")
```

**Actions**:
- `created` - Task created
- `updated` - Field changed
- `completed` - Marked as complete
- `uncompleted` - Unmarked
- `deleted` - Task deleted (soft delete log)

**Indexes**:
```sql
CREATE INDEX idx_task_activities_task ON task_activities(task_id);
CREATE INDEX idx_task_activities_created ON task_activities(created_at DESC);
```

---

### 7. Attachment Model

**Purpose**: Store file metadata for task attachments

```python
class Attachment(SQLModel, table=True):
    __tablename__ = "attachments"

    id: int = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", nullable=False)
    user_id: str = Field(nullable=False)
    filename: str = Field(max_length=255, nullable=False)
    file_path: str = Field(max_length=500, nullable=False)  # S3/Cloudinary URL
    file_size: int = Field(nullable=False)  # Bytes
    mime_type: str = Field(max_length=100, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Task = Relationship(back_populates="attachments")
```

**Constraints**:
- `CHECK(file_size <= 10485760)` - Max 10MB
- Allowed mime types: images, PDFs, documents

**Indexes**:
```sql
CREATE INDEX idx_attachments_task ON attachments(task_id);
```

---

## Pydantic Models (API)

### Request Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(default="#8B5CF6", pattern="^#[0-9A-Fa-f]{6}$")
    icon: str = Field(default="📁", max_length=10)

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=10)

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = Field(default="medium")
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None

class SubtaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    order: int = Field(default=0)

class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30, pattern="^[a-zA-Z0-9_-]+$")

class RecurrenceCreate(BaseModel):
    pattern: str  # daily, weekly, monthly
    interval: int = Field(default=1, ge=1)
```

---

## Sample Data

### Categories

```sql
INSERT INTO categories (user_id, name, color, icon) VALUES
('user-uuid-123', 'Work', '#8B5CF6', '💼'),
('user-uuid-123', 'Personal', '#EC4899', '🏠'),
('user-uuid-123', 'Shopping', '#10B981', '🛒'),
('user-uuid-123', 'Fitness', '#F59E0B', '🏋️');
```

### Tasks with New Fields

```sql
INSERT INTO tasks (user_id, title, priority, due_date, category_id, is_completed) VALUES
('user-uuid-123', 'Deploy app to production', 'critical', '2025-12-31 17:00:00', 1, false),
('user-uuid-123', 'Review pull requests', 'high', '2026-01-02 12:00:00', 1, false),
('user-uuid-123', 'Buy groceries', 'medium', '2026-01-01 18:00:00', 3, false),
('user-uuid-123', 'Morning workout', 'low', NULL, 4, true);
```

### Tags

```sql
INSERT INTO tags (user_id, name) VALUES
('user-uuid-123', 'urgent'),
('user-uuid-123', 'meeting'),
('user-uuid-123', 'bugs'),
('user-uuid-123', 'review');
```

### Task-Tag Associations

```sql
INSERT INTO task_tags (task_id, tag_id) VALUES
(1, 1),  -- Deploy app tagged as 'urgent'
(2, 3),  -- Review PRs tagged as 'bugs'
(2, 4);  -- Review PRs tagged as 'review'
```

### Subtasks

```sql
INSERT INTO subtasks (parent_task_id, title, is_completed, "order") VALUES
(3, 'Milk', false, 1),
(3, 'Bread', false, 2),
(3, 'Eggs', true, 3);
```

---

## Queries

### Get Tasks with Filters

```sql
-- Tasks with category, priority, and due date filters
SELECT
    t.*,
    c.name as category_name,
    c.color as category_color,
    ARRAY_AGG(tg.name) as tags
FROM tasks t
LEFT JOIN categories c ON t.category_id = c.id
LEFT JOIN task_tags tt ON t.id = tt.task_id
LEFT JOIN tags tg ON tt.tag_id = tg.id
WHERE t.user_id = $1
  AND ($2::INTEGER IS NULL OR t.category_id = $2)
  AND ($3::VARCHAR IS NULL OR t.priority = $3)
  AND (
    $4::VARCHAR IS NULL
    OR ($4 = 'today' AND DATE(t.due_date) = CURRENT_DATE)
    OR ($4 = 'week' AND t.due_date <= CURRENT_DATE + INTERVAL '7 days')
    OR ($4 = 'overdue' AND t.due_date < CURRENT_TIMESTAMP AND NOT t.is_completed)
  )
GROUP BY t.id, c.id
ORDER BY
    CASE t.priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    t.due_date NULLS LAST;
```

### Search Tasks (Full-Text)

```sql
-- Add tsvector column for search
ALTER TABLE tasks ADD COLUMN search_vector tsvector;

CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);

-- Update search vector on insert/update
CREATE OR REPLACE FUNCTION tasks_search_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_search_vector_update
BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION tasks_search_update();

-- Search query
SELECT * FROM tasks
WHERE user_id = $1
  AND search_vector @@ plainto_tsquery('english', $2)
ORDER BY ts_rank(search_vector, plainto_tsquery('english', $2)) DESC;
```

### Get Statistics

```sql
-- User productivity statistics
SELECT
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE is_completed) as completed_tasks,
    ROUND(COUNT(*) FILTER (WHERE is_completed)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 2) as completion_rate,
    COUNT(*) FILTER (WHERE is_completed AND DATE(updated_at) >= CURRENT_DATE - INTERVAL '7 days') as completed_this_week,
    COUNT(*) FILTER (WHERE due_date < CURRENT_TIMESTAMP AND NOT is_completed) as overdue_tasks
FROM tasks
WHERE user_id = $1;
```

---

## Migration Strategy

### Step 1: Add New Tables
```bash
alembic revision --autogenerate -m "Add intermediate features tables"
alembic upgrade head
```

### Step 2: Update Existing Tables
```sql
-- Non-breaking changes (defaults provided)
ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP NULL;
-- etc.
```

### Step 3: Backfill Data (if needed)
```sql
-- Set default categories for existing tasks (optional)
UPDATE tasks SET category_id = NULL WHERE category_id IS NULL;
```

---

**Version**: 1.0.0
**Created**: 2025-12-31
**Status**: Ready for Implementation
