# Todo Application

A full-stack task management web application with user authentication and multi-tenant support.

## Overview

This project implements a complete todo application with:
- **Phase 1**: CLI-based task manager (legacy)
- **Phase 2**: Modern web application with authentication and cloud database (current)

## Tech Stack

### Backend
- **Python 3.13+** with FastAPI
- **SQLModel** for ORM
- **Neon PostgreSQL** (serverless)
- **JWT Authentication** (24-hour expiration)
- **Alembic** for migrations

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
# Edit .env with your Neon DATABASE_URL and JWT_SECRET

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
│   │   ├── services/          # Business logic
│   │   ├── api/
│   │   │   ├── routes/        # API endpoints
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
│   │   └── dashboard/         # Protected dashboard
│   ├── components/            # React components
│   │   ├── TaskForm.tsx
│   │   ├── TaskList.tsx
│   │   └── TaskItem.tsx
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
│   └── 002-web-app-transformation/  # Phase 2 (Web)
│       ├── spec.md            # Requirements
│       ├── plan.md            # Architecture
│       ├── tasks.md           # Task breakdown
│       ├── data-model.md      # Database schema
│       ├── contracts/         # API contracts
│       ├── research.md        # Technical decisions
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

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | API information | No |
| GET | `/health` | Health check | No |
| POST | `/api/tasks` | Create task | Yes |
| GET | `/api/tasks` | List user's tasks | Yes |
| GET | `/api/tasks/{id}` | Get specific task | Yes |
| PATCH | `/api/tasks/{id}` | Update task | Yes |
| DELETE | `/api/tasks/{id}` | Delete task | Yes |

All protected endpoints require `Authorization: Bearer <JWT_TOKEN>` header.

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
JWT_SECRET=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
JWT_EXPIRATION=86400
API_PORT=8000
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

### Backend (Railway/Render)

1. Push to GitHub
2. Connect repository
3. Add environment variables
4. Deploy

### Frontend (Vercel)

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Database (Neon)

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

- **Phase 1** (001-basic-todo-ops): CLI-based task manager
- **Phase 2** (002-web-app-transformation): Full-stack web application ✅ Current

---

Built with ❤️ for Q4 2025 Hackathon
