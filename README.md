---
title: Todo App
emoji: ✅
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
license: mit
short_description: AI-powered task management with chat interface
---

# Todo Application

A full-stack task management web application with user authentication and multi-tenant support.

## Overview

This project implements a complete todo application with:
- **Phase 1**: CLI-based task manager (legacy)
- **Phase 2**: Modern web application with authentication and cloud database
- **Phase 3**: AI-powered chatbot for task management via natural language
- **Phase 4**: Kubernetes deployment with Helm charts (current)

## Tech Stack

### Backend
- **Python 3.13+** with FastAPI
- **SQLModel** for ORM
- **Neon PostgreSQL** (serverless)
- **JWT Authentication** (24-hour expiration)
- **Alembic** for migrations
- **OpenRouter API** (AI chatbot with Llama 3.3 70B)
- **httpx** for async API calls

### Frontend
- **Next.js 16+** (App Router)
- **TypeScript 5.x**
- **Better Auth** (JWT sessions)
- **Tailwind CSS 4**
- **Lucide React** (icons)

## Features

✅ **Authentication**
- User registration with email/password
- Secure sign-in with JWT
- Session management with httpOnly cookies
- Route protection middleware
- Logout functionality

✅ **Task Management**
- Create tasks with title and description
- View all tasks (ordered by created date)
- Toggle task completion status
- Edit task details inline
- Delete tasks with confirmation
- Optimistic UI updates

✅ **Advanced Task Features (Phase 4)**
- **Categories**: Organize tasks with colored categories and custom icons
- **Priorities**: Set task priority levels (Critical, High, Medium, Low)
- **Due Dates**: Assign due dates with natural language parsing
- **Search**: Full-text search across task titles, descriptions, and notes
- **Subtasks**: Break down tasks into checklist items with progress tracking
- **Statistics**: View productivity charts and completion analytics
- **Tags**: Add multiple hashtags to tasks for flexible organization
- **Recurring Tasks**: Create daily, weekly, or monthly recurring tasks

✅ **Security**
- User isolation (Golden Rule: all queries include WHERE user_id filter)
- JWT validation on all protected endpoints
- Password hashing with bcrypt
- CORS configuration
- Global error handling

✅ **UI/UX**
- Responsive design (mobile, tablet, desktop)
- Dark mode support
- Form validation
- Loading states
- Error handling with rollback

✅ **AI Chatbot** (Phase 3)
- Natural language task management
- Multilingual support (English/Urdu)
- Conversation history with persistence
- Automatic language translation
- Create, list, complete, delete, update tasks via chat
- Intelligent parsing of categories, priorities, due dates
- Hashtag parsing for automatic tagging
- Recurring task pattern recognition
- Subtask management via natural language
- Stateless AI agent architecture
- Beautiful glassmorphic chat interface

## Quick Start

### Prerequisites

- **Python 3.13+**
- **Node.js 18+**
- **Neon PostgreSQL account** (free tier at [neon.tech](https://neon.tech))

### 1. Clone Repository

```bash
git clone <repo-url>
cd todo-app-hackthon2
```

### 2. Setup Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt
# or
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your:
#   - Neon DATABASE_URL
#   - JWT_SECRET
#   - OPENAI_API_KEY (OpenRouter API key from https://openrouter.ai)

# Run migrations
alembic upgrade head

# Start API server
uvicorn src.api.main:app --reload
```

Backend runs at: http://localhost:8000
API Docs: http://localhost:8000/docs

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with API URL and auth secret

# Start development server
npm run dev
```

Frontend runs at: http://localhost:3000

## Project Structure

```
todo-app-hackthon2/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── models/            # SQLModel entities
│   │   │   ├── task.py        # Task model
│   │   │   ├── conversation.py # Chat conversation
│   │   │   └── message.py     # Chat messages
│   │   ├── services/          # Business logic
│   │   │   ├── task_service.py
│   │   │   └── chat_service.py # AI chat orchestration
│   │   ├── agent/             # AI chatbot (Phase 3)
│   │   │   └── chat_agent.py  # OpenRouter integration
│   │   ├── mcp/               # MCP tools placeholder
│   │   │   ├── base.py
│   │   │   └── tools.py
│   │   ├── api/
│   │   │   ├── routes/        # API endpoints
│   │   │   │   ├── tasks.py   # Task CRUD
│   │   │   │   └── chat.py    # Chat endpoints
│   │   │   ├── deps.py        # Dependencies (DB, Auth)
│   │   │   └── main.py        # FastAPI app
│   │   └── db/
│   │       ├── session.py     # Database connection
│   │       └── migrations/    # Alembic migrations
│   ├── tests/
│   ├── .env.example
│   ├── pyproject.toml
│   ├── alembic.ini
│   └── README.md
│
├── frontend/                   # Next.js frontend
│   ├── app/
│   │   ├── page.tsx           # Landing page
│   │   ├── auth/              # Sign-in/Sign-up
│   │   ├── dashboard/         # Protected dashboard
│   │   └── chat/              # AI Chat interface (Phase 3)
│   │       └── page.tsx       # Chat UI with glassmorphism
│   ├── components/            # React components
│   │   ├── TaskForm.tsx
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   └── ConfirmDialog.tsx  # Custom modals
│   ├── lib/
│   │   ├── api.ts            # API client
│   │   └── auth.ts           # Better Auth config
│   ├── types/
│   │   └── index.ts          # TypeScript interfaces
│   ├── middleware.ts         # Route protection
│   ├── .env.local.example
│   ├── package.json
│   └── README.md
│
├── specs/                      # Feature specifications
│   ├── 001-basic-todo-ops/    # Phase 1 (CLI)
│   ├── 002-web-app-transformation/  # Phase 2 (Web)
│   │   ├── spec.md            # Requirements
│   │   ├── plan.md            # Architecture
│   │   ├── tasks.md           # Task breakdown
│   │   ├── data-model.md      # Database schema
│   │   ├── contracts/         # API contracts
│   │   ├── research.md        # Technical decisions
│   │   └── quickstart.md      # Setup guide
│   └── 003-ai-todo-chatbot/   # Phase 3 (AI Chat)
│       ├── spec.md            # AI chatbot requirements
│       ├── plan.md            # Architecture decisions
│       ├── tasks.md           # Implementation tasks
│       ├── data-model.md      # Conversation schema
│       └── quickstart.md      # Setup guide
│
├── history/                    # Documentation
│   ├── prompts/               # Development history
│   └── adr/                   # Architecture decisions
│
├── .specify/                   # Templates and scripts
└── README.md                   # This file
```

## Architecture

### Backend API

```
FastAPI Application
├── Routes (/api/tasks)
│   ├── POST /api/tasks         → Create task
│   ├── GET /api/tasks          → List user's tasks
│   ├── GET /api/tasks/{id}     → Get specific task
│   ├── PATCH /api/tasks/{id}   → Update task
│   └── DELETE /api/tasks/{id}  → Delete task
│
├── Middleware
│   ├── CORS (credentials support)
│   └── Global error handling
│
├── Dependencies
│   ├── get_db() → Database session
│   └── get_current_user() → JWT validation
│
└── Services
    └── TaskService → Business logic with user isolation
```

### Frontend Structure

```
Next.js App Router
├── Public Routes
│   ├── / (Landing page)
│   ├── /auth/sign-in
│   └── /auth/sign-up
│
├── Protected Routes
│   └── /dashboard (requires JWT)
│
├── Middleware
│   └── Route protection
│
└── Components
    ├── TaskForm → Create tasks
    ├── TaskList → Display tasks
    └── TaskItem → Task actions
```

### Database Schema

```sql
-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | API information | No |
| GET | `/health` | Health check | No |
| POST | `/api/tasks` | Create task | Yes |
| GET | `/api/tasks` | List user's tasks | Yes |
| GET | `/api/tasks/{id}` | Get specific task | Yes |
| PATCH | `/api/tasks/{id}` | Update task | Yes |
| DELETE | `/api/tasks/{id}` | Delete task | Yes |

### AI Chat Endpoints (Phase 3)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/chat/` | Send message to AI chatbot | Yes |
| GET | `/api/chat/conversations` | List user's conversations | Yes |
| GET | `/api/chat/conversations/{id}/messages` | Get conversation history | Yes |
| DELETE | `/api/chat/conversations/{id}` | Delete conversation | Yes |

All protected endpoints require `Authorization: Bearer <JWT_TOKEN>` header.

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
JWT_SECRET=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
JWT_EXPIRATION=86400
API_PORT=8000

# AI Chatbot (Phase 3)
OPENAI_API_KEY=sk-or-v1-xxxxx  # OpenRouter API key from https://openrouter.ai
OPENAI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=same-as-backend-jwt-secret
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

## Development Workflow

### 1. Start Backend

```bash
cd backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

### 3. Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Create Account

1. Navigate to http://localhost:3000
2. Click "Get Started Free"
3. Register with email/password
4. Start managing tasks!

### 5. Use AI Chatbot (Phase 3)

1. Navigate to http://localhost:3000/chat
2. Switch language (English/اردو) if needed
3. Chat naturally with the AI:
   - "Add a task to buy milk"
   - "Show me my tasks"
   - "Mark task 5 as complete"
   - "Delete task 3"
   - "Update task 2 title to 'Buy organic milk'"
4. View conversation history in sidebar
5. Create new conversations or delete old ones

## Testing

### Manual Testing

1. **Authentication Flow**:
   - Sign up with new account
   - Sign in with credentials
   - Access dashboard (should redirect if not authenticated)
   - Log out (should clear session)

2. **Task Management**:
   - Create task with title and description
   - View task in list
   - Toggle completion status
   - Edit task inline
   - Delete task with confirmation

3. **Security**:
   - Verify users can only see their own tasks
   - Test JWT expiration (after 24 hours)
   - Verify protected routes redirect to sign-in

### Backend Testing

```bash
cd backend
pytest
pytest --cov=src
```

### Frontend Testing

```bash
cd frontend
npm test  # (when tests are added)
```

## Deployment

### Phase IV: Kubernetes Deployment (Development & Production)

Deploy the Todo App to Kubernetes using Minikube (local) or any cloud provider.

#### Quick Start

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=4096
minikube addons enable metrics-server

# 2. Build Docker images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# 3. Load images into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# 4. Deploy with Helm
helm install todo-app helm/todo-app -n todo-app \
  -f helm/todo-app/values-dev.yaml

# 5. Port-forward and access
kubectl port-forward service/frontend 3000:3000 -n todo-app &
# Open http://localhost:3000
```

#### Documentation

- **Quickstart**: `specs/006-phase-4-kubernetes/quickstart.md` (30 min setup)
- **Deployment Guide**: `specs/006-phase-4-kubernetes/DEPLOYMENT.md` (step-by-step)
- **Troubleshooting**: `specs/006-phase-4-kubernetes/TROUBLESHOOTING.md` (common issues)
- **Pre/Post Checklist**: `specs/006-phase-4-kubernetes/CHECKLIST.md` (verification)
- **DevOps Tools**: `specs/006-phase-4-kubernetes/DEVOPS.md` (Gordon, kubectl-ai, kagent)
- **Environment Variables**: `specs/006-phase-4-kubernetes/ENVIRONMENT_VARIABLES.md` (config guide)
- **Helm Chart**: `helm/todo-app/README.md` (chart reference)
- **Architecture**: `specs/006-phase-4-kubernetes/spec.md` (full specification)
- **Research**: `specs/006-phase-4-kubernetes/research.md` (design decisions)

#### Key Features

- **Containerized**: Multi-stage Docker builds for both frontend and backend
- **Local K8s**: Minikube for development/testing
- **Helm Charts**: Production-ready with dev/staging/prod values
- **Auto-Scaling**: Horizontal Pod Autoscaler for high availability
- **Health Checks**: Liveness and readiness probes
- **ConfigMaps**: Non-sensitive configuration management
- **Secrets**: Secure handling of API keys and credentials
- **Service Discovery**: Internal service-to-service communication
- **External Database**: Neon PostgreSQL integration

#### Infrastructure Files

- `frontend/Dockerfile` - Multi-stage Node.js build
- `backend/Dockerfile` - Python Alpine runtime
- `docker-compose.yml` - Local 3-service stack
- `helm/todo-app/` - Complete Helm chart with templates
- `k8s/setup.sh` - Minikube setup script

### Traditional Deployment (Cloud Providers)

#### Backend (Railway/Render)

1. Push to GitHub
2. Connect repository
3. Add environment variables
4. Deploy

#### Frontend (Vercel)

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

#### Database (Neon)

Already serverless - no deployment needed!

## Security Features

- **Golden Rule**: All database queries include `WHERE user_id = current_user_id`
- **JWT Tokens**: 24-hour expiration, httpOnly cookies
- **Password Hashing**: Bcrypt with salt (handled by Better Auth)
- **CORS**: Specific origins only (no wildcards with credentials)
- **Error Handling**: Never exposes internal details
- **Input Validation**: Pydantic models on backend, client-side validation on frontend

## Performance

- **Database**: Connection pooling with pool_pre_ping for Neon serverless
- **Frontend**: Optimistic UI updates for instant feedback
- **API**: <500ms response time for 95th percentile
- **Dashboard**: <2s load time for 10+ tasks

## Documentation

- **Backend**: See `backend/README.md`
- **Frontend**: See `frontend/README.md`
- **API Specification**: See `specs/002-web-app-transformation/contracts/api.yaml`
- **Architecture**: See `specs/002-web-app-transformation/plan.md`

## Known Limitations

- No automated tests (manual testing only)
- No rate limiting
- No password reset functionality
- No email verification
- No task sharing/collaboration
- No task categories or tags
- No search functionality
- No task due dates

## Future Enhancements

- Add automated tests (pytest, Jest, Playwright)
- Implement rate limiting
- Add password reset via email
- Email verification for new accounts
- Task sharing between users
- Task categories and tags
- Search and filtering
- Task due dates and reminders
- Task attachments
- Task comments

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

For detailed setup instructions, see:
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`

For issues or questions, please open an issue on GitHub.

## Project History

- **Phase 1** (001-basic-todo-ops): CLI-based task manager ✅
- **Phase 2** (002-web-app-transformation): Full-stack web application ✅
- **Phase 3** (003-ai-todo-chatbot): AI-powered chatbot for task management ✅
- **Phase 4** (006-phase-4-kubernetes): Kubernetes deployment with Helm charts ✅ **Current**
- **Phase 5** (Hugging Face Deployment): Optimized for Hugging Face Spaces deployment ✅ **Latest**

### Phase 4 Highlights

- **Docker Containerization**: Multi-stage builds for optimized images (150-300MB)
- **Kubernetes Ready**: Deploy to Minikube or any K8s cluster
- **Helm Charts**: Production-ready with values overrides (dev/staging/prod)
- **Auto-Scaling**: HPA configured for high availability (2-5 replicas, 70% CPU trigger)
- **Health Management**: Liveness and readiness probes for self-healing
- **Configuration Management**: ConfigMaps and Secrets for secure deployments
- **AI DevOps Tools**: Integration with Gordon, kubectl-ai, and kagent
- **Comprehensive Docs**: 10+ guides covering deployment, troubleshooting, and best practices

### Phase 5 Highlights (Hugging Face Deployment)

- **Enhanced Database Reliability**: Improved Neon PostgreSQL connection with exponential backoff and jitter for cold starts
- **Robust Authentication**: Dual fallback mechanism using both cookies and localStorage for Hugging Face Spaces compatibility
- **Improved Error Handling**: Better error messages and retry mechanisms for task fetching and chat functionality
- **Hugging Face Optimized**: Fixed cookie stripping issues and API route mismatches for seamless deployment
- **Deployment Guide**: Comprehensive documentation for Hugging Face Spaces deployment in `HUGGING_FACE_DEPLOYMENT.md`

For Hugging Face deployment instructions, see:
- `HUGGING_FACE_DEPLOYMENT.md` - Complete deployment guide with environment variables and troubleshooting

For detailed Phase 4 documentation, see:
- `specs/006-phase-4-kubernetes/quickstart.md` - 30-minute quick start
- `specs/006-phase-4-kubernetes/DEPLOYMENT.md` - Step-by-step deployment
- `specs/006-phase-4-kubernetes/TROUBLESHOOTING.md` - Common issues & solutions
- `specs/006-phase-4-kubernetes/CHECKLIST.md` - Pre/post deployment verification

### Phase 3 Highlights

- **Multilingual AI**: Chat in English or Urdu with automatic translation
- **Natural Language**: Manage tasks conversationally
- **Stateless Architecture**: Fresh agent on each request for reliability
- **Beautiful UI**: 3D glassmorphism design with smooth animations
- **Conversation Persistence**: Chat history saved across sessions

For detailed Phase 3 documentation, see:
- `specs/003-ai-todo-chatbot/quickstart.md` - Setup guide
- `specs/003-ai-todo-chatbot/plan.md` - Architecture decisions
- `URDU_TRANSLATION_TEST_GUIDE.md` - Multilingual testing

---

Built with ❤️ for Q4 2025 Hackathon
