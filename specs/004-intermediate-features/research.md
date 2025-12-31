# Technology Research: Intermediate Features

**Feature**: 004-intermediate-features
**Date**: 2025-12-31
**Status**: Complete

## Purpose

This document records technology selection decisions for the intermediate features implementation. Each decision is based on evaluation criteria specific to our requirements.

---

## Research Task 1: Date Parsing Library Evaluation

### Question
Which Python library best handles natural language dates ("tomorrow", "next Friday", "next week")?

### Options Evaluated

1. **python-date util** (dateutil)
2. **parsedatetime**
3. **dateparser**

### Evaluation Criteria

- ✅ Accuracy in parsing common natural language phrases
- ✅ Support for relative dates (tomorrow, next week)
- ✅ Timezone handling
- ✅ Maintenance & community support
- ✅ Performance for real-time chat interactions
- ✅ Ease of integration with existing code

### Comparison

| Criteria | python-dateutil | parsedatetime | dateparser |
|----------|----------------|---------------|------------|
| Relative dates | ✅ Good | ✅ Excellent | ✅ Excellent |
| Timezone support | ✅ Excellent | ⚠️ Basic | ✅ Good |
| Maintenance | ✅ Active | ⚠️ Moderate | ✅ Active |
| Performance | ✅ Fast | ✅ Fast | ⚠️ Slower |
| Bundle size | ✅ Small | ✅ Small | ❌ Large (many dependencies) |
| Ease of use | ✅ Simple API | ✅ Simple API | ⚠️ Complex config |

### Decision: **python-dateutil**

**Rationale**:
- Already a de-facto standard in Python ecosystem (companion to stdlib datetime)
- Excellent timezone handling (critical for due dates)
- Lightweight with minimal dependencies
- Well-maintained with strong community support
- Fast performance for real-time chat responses
- Simple API: `parser.parse("tomorrow")` just works

**Alternatives Considered**:
- **parsedatetime**: Better at parsing informal dates ("next Tuesday"), but lacks robust timezone support
- **dateparser**: Most comprehensive but adds 20+ dependencies and slower performance (not worth the trade-off)

**Implementation Notes**:
```python
from dateutil import parser, tz
from datetime import datetime, timedelta

# Parse natural language dates
user_date = parser.parse("tomorrow at 5pm")

# Handle relative dates manually (simple helpers)
def parse_natural_date(text: str, user_timezone: str) -> datetime:
    text_lower = text.lower()

    # Relative shortcuts
    if "tomorrow" in text_lower:
        return datetime.now() + timedelta(days=1)
    if "next week" in text_lower:
        return datetime.now() + timedelta(weeks=1)
    if "next friday" in text_lower:
        # Calculate next Friday
        ...

    # Fallback to dateutil parser
    return parser.parse(text)
```

---

## Research Task 2: Chart Library Selection (Frontend)

### Question
Which React chart library best fits our statistics dashboard needs?

### Options Evaluated

1. **Recharts**
2. **Chart.js (react-chartjs-2)**
3. **Victory**
4. **Nivo**

### Evaluation Criteria

- ✅ TypeScript support (first-class)
- ✅ Bundle size (smaller is better)
- ✅ Ease of customization
- ✅ Documentation quality
- ✅ Responsive design
- ✅ Chart types needed: Bar, Pie, Line

### Comparison

| Criteria | Recharts | Chart.js | Victory | Nivo |
|----------|----------|----------|---------|------|
| TypeScript | ✅ Native | ⚠️ Wrapper | ✅ Native | ✅ Native |
| Bundle size | ✅ 95KB | ❌ 180KB | ⚠️ 120KB | ❌ 250KB |
| Customization | ✅ Excellent | ⚠️ Limited | ✅ Good | ✅ Excellent |
| Documentation | ✅ Great | ✅ Great | ⚠️ Moderate | ✅ Great |
| Responsive | ✅ Built-in | ✅ Built-in | ⚠️ Manual | ✅ Built-in |
| Learning curve | ✅ Easy | ✅ Easy | ⚠️ Moderate | ⚠️ Steep |

### Decision: **Recharts**

**Rationale**:
- TypeScript-first design (not a wrapper)
- Smallest bundle size (95KB gzipped)
- Composable API that matches React patterns
- Built on D3 but with simpler API
- Responsive by default
- Excellent documentation with many examples
- All chart types we need: BarChart, PieChart, LineChart

**Alternatives Considered**:
- **Chart.js**: Popular but larger bundle and TypeScript support is via wrapper
- **Victory**: Good but slightly heavier and more verbose API
- **Nivo**: Most feature-rich but overkill for our needs (250KB bundle)

**Implementation Example**:
```tsx
import { BarChart, Bar, PieChart, Pie, XAxis, YAxis, Tooltip } from 'recharts';

// Completion rate pie chart
<PieChart width={300} height={300}>
  <Pie data={completionData} dataKey="value" nameKey="name" />
  <Tooltip />
</PieChart>

// Tasks completed per day bar chart
<BarChart width={600} height={300} data={dailyData}>
  <XAxis dataKey="day" />
  <YAxis />
  <Bar dataKey="completed" fill="#8884d8" />
  <Tooltip />
</BarChart>
```

---

## Research Task 3: File Storage Provider Comparison

### Question
Should we use AWS S3 or Cloudinary for file attachments?

### Evaluation Criteria

- ✅ Free tier availability
- ✅ Image optimization features
- ✅ CDN included
- ✅ API simplicity
- ✅ Pricing beyond free tier
- ✅ Setup complexity

### Comparison

| Criteria | Cloudinary | AWS S3 |
|----------|-----------|--------|
| Free tier | ✅ 25GB storage, 25GB bandwidth | ⚠️ 5GB storage, 15GB bandwidth |
| Image optimization | ✅ Built-in (resize, format, quality) | ❌ Requires Lambda/processing |
| CDN | ✅ Included | ⚠️ Requires CloudFront setup |
| API simplicity | ✅ Simple REST API | ⚠️ Complex AWS SDK |
| Pricing (after free) | ✅ $89/month for 97GB | ⚠️ $23/month for 100GB (+ bandwidth) |
| Setup complexity | ✅ Single API key | ⚠️ IAM roles, buckets, policies |
| File types | ✅ Images, videos, docs | ✅ Any file type |

### Decision: **Cloudinary**

**Rationale**:
- Generous free tier (25GB vs 5GB) sufficient for MVP
- Image optimization built-in (automatic format conversion, compression)
- CDN included globally (no CloudFront setup needed)
- Simple API: 3 environment variables vs AWS's complex IAM setup
- Faster implementation time (1 hour vs 1 day for AWS)
- Perfect for our use case (mostly images and small documents)

**Alternatives Considered**:
- **AWS S3**: More powerful but overkill for MVP. Complex setup not worth it when Cloudinary solves our needs perfectly.

**Implementation Notes**:
```python
# Backend: cloudinary SDK
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Upload file
result = cloudinary.uploader.upload(
    file,
    folder=f"tasks/{task_id}",
    resource_type="auto"  # Auto-detect file type
)

# Delete file
cloudinary.uploader.destroy(public_id)
```

**Environment Variables Required**:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

---

## Research Task 4: Full-Text Search Best Practices

### Question
How to implement efficient PostgreSQL full-text search with tsvector?

### Implementation Strategy

**Decision**: Use PostgreSQL native full-text search with `tsvector` + GIN index

**Rationale**:
- No external dependencies (Elasticsearch, Algolia)
- Proven performance for up to 1M records
- Built into PostgreSQL (no additional service)
- Simple to implement and maintain
- Sub-100ms query time for typical workloads

### Implementation Guide

#### 1. Add Search Vector Column to Tasks Table

```sql
-- Add tsvector column
ALTER TABLE tasks ADD COLUMN search_vector tsvector;

-- Create GIN index for fast search
CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);

-- Create trigger to auto-update search vector
CREATE OR REPLACE FUNCTION tasks_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_search_vector_trigger
BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION tasks_search_vector_update();
```

#### 2. Query Syntax

```python
# Python/SQLModel query
from sqlalchemy import func

# Search tasks
query = session.query(Task).filter(
    Task.user_id == current_user_id,
    Task.search_vector.op('@@')(func.to_tsquery('english', search_term))
)

# Relevance ranking
query = query.order_by(
    func.ts_rank(Task.search_vector, func.to_tsquery('english', search_term)).desc()
)

# Fuzzy matching (similarity threshold)
query = session.query(Task).filter(
    Task.user_id == current_user_id,
    func.similarity(Task.title, search_term) > 0.3
)
```

#### 3. Weighting Strategy

- **Weight A**: Task title (highest priority)
- **Weight B**: Task description (secondary priority)
- **Weight C**: Tags (if needed later)
- **Weight D**: Notes (lowest priority)

#### 4. Performance Tuning

- **Pagination**: Always limit results (default 20, max 100)
- **Index maintenance**: `VACUUM ANALYZE tasks;` periodically
- **Query optimization**: Use `ts_rank_cd` for better relevance
- **Highlighting**: Use `ts_headline` to show matching snippets

```sql
-- Example with highlighting
SELECT
  id,
  title,
  ts_headline('english', description, to_tsquery('english', 'milk')) as snippet
FROM tasks
WHERE search_vector @@ to_tsquery('english', 'milk')
AND user_id = '...'
ORDER BY ts_rank(search_vector, to_tsquery('english', 'milk')) DESC
LIMIT 20;
```

---

## Research Task 5: Recurring Task Generation Strategy

### Question
Should we use a background job (APScheduler) or on-demand generation (when task completed)?

### Options Evaluated

1. **Background Job** (APScheduler): Cron-like scheduler runs hourly to generate next occurrences
2. **On-Demand**: When user completes a recurring task, immediately create next occurrence

### Comparison

| Criteria | Background Job | On-Demand |
|----------|---------------|-----------|
| Reliability | ✅ Always runs | ⚠️ Requires user action |
| Complexity | ⚠️ Requires scheduler | ✅ Simple |
| User experience | ✅ Tasks appear automatically | ⚠️ Tasks appear only after completion |
| Resource usage | ⚠️ Cron job overhead | ✅ No background process |
| Edge cases | ✅ Handles skipped tasks | ❌ Breaks if user never completes |
| Scalability | ⚠️ All users checked hourly | ✅ Only active users |

### Decision: **Background Job with APScheduler**

**Rationale**:
- Better user experience: Tasks appear automatically at midnight
- More reliable: Doesn't depend on user completing tasks
- Handles edge cases: What if user never completes a daily task?
- Industry standard: How Todoist, TickTick, etc. handle recurring tasks
- APScheduler is lightweight (not Celery-level complexity)

**Alternatives Considered**:
- **On-Demand**: Simpler but poor UX (daily tasks wouldn't appear until you complete previous one)

**Implementation Notes**:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

def generate_recurring_tasks():
    """Run every hour to check for recurring tasks due"""
    now = datetime.now()

    # Find tasks with recurrence and next_recurrence_date <= now
    recurring_tasks = session.query(Task).filter(
        Task.recurrence_pattern != None,
        Task.next_recurrence_date <= now
    ).all()

    for task in recurring_tasks:
        # Create next occurrence
        new_task = Task(
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            category_id=task.category_id,
            due_date=calculate_next_due_date(task.recurrence_pattern),
            recurrence_pattern=task.recurrence_pattern
        )
        session.add(new_task)

        # Update original task's next_recurrence_date
        task.next_recurrence_date = calculate_next_occurrence(task.recurrence_pattern)

    session.commit()

# Schedule job to run every hour
scheduler.add_job(generate_recurring_tasks, 'interval', hours=1)
scheduler.start()
```

**Recurrence Pattern Calculation**:
```python
def calculate_next_occurrence(pattern: RecurrencePattern) -> datetime:
    now = datetime.now()

    if pattern == RecurrencePattern.DAILY:
        return now + timedelta(days=1)
    elif pattern == RecurrencePattern.WEEKLY:
        return now + timedelta(weeks=1)
    elif pattern == RecurrencePattern.MONTHLY:
        return now + timedelta(days=30)  # Approximate, can be refined
```

---

## Research Task 6: Rich Text Editor Selection

### Question
Which markdown/rich text editor for task notes?

### Options Evaluated

1. **React-Markdown** (markdown renderer only)
2. **Tiptap** (WYSIWYG editor)
3. **Slate** (framework for editors)
4. **Draft.js** (Facebook's editor)

### Comparison

| Criteria | React-Markdown | Tiptap | Slate | Draft.js |
|----------|---------------|--------|-------|----------|
| Complexity | ✅ Simple | ⚠️ Moderate | ⚠️ Complex | ⚠️ Moderate |
| Bundle size | ✅ 25KB | ⚠️ 150KB | ⚠️ 180KB | ❌ 220KB |
| Markdown support | ✅ Native | ✅ Plugin | ⚠️ Custom | ❌ Requires plugin |
| Security | ✅ Safe | ✅ Safe | ⚠️ Manual | ⚠️ Manual |
| Maintenance | ✅ Active | ✅ Active | ⚠️ Slow | ❌ Archived |
| TypeScript | ✅ Full | ✅ Full | ⚠️ Partial | ⚠️ Partial |

### Decision: **React-Markdown**

**Rationale**:
- Task notes don't need WYSIWYG editing (markdown is sufficient)
- Smallest bundle size (25KB vs 150KB+)
- Secure by default (sanitizes HTML)
- Simple to implement (render only, no complex editor state)
- Users can type markdown in a simple `<textarea>`
- Matches developer-friendly workflow

**Alternatives Considered**:
- **Tiptap**: Excellent WYSIWYG but overkill for simple task notes
- **Slate/Draft.js**: Too complex for our needs

**Implementation Example**:
```tsx
import ReactMarkdown from 'react-markdown';
import { useState } from 'react';

function TaskNotes({ taskId }: { taskId: number }) {
  const [notes, setNotes] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  if (isEditing) {
    return (
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Add task notes (supports **markdown**)"
        className="w-full p-2 border rounded"
      />
    );
  }

  return (
    <div className="prose max-w-none">
      <ReactMarkdown>{notes}</ReactMarkdown>
    </div>
  );
}
```

**Supported Markdown**:
- **Bold**: `**text**`
- *Italic*: `*text*`
- Lists: `- item` or `1. item`
- Links: `[text](url)`
- Code: `` `code` ``
- Headers: `# H1`, `## H2`

---

## Summary of Decisions

| Technology Area | Decision | Key Reason |
|----------------|----------|------------|
| Date Parsing | python-dateutil | Lightweight, robust timezone support |
| Charts | Recharts | TypeScript-first, smallest bundle, composable |
| File Storage | Cloudinary | Generous free tier, image optimization built-in |
| Full-Text Search | PostgreSQL tsvector | Native, no external dependencies, proven |
| Recurring Tasks | APScheduler | Better UX, more reliable than on-demand |
| Rich Text Editor | React-Markdown | Simple, secure, sufficient for task notes |

**Total Additional Dependencies**:
- Backend: `python-dateutil`, `APScheduler`, `cloudinary`
- Frontend: `recharts`, `react-markdown`

**Estimated Bundle Size Impact**: +120KB (frontend), +5MB (backend)

---

**Research Status**: ✅ **COMPLETE**
**Next Phase**: Phase 1 - Create API contracts and quickstart guide
