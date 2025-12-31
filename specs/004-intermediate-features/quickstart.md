# Quickstart Guide: Intermediate Features

**Feature**: 004-intermediate-features
**Date**: 2025-12-31
**Prerequisites**: Phase 1-3 (Basic CRUD, AI Chatbot) must be complete

## Overview

This guide walks you through setting up the intermediate features for the todo app, including categories, priorities, due dates, search, subtasks, tags, recurring tasks, statistics, attachments, and activity log.

---

## 1. Install Dependencies

### Backend

```bash
cd backend

# Install new Python packages
pip install python-dateutil  # Natural language date parsing
pip install APScheduler      # Recurring task generation
pip install cloudinary        # File storage

# Update requirements.txt
pip freeze > requirements.txt
```

### Frontend

```bash
cd frontend

# Install new NPM packages
npm install recharts          # Charts for statistics dashboard
npm install react-markdown    # Markdown renderer for task notes

# Save dependencies
npm install
```

---

## 2. Configure Environment Variables

Add the following to your `.env` file:

### Backend `.env`

```env
# Existing variables (keep these)
DATABASE_URL=postgresql://...
JWT_SECRET=...
OPENAI_API_KEY=sk-or-v1-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=meta-llama/llama-3.3-70b-instruct:free

# NEW: Cloudinary configuration (for file attachments)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Get Cloudinary Credentials

1. Go to [cloudinary.com](https://cloudinary.com/) and sign up for free
2. Navigate to Dashboard
3. Copy your:
   - Cloud Name
   - API Key
   - API Secret
4. Paste into `.env` file

**Free Tier**: 25GB storage, 25GB bandwidth/month (plenty for MVP)

---

## 3. Database Migration

Run the database migration to add new tables and columns:

```bash
cd backend

# Run migration script
python scripts/migrate_004_intermediate_features.py

# Or manually run SQL migration
psql $DATABASE_URL -f database/migrations/004_add_intermediate_features.sql
```

### Migration Details

The migration script will:
- ✅ Add 5 new tables: `categories`, `tags`, `task_tags`, `subtasks`, `task_activities`, `attachments`
- ✅ Add 4 new columns to `tasks` table: `priority`, `due_date`, `category_id`, `recurrence_pattern`, `next_recurrence_date`
- ✅ Create indexes for performance: `priority`, `due_date`, `category_id`, `search_vector`
- ✅ Create GIN index for full-text search
- ✅ Create triggers for auto-updating search vectors

**Estimated Time**: 30 seconds

---

## 4. Start the Backend with Recurring Task Scheduler

The backend now includes a background job that generates recurring tasks every hour.

```bash
cd backend

# Start the server (APScheduler starts automatically)
python src/main.py

# OR with uvicorn
uvicorn src.main:app --reload
```

### Verify Scheduler is Running

Check logs for:
```
INFO:     APScheduler started
INFO:     Added job "generate_recurring_tasks" to job store "default"
```

---

## 5. Test New Features

### 5.1 Test Categories

```bash
# Create a category
curl -X POST http://localhost:8000/api/categories \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"name": "Work", "color": "#3B82F6", "icon": "💼"}'

# List categories
curl http://localhost:8000/api/categories \
  -H "Authorization: Bearer YOUR_JWT"
```

### 5.2 Test Priority & Due Dates

```bash
# Create task with priority and due date
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deploy app",
    "priority": "high",
    "due_date": "2025-12-31T17:00:00Z",
    "category_id": 1
  }'
```

### 5.3 Test Search

```bash
# Search tasks
curl "http://localhost:8000/api/tasks/search?q=deploy&priority=high" \
  -H "Authorization: Bearer YOUR_JWT"
```

### 5.4 Test Subtasks

```bash
# Add subtask to task 1
curl -X POST http://localhost:8000/api/tasks/1/subtasks \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"title": "Write tests", "order": 1}'

# Mark subtask complete
curl -X PUT http://localhost:8000/api/tasks/1/subtasks/1/complete \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"is_completed": true}'
```

### 5.5 Test Tags

```bash
# Add tag to task
curl -X POST http://localhost:8000/api/tasks/1/tags \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"name": "urgent"}'

# List all tags
curl http://localhost:8000/api/tags \
  -H "Authorization: Bearer YOUR_JWT"
```

### 5.6 Test File Attachments

```bash
# Upload file
curl -X POST http://localhost:8000/api/tasks/1/attachments \
  -H "Authorization: Bearer YOUR_JWT" \
  -F "file=@/path/to/file.pdf"

# Download file
curl http://localhost:8000/api/tasks/1/attachments/1 \
  -H "Authorization: Bearer YOUR_JWT" \
  --output downloaded_file.pdf
```

### 5.7 Test Statistics

```bash
# Get user statistics
curl http://localhost:8000/api/statistics \
  -H "Authorization: Bearer YOUR_JWT"

# Get statistics for date range
curl "http://localhost:8000/api/statistics?from=2025-01-01&to=2025-12-31" \
  -H "Authorization: Bearer YOUR_JWT"
```

### 5.8 Test Recurring Tasks

```bash
# Create daily recurring task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Take vitamin",
    "recurrence_pattern": "daily"
  }'

# Wait for background job to run (every hour)
# Or manually trigger: python scripts/generate_recurring_tasks.py
```

---

## 6. AI Chatbot Testing

The AI chatbot now understands advanced commands:

### Category Commands
```
"Add work task deploy app"
"Show all work tasks"
"Move task 5 to personal category"
```

### Priority Commands
```
"Add critical priority task fix bug"
"Set task 3 to high priority"
"Show all high priority tasks"
```

### Due Date Commands
```
"Add task due tomorrow finish report"
"Add task due next Friday at 5pm review code"
"Show overdue tasks"
"Show tasks due this week"
```

### Search Commands
```
"Find tasks about meeting"
"Search for grocery tasks"
```

### Subtask Commands
```
"Add subtask to task 5: write tests"
"Show subtasks of task 3"
```

### Tag Commands
```
"Add task tagged urgent and meeting"
"Show tasks tagged work"
```

### Recurring Task Commands
```
"Add daily task take vitamin"
"Create weekly task review goals"
```

**Test via Chat UI**:
1. Go to `http://localhost:3000/chat`
2. Type any of the above commands
3. Verify AI correctly creates tasks with proper fields

---

## 7. Frontend Setup

### 7.1 Start Development Server

```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000`

### 7.2 New Pages Available

- **Dashboard**: `http://localhost:3000/dashboard` (enhanced with filters, search, sorting)
- **Statistics**: `http://localhost:3000/dashboard/statistics` (charts and analytics)
- **Categories**: `http://localhost:3000/dashboard/categories` (category management)
- **Chat**: `http://localhost:3000/chat` (AI chatbot with advanced commands)

### 7.3 New Features in UI

**Dashboard Enhancements**:
- 🔍 Search bar (real-time task search)
- 🏷️ Category filter sidebar
- ⚡ Priority filter (Critical, High, Medium, Low)
- 📅 Due date filters (Today, This Week, Overdue)
- 🏷️ Tag filter (click tags to filter)
- ↕️ Sort options (Priority, Due Date, Alphabetical)

**Task Detail View**:
- ✅ Subtask list with progress bar
- 🏷️ Tag chips
- 📎 File attachments
- 📝 Activity log (change history)

**New Charts** (Statistics Page):
- Bar chart: Tasks completed per day
- Pie chart: Completion rate
- Line chart: Productivity trend

---

## 8. Database Performance Tuning (Optional)

For optimal performance with large datasets:

```sql
-- Analyze tables after migration
ANALYZE tasks;
ANALYZE categories;
ANALYZE tags;
ANALYZE subtasks;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Rebuild search vectors for existing tasks
UPDATE tasks SET search_vector =
  setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
  setweight(to_tsvector('english', COALESCE(description, '')), 'B')
WHERE search_vector IS NULL;
```

---

## 9. Troubleshooting

### Issue: APScheduler not running

**Solution**:
```python
# In src/main.py, verify scheduler is started
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(generate_recurring_tasks, 'interval', hours=1)
scheduler.start()
```

### Issue: Cloudinary upload fails

**Solution**:
- Verify environment variables are set
- Check API credentials in Cloudinary dashboard
- Ensure file size is <10MB
- Check network connectivity

### Issue: Full-text search not working

**Solution**:
```sql
-- Rebuild search vectors
UPDATE tasks SET search_vector =
  setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
  setweight(to_tsvector('english', COALESCE(description, '')), 'B');

-- Verify GIN index exists
SELECT indexname FROM pg_indexes WHERE tablename = 'tasks' AND indexname = 'idx_tasks_search';
```

### Issue: Charts not rendering

**Solution**:
- Check Recharts is installed: `npm list recharts`
- Verify statistics API returns data
- Check browser console for errors
- Ensure data format matches chart expectations

---

## 10. Production Deployment Checklist

Before deploying to production:

- [ ] Run all database migrations
- [ ] Set all environment variables (Cloudinary, etc.)
- [ ] Test file upload limits (10MB max)
- [ ] Enable rate limiting on file uploads (10/hour/user)
- [ ] Set up database backups (includes new tables)
- [ ] Monitor APScheduler job execution
- [ ] Test recurring task generation
- [ ] Verify search performance with 1000+ tasks
- [ ] Enable HTTPS for file uploads
- [ ] Configure CDN for Cloudinary
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Test all AI chatbot commands end-to-end

---

## 11. Next Steps

### Optional Enhancements

1. **Dark Mode for Statistics**: Add theme toggle for charts
2. **Export Tasks**: Add CSV/PDF export functionality
3. **Bulk Operations**: "Complete all tasks tagged urgent"
4. **Advanced Recurrence**: Custom recurrence patterns (every 2 weeks, last day of month)
5. **Email Reminders**: Send email for overdue tasks
6. **Calendar View**: Visual calendar for due dates

### Go to Phase 5

Once Phase 4 is complete and tested:
```bash
git checkout 005-advanced-task-filters
/sp.plan  # Create plan for natural language query enhancement
```

---

## 12. Resources

### Documentation Links

- **python-dateutil**: https://dateutil.readthedocs.io/
- **Recharts**: https://recharts.org/
- **Cloudinary**: https://cloudinary.com/documentation
- **APScheduler**: https://apscheduler.readthedocs.io/
- **PostgreSQL Full-Text Search**: https://www.postgresql.org/docs/current/textsearch.html

### API Reference

- **OpenAPI Spec**: `specs/004-intermediate-features/contracts/api.yaml`
- **Data Models**: `specs/004-intermediate-features/data-model.md`
- **Implementation Plan**: `specs/004-intermediate-features/plan.md`

---

**Quickstart Status**: ✅ Complete
**Estimated Setup Time**: 30-45 minutes
**Next Command**: `/sp.tasks` to generate implementation tasks
