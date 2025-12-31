# Quick Start Guide: AI-Powered Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Prerequisites**: Phase 2 (Web App with Authentication) must be set up and running
**Time to Complete**: ~15 minutes

## Overview

This guide walks you through setting up the AI-powered chatbot feature that allows users to manage todos through natural language conversation.

---

## Prerequisites Check

Before starting, verify Phase 2 is working:

- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:3000
- [ ] Neon PostgreSQL database connected
- [ ] You can sign in and create tasks via web UI
- [ ] You have an OpenRouter API account (free tier available)

---

## Step 1: Get OpenRouter API Key

1. Go to [openrouter.ai](https://openrouter.ai/)
2. Sign in with Google/GitHub or create account
3. Navigate to **Keys** section in dashboard
4. Click **Create Key**
5. Copy the key (starts with `sk-or-v1-...`)
6. **Important**: Save it securely!

**Free Tier**: This project uses `meta-llama/llama-3.3-70b-instruct:free` - completely free for development!

**Cost Estimate** (if upgrading to paid models):
- GPT-4o: ~$2.50 per 1M input tokens
- Claude 3.5 Sonnet: ~$3 per 1M input tokens
- Llama 3.3 70B (paid): ~$0.35 per 1M tokens
- 100 chat messages with free model: **$0.00**

---

## Step 2: Install Backend Dependencies

```bash
cd backend

# If using pip
pip install httpx

# If using uv (recommended)
uv add httpx

# Verify installation
python -c "import httpx; print(httpx.__version__)"
```

**Expected Output**: `0.x.x` (httpx version)

**Note**: This project uses OpenRouter API via direct HTTP calls with `httpx`, not the OpenAI SDK. The MCP tools are integrated directly in the chat agent.

---

## Step 3: Configure Environment Variables

Edit `backend/.env` and add:

```env
# Existing variables (keep these)
DATABASE_URL=postgresql://...
JWT_SECRET=...
CORS_ORIGINS=http://localhost:3000

# New variables for Phase 3 (OpenRouter)
OPENAI_API_KEY=sk-or-v1-...  # Your OpenRouter API key from Step 1
OPENAI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

**Important Notes**:
- `OPENAI_API_KEY`: Despite the name, this is your **OpenRouter** API key (starts with `sk-or-v1-`)
- `OPENAI_BASE_URL`: Must be OpenRouter endpoint, NOT OpenAI's API
- `AI_MODEL`: Free Llama model (or upgrade to paid model like `openai/gpt-4o`)

**Security**: Never commit `.env` to git! Verify `.env` is in `.gitignore`.

---

## Step 4: Run Database Migrations

Create new tables for conversations and messages:

```bash
cd backend

# Generate migrations (if not already created)
alembic revision --autogenerate -m "Add conversations and messages tables"

# Apply migrations
alembic upgrade head

# Verify tables exist
python -c "
from sqlmodel import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute(text(\"SELECT tablename FROM pg_tables WHERE schemaname='public'\"))
    tables = [row[0] for row in result]
    print('Tables:', tables)
    assert 'conversations' in tables, 'conversations table missing!'
    assert 'messages' in tables, 'messages table missing!'
    print('✓ Database migration successful!')
"
```

**Expected Output**:
```
Tables: ['tasks', 'conversations', 'messages']
✓ Database migration successful!
```

**Troubleshooting**:
- If migration fails, check `DATABASE_URL` is correct
- Ensure Neon database is accessible (not paused)
- Run `alembic current` to see current migration status

---

## Step 5: Verify Frontend Dependencies

```bash
cd frontend

# Verify Next.js and dependencies are installed
npm list next react tailwindcss

# If not installed:
npm install
```

**Note**: This project uses a custom-built glassmorphic chat UI instead of ChatKit. All dependencies should already be installed from Phase 2 setup.

---

## Step 6: Start Backend Server

```bash
cd backend

# Start with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
════════════════════════════════════════════════════════════
🚀 BACKEND STARTING WITH DEBUG MODE
════════════════════════════════════════════════════════════
OpenRouter API Key: sk-or-v1-xxxxx...
Base URL: https://openrouter.ai/api/v1
Model: meta-llama/llama-3.3-70b-instruct:free
════════════════════════════════════════════════════════════
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify**:
- ✅ API key shows (truncated for security)
- ✅ Base URL is `https://openrouter.ai/api/v1`
- ✅ Model is free Llama model
- Open http://localhost:8000 in browser - should see API info JSON
- Open http://localhost:8000/docs for Swagger UI
- Look for `/api/chat/` endpoint in documentation

---

## Step 7: Start Frontend Server

```bash
cd frontend

# Start development server
npm run dev
```

**Expected Output**:
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.5s
```

---

## Step 8: Test the Chatbot

### Test 1: Access Chat Interface

1. Open http://localhost:3000 in browser
2. Sign in with your Phase 2 account
3. Click **AI Chat** in navigation menu
4. You should see chat interface with input box

### Test 2: Create Task via Chat

1. Type: `Add a task to buy groceries`
2. Press Enter
3. **Expected**: AI responds with "✓ Created task: Buy groceries (ID: X)"
4. **Verify**: Go to /dashboard - task should appear in task list

### Test 3: List Tasks

1. Type: `Show me my tasks`
2. **Expected**: AI lists all your tasks with IDs and completion status

### Test 4: Complete Task

1. Note task ID from previous step (e.g., ID: 5)
2. Type: `Mark task 5 as complete`
3. **Expected**: AI confirms "✓ Completed task: Buy groceries"
4. **Verify**: Task shows checkmark in /dashboard

### Test 5: Conversation Persistence

1. Refresh the page (F5)
2. **Expected**: Chat history is preserved - all previous messages visible
3. **Verify Stateless Architecture**: Restart backend server, chat history still intact

---

## Step 9: Verify Stateless Architecture

**Test Statelessness**:

```bash
# Terminal 1: Run backend
cd backend
uvicorn src.api.main:app --reload

# Terminal 2: Send chat request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "Show my tasks"}'

# Terminal 1: Stop server (Ctrl+C)
# Terminal 1: Restart server
uvicorn src.api.main:app --reload

# Terminal 2: Send another request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "Show my tasks"}'

# Should work - no "session lost" error
```

**Expected**: Both requests succeed. Conversation history preserved across server restarts.

---

## Step 10: Monitor Logs

### Backend Logs

```bash
cd backend
tail -f logs/app.log  # If logging to file

# Or watch console output
# You should see:
# - "Processing chat message for user: {user_id}"
# - "Initializing AI agent with MCP tools"
# - "Tool executed: add_task"
# - "Saved assistant response to database"
```

### Database Queries

```bash
# Check messages table
psql $DATABASE_URL -c "SELECT role, substring(content, 1, 50) as content FROM messages ORDER BY created_at DESC LIMIT 5;"

# Expected output:
   role    |                content
-----------+--------------------------------------------------
assistant | ✓ Completed task: Buy groceries
user      | Mark task 5 as complete
assistant | Your tasks: 1. [ ] Buy groceries (ID: 5)
user      | Show me my tasks
...
```

---

## Troubleshooting

### Issue: "OpenRouter API key not found" or 401 Unauthorized

**Cause**: Environment variable not loaded or invalid API key

**Fix**:
```bash
# Verify .env file exists and has correct key
cat backend/.env | grep OPENAI_API_KEY
# Should show: OPENAI_API_KEY=sk-or-v1-xxxxx

# Restart backend server (reload .env)
cd backend
uvicorn src.api.main:app --reload
```

**Verify on startup**:
- Logs should show `OpenRouter API Key: sk-or-v1-xxxxx...`
- If showing `MISSING` or wrong prefix, check `.env` file

### Issue: "AI service temporarily unavailable"

**Cause**: OpenRouter API rate limit or network error

**Fix**:
1. Check API key is valid: https://openrouter.ai/keys
2. Check free tier limits: https://openrouter.ai/docs/limits
3. Wait 1 minute and retry
4. Try different free model if needed

### Issue: "Table 'conversations' does not exist"

**Cause**: Migration not run

**Fix**:
```bash
cd backend
alembic upgrade head
```

### Issue: Chat messages not persisting

**Cause**: Database connection issue or missing indexes

**Fix**:
```bash
# Check database connection
python -c "
from sqlmodel import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
print('✓ Database connected')
"

# Verify indexes
psql $DATABASE_URL -c "\d messages"
# Should show idx_messages_conversation_id index
```

### Issue: Frontend shows "Network Error"

**Cause**: Backend not running or CORS misconfigured

**Fix**:
1. Verify backend running: http://localhost:8000
2. Check CORS in `backend/.env`:
   ```env
   CORS_ORIGINS=http://localhost:3000
   ```
3. Check browser console for specific error

### Issue: "JWT token invalid"

**Cause**: Signed out or token expired

**Fix**:
1. Go to http://localhost:3000/auth/sign-in
2. Sign in again
3. JWT token auto-refreshed

---

## Performance Benchmarks

### Expected Response Times

| Operation | Target | Actual |
|-----------|--------|--------|
| Create task via chat | <5s | ~2-3s |
| List tasks via chat | <3s | ~1-2s |
| Complete task via chat | <5s | ~2-3s |
| Load chat history (50 msgs) | <2s | ~500ms |

**Test Performance**:
```bash
# Install httpie
pip install httpie

# Measure response time
time http POST http://localhost:8000/api/chat \
  Authorization:"Bearer $TOKEN" \
  message="Show my tasks"
```

---

## Next Steps

### Explore Features

- [x] Basic chat interface working
- [ ] Try updating tasks: `Change task 1 title to 'Buy organic milk'`
- [ ] Try deleting tasks: `Delete task 2`
- [ ] Test error handling: `Complete task 999999` (should return "Task not found")
- [ ] Test ambiguous commands: `milk` (AI should ask for clarification)

### Production Deployment

For production deployment guide, see:
- Backend: Deploy to Railway/Render
- Frontend: Deploy to Vercel
- Database: Already on Neon (production-ready)

**Environment Variables for Production**:
```env
# Backend
DATABASE_URL=postgresql://...  # Neon production URL
OPENAI_API_KEY=sk-or-v1-...    # OpenRouter production API key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=meta-llama/llama-3.3-70b-instruct:free  # Or paid model
JWT_SECRET=...                 # Strong random secret
CORS_ORIGINS=https://yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
BETTER_AUTH_SECRET=...         # Same as JWT_SECRET
```

---

## Useful Commands

```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Check database tables
psql $DATABASE_URL -c "\dt"

# View recent messages
psql $DATABASE_URL -c "SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;"

# Count total messages
psql $DATABASE_URL -c "SELECT COUNT(*) FROM messages;"

# Check OpenRouter usage and credits
# Go to: https://openrouter.ai/activity
```

---

## Development Workflow

### Day-to-day Development

```bash
# Terminal 1: Backend (auto-reload on file changes)
cd backend
uvicorn src.api.main:app --reload

# Terminal 2: Frontend (auto-reload on file changes)
cd frontend
npm run dev

# Terminal 3: Watch logs
cd backend
tail -f logs/app.log

# Terminal 4: Run tests
cd backend
pytest tests/ -v
```

### Making Changes

1. **Update MCP Tools**: Edit `backend/src/mcp/tools.py`
2. **Update AI Prompt**: Edit `backend/src/agent/prompts.py`
3. **Update Frontend UI**: Edit `frontend/components/ChatInterface.tsx`
4. **Changes auto-reload** in both backend and frontend

### Testing Changes

```bash
# Unit tests
cd backend
pytest tests/test_mcp_tools.py -v

# Integration tests
pytest tests/test_chat_endpoint.py -v

# Manual testing
# Use chat interface at http://localhost:3000/chat
```

---

## Resources

- **OpenRouter API Docs**: https://openrouter.ai/docs
- **OpenRouter Models**: https://openrouter.ai/models
- **OpenRouter Limits**: https://openrouter.ai/docs/limits
- **Llama 3.3 70B Info**: https://openrouter.ai/meta-llama/llama-3.3-70b-instruct:free
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **httpx Docs**: https://www.python-httpx.org/

---

## Support

If you encounter issues:

1. Check logs: `backend/logs/app.log`
2. Verify environment variables: `cat backend/.env`
3. Test API directly: http://localhost:8000/docs
4. Check database: `psql $DATABASE_URL`
5. Create GitHub issue with:
   - Error message
   - Steps to reproduce
   - Environment (OS, Python version, Node version)

---

**Version**: 1.0.0 | **Created**: 2025-12-30 | **Status**: Ready for Use
