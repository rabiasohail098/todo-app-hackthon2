# Quickstart: Web Application Transformation

**Feature**: 002-web-app-transformation
**Date**: 2025-12-10

## Prerequisites

- Python 3.13+ with UV package manager
- Node.js 20+ with npm/pnpm
- Neon PostgreSQL account (free tier available)
- Git

## 1. Clone and Setup

```bash
# Clone repository
git clone <repo-url>
cd todo-app-hackthon2

# Create feature branch
git checkout -b 002-web-app-transformation
```

## 2. Backend Setup

### Create Backend Directory Structure

```bash
mkdir -p backend/src/{models,services,api/routes,db/migrations}
mkdir -p backend/tests/{unit,integration}
```

### Initialize Python Project

```bash
cd backend

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "todo-api"
version = "1.0.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlmodel>=0.0.14",
    "psycopg2-binary>=2.9.9",
    "python-jose[cryptography]>=3.3.0",
    "python-dotenv>=1.0.0",
    "alembic>=1.13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",
]
EOF

# Install dependencies
uv sync
```

### Create Environment File

```bash
# backend/.env
cat > .env << 'EOF'
DATABASE_URL=postgresql://user:pass@your-neon-host.neon.tech/dbname?sslmode=require
JWT_SECRET=your-32-byte-secret-key-here-change-me
CORS_ORIGINS=http://localhost:3000
EOF
```

### Run Backend

```bash
# Development server
uv run uvicorn src.api.main:app --reload --port 8000
```

## 3. Frontend Setup

### Create Frontend Directory Structure

```bash
cd ../  # Back to repo root
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
```

### Install Dependencies

```bash
npm install better-auth
# or
pnpm add better-auth
```

### Create Environment File

```bash
# frontend/.env.local
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-32-byte-secret-key-here-change-me
EOF
```

### Run Frontend

```bash
npm run dev
# or
pnpm dev
```

## 4. Database Setup

### Create Neon Database

1. Go to [neon.tech](https://neon.tech) and create account
2. Create new project
3. Copy connection string to `backend/.env`

### Run Migrations

```bash
cd backend
uv run alembic upgrade head
```

## 5. Verify Setup

### Backend Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok", "timestamp": "..."}
```

### Frontend Access

Open http://localhost:3000 in browser

## 6. Development Workflow

### Backend Changes

```bash
cd backend
uv run uvicorn src.api.main:app --reload
uv run pytest  # Run tests
```

### Frontend Changes

```bash
cd frontend
npm run dev
npm run test  # Run tests
npm run build  # Production build
```

### Database Migrations

```bash
cd backend
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

## 7. Testing

### Backend Tests

```bash
cd backend
uv run pytest tests/unit -v        # Unit tests
uv run pytest tests/integration -v  # Integration tests
uv run pytest --cov=src            # Coverage report
```

### Frontend Tests

```bash
cd frontend
npm run test           # Jest tests
npm run test:e2e       # Playwright E2E tests
```

## 8. Common Issues

### CORS Errors

If you see CORS errors in browser console:
1. Verify `CORS_ORIGINS` in backend `.env` includes frontend URL
2. Restart backend after changing `.env`

### Database Connection

If database connection fails:
1. Verify `DATABASE_URL` has `?sslmode=require` suffix
2. Check Neon dashboard for connection limits
3. Verify IP allowlist in Neon settings

### JWT Errors

If authentication fails:
1. Verify `JWT_SECRET` matches in both backend and frontend `.env`
2. Check token expiration (24 hours)
3. Clear browser cookies and try again

## 9. Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Neon PostgreSQL connection string | `postgresql://...@neon.tech/...` |
| JWT_SECRET | Secret for JWT signing (32+ bytes) | `your-secret-key` |
| CORS_ORIGINS | Allowed frontend origins (comma-separated) | `http://localhost:3000` |

### Frontend (`frontend/.env.local`)

| Variable | Description | Example |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API URL | `http://localhost:8000` |
| BETTER_AUTH_SECRET | Secret for Better Auth (32+ bytes) | `your-secret-key` |

## 10. Project Structure After Setup

```
todo-app-hackthon2/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   ├── models/
│   │   ├── services/
│   │   └── db/
│   ├── tests/
│   ├── pyproject.toml
│   └── .env
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── auth/
│   │   └── dashboard/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── .env.local
└── specs/
    └── 002-web-app-transformation/
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        └── contracts/
            └── api.yaml
```
