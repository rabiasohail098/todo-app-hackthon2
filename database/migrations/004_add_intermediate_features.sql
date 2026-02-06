-- Migration: 004 - Add Intermediate Features
-- Date: 2025-12-31
-- Description: Add categories, tags, subtasks, priorities, due dates, recurring tasks, attachments, and activity log

-- =============================================================================
-- 1. CREATE CATEGORIES TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#8B5CF6',
    icon VARCHAR(10) DEFAULT '📁',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT categories_name_not_empty CHECK (LENGTH(name) >= 1),
    CONSTRAINT categories_color_hex CHECK (color ~ '^#[0-9A-Fa-f]{6}$')
);

-- Indexes for categories
CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_user_name ON categories(user_id, name);

-- =============================================================================
-- 2. CREATE TAGS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT tags_no_spaces CHECK (name NOT LIKE '% %')
);

-- Indexes for tags
CREATE INDEX IF NOT EXISTS idx_tags_user_id ON tags(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_tags_user_name ON tags(user_id, LOWER(name));

-- =============================================================================
-- 3. CREATE TASK_TAGS JOIN TABLE (Many-to-Many)
-- =============================================================================
CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (task_id, tag_id)
);

-- Indexes for task_tags
CREATE INDEX IF NOT EXISTS idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX IF NOT EXISTS idx_task_tags_tag_id ON task_tags(tag_id);

-- =============================================================================
-- 4. CREATE SUBTASKS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS subtasks (
    id SERIAL PRIMARY KEY,
    parent_task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for subtasks
CREATE INDEX IF NOT EXISTS idx_subtasks_parent_task_id ON subtasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_subtasks_order ON subtasks(parent_task_id, "order");

-- =============================================================================
-- 5. CREATE TASK_ACTIVITIES TABLE (Activity Log)
-- =============================================================================
CREATE TABLE IF NOT EXISTS task_activities (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    field VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraint for action types
    CONSTRAINT task_activities_action_check CHECK (
        action IN ('created', 'updated', 'completed', 'deleted', 'priority_changed',
                   'category_changed', 'due_date_set', 'tag_added', 'tag_removed',
                   'subtask_added', 'subtask_completed', 'attachment_added')
    )
);

-- Indexes for task_activities
CREATE INDEX IF NOT EXISTS idx_task_activities_task_id ON task_activities(task_id);
CREATE INDEX IF NOT EXISTS idx_task_activities_user_id ON task_activities(user_id);
CREATE INDEX IF NOT EXISTS idx_task_activities_created_at ON task_activities(created_at DESC);

-- =============================================================================
-- 6. CREATE ATTACHMENTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS attachments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraint for file size (10MB max)
    CONSTRAINT attachments_file_size_check CHECK (file_size <= 10485760)
);

-- Indexes for attachments
CREATE INDEX IF NOT EXISTS idx_attachments_task_id ON attachments(task_id);

-- =============================================================================
-- 7. ALTER TASKS TABLE - ADD NEW COLUMNS
-- =============================================================================

-- Add priority column
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium';

-- Add due_date column
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS due_date TIMESTAMP NULL;

-- Add category_id column
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS category_id INTEGER NULL REFERENCES categories(id) ON DELETE SET NULL;

-- Add recurrence columns
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(50) NULL;

ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS recurrence_interval INTEGER DEFAULT 1;

ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS next_recurrence_date TIMESTAMP NULL;

ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS parent_recurrence_id INTEGER NULL REFERENCES tasks(id) ON DELETE SET NULL;

-- Add notes column for markdown notes
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS notes TEXT NULL;

-- Add search_vector column for full-text search
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS search_vector TSVECTOR;

-- Add constraint for priority values (using DO block for idempotency)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'tasks_priority_check'
    ) THEN
        ALTER TABLE tasks
        ADD CONSTRAINT tasks_priority_check
        CHECK (priority IN ('critical', 'high', 'medium', 'low'));
    END IF;
END $$;

-- Add constraint for recurrence pattern (using DO block for idempotency)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'tasks_recurrence_check'
    ) THEN
        ALTER TABLE tasks
        ADD CONSTRAINT tasks_recurrence_check
        CHECK (recurrence_pattern IS NULL OR recurrence_pattern IN ('daily', 'weekly', 'monthly', 'custom'));
    END IF;
END $$;

-- =============================================================================
-- 8. CREATE INDEXES ON TASKS TABLE
-- =============================================================================

-- Index for priority filtering
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);

-- Index for due_date filtering and sorting
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);

-- Index for category filtering
CREATE INDEX IF NOT EXISTS idx_tasks_category_id ON tasks(category_id);

-- Index for recurring tasks
CREATE INDEX IF NOT EXISTS idx_tasks_recurrence ON tasks(recurrence_pattern, next_recurrence_date)
WHERE recurrence_pattern IS NOT NULL;

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_tasks_user_priority_due ON tasks(user_id, priority, due_date);

-- Composite index for overdue tasks
CREATE INDEX IF NOT EXISTS idx_tasks_user_overdue ON tasks(user_id, due_date, is_completed)
WHERE due_date IS NOT NULL AND is_completed = FALSE;

-- =============================================================================
-- 9. FULL-TEXT SEARCH SETUP
-- =============================================================================

-- GIN index for full-text search
CREATE INDEX IF NOT EXISTS idx_tasks_search ON tasks USING GIN(search_vector);

-- Function to update search_vector automatically
CREATE OR REPLACE FUNCTION tasks_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(NEW.notes, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- Trigger to auto-update search_vector on INSERT/UPDATE
DROP TRIGGER IF EXISTS tasks_search_vector_trigger ON tasks;
CREATE TRIGGER tasks_search_vector_trigger
BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION tasks_search_vector_update();

-- =============================================================================
-- 10. INITIALIZE SEARCH VECTORS FOR EXISTING TASKS
-- =============================================================================

-- Update search_vector for all existing tasks
UPDATE tasks
SET search_vector =
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(notes, '')), 'C')
WHERE search_vector IS NULL;

-- =============================================================================
-- 11. CREATE UPDATE TIMESTAMP TRIGGERS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for categories
DROP TRIGGER IF EXISTS update_categories_updated_at ON categories;
CREATE TRIGGER update_categories_updated_at
BEFORE UPDATE ON categories
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for subtasks
DROP TRIGGER IF EXISTS update_subtasks_updated_at ON subtasks;
CREATE TRIGGER update_subtasks_updated_at
BEFORE UPDATE ON subtasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 12. ANALYZE TABLES FOR QUERY OPTIMIZATION
-- =============================================================================

ANALYZE tasks;
ANALYZE categories;
ANALYZE tags;
ANALYZE task_tags;
ANALYZE subtasks;
ANALYZE task_activities;
ANALYZE attachments;

-- =============================================================================
-- Migration Complete
-- =============================================================================

-- Summary:
-- ✅ Created 6 new tables: categories, tags, task_tags, subtasks, task_activities, attachments
-- ✅ Added 9 new columns to tasks table: priority, due_date, category_id, recurrence fields, notes, search_vector
-- ✅ Created 15+ indexes for optimal query performance
-- ✅ Set up full-text search with tsvector and GIN index
-- ✅ Created triggers for auto-updating timestamps and search vectors
-- ✅ Added constraints for data integrity
