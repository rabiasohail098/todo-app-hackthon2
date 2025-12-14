# Implementation Plan: Web Application Transformation

**Branch**: `002-web-app-transformation` | **Date**: 2025-12-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-web-app-transformation/spec.md`

## Summary

Transform the existing console-based Todo application into a modern, multi-tenant web application. The implementation uses a full-stack architecture with Next.js 16+ frontend (Better Auth + Tailwind CSS), FastAPI backend (SQLModel ORM), and Neon Serverless PostgreSQL for persistence. Core features include secure JWT-based authentication, user-isolated task CRUD operations, and responsive dashboard UI.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Better Auth, Next.js 16+, Tailwind CSS
**Storage**: Neon Serverless PostgreSQL
**Testing**: pytest (backend), Jest + React Testing Library (frontend)
**Target Platform**: Web (modern browsers ES6+), responsive (min 320px)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: API p95 < 500ms, dashboard load < 2s for 10+ tasks
**Constraints**: 24-hour JWT expiration, 8-char password minimum, no rate limiting (Phase 2)
**Scale/Scope**: 100 concurrent users, multi-tenant with row-level isolation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Phase 1 Status | Phase 2 Justification |
|-----------|---------------|----------------------|
| I. Spec-Driven Development | ✅ PASS | Spec completed with 8 user stories, 26 FRs, 5 NFRs |
| II. CLI-First Architecture | ⚠️ VIOLATION | **Justified**: Phase 2 transforms to web interface |
| III. In-Memory Storage Only | ⚠️ VIOLATION | **Justified**: Phase 2 requires PostgreSQL persistence |
| IV. PEP 8 Code Quality | ✅ PASS | Backend Python code will follow PEP 8 |
| V. No External Dependencies | ⚠️ VIOLATION | **Justified**: Phase 2 requires FastAPI, SQLModel, etc. |
| VI. Clean, Modular Code | ✅ PASS | Monorepo structure with clear separation |

**⚠️ CONSTITUTION AMENDMENT REQUIRED**: This feature represents the Phase 1 → Phase 2 transition. The constitution MUST be updated before implementation to:
1. Remove Phase 1 constraints (CLI-only, in-memory, no dependencies)
2. Add Phase 2 principles (web architecture, database persistence, security)
3. Increment version to 2.0.0 (MAJOR change)

## Project Structure

### Documentation (this feature)

```text
specs/002-web-app-transformation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
│   └── api.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLModel entities (Task, relationships)
│   ├── services/        # Business logic (TaskService, AuthService)
│   ├── api/             # FastAPI routers and dependencies
│   │   ├── routes/      # Endpoint definitions
│   │   ├── deps.py      # JWT validation, DB session
│   │   └── main.py      # FastAPI app entry point
│   └── db/              # Database configuration
│       ├── session.py   # Neon connection pooling
│       └── migrations/  # Alembic migrations
├── tests/
│   ├── unit/            # Service layer tests
│   ├── integration/     # API endpoint tests
│   └── conftest.py      # pytest fixtures
├── pyproject.toml       # Python dependencies (UV)
└── .env.example         # Environment template

frontend/
├── src/
│   ├── app/             # Next.js App Router pages
│   │   ├── page.tsx              # Landing page
│   │   ├── auth/
│   │   │   ├── sign-in/page.tsx  # Sign-in page
│   │   │   └── sign-up/page.tsx  # Sign-up page
│   │   └── dashboard/
│   │       └── page.tsx          # Protected dashboard
│   ├── components/      # Reusable UI components
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   └── AuthForm.tsx
│   ├── lib/             # Utilities and API client
│   │   ├── api.ts       # Fetch wrapper with JWT
│   │   └── auth.ts      # Better Auth configuration
│   └── types/           # TypeScript interfaces
│       └── index.ts     # Task, User types (match Pydantic)
├── tests/
│   └── components/      # React component tests
├── package.json         # Node dependencies
├── tailwind.config.ts   # Tailwind configuration
└── .env.local.example   # Environment template
```

**Structure Decision**: Web application (Option 2) with separate `backend/` and `frontend/` directories. This enables independent deployment, separate CI pipelines, and clear technology boundaries.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| External database (Neon PostgreSQL) | Multi-tenant data persistence required for user isolation | In-memory storage loses data on restart, no user isolation |
| Web framework (FastAPI) | RESTful API required for frontend-backend communication | CLI cannot serve HTTP requests |
| External auth (Better Auth) | Secure JWT implementation with password hashing | Rolling own auth is security risk |
| Frontend framework (Next.js) | Modern web UI with SSR, routing, auth integration | CLI cannot provide web interface |

## Architecture Decisions

### ADR-001: Monorepo with Separate Backend/Frontend

**Decision**: Single repository with `backend/` and `frontend/` directories.

**Rationale**:
- Atomic commits across stack changes
- Shared type definitions possible via codegen
- Simpler development workflow
- Single PR for full-stack features

**Alternatives Rejected**:
- Polyrepo: Coordination overhead, version drift
- Single project: Technology mismatch (Python + TypeScript)

### ADR-002: JWT Storage in httpOnly Cookies

**Decision**: Store JWT in httpOnly cookies rather than localStorage.

**Rationale**:
- XSS protection (JavaScript cannot access httpOnly cookies)
- Automatic attachment to requests (no manual header management)
- Better Auth supports this pattern natively

**Alternatives Rejected**:
- localStorage: Vulnerable to XSS attacks
- sessionStorage: Lost on tab close

### ADR-003: SQLModel over Raw SQLAlchemy

**Decision**: Use SQLModel for ORM layer.

**Rationale**:
- Built-in Pydantic integration for request/response validation
- Type safety between database models and API schemas
- Simpler than maintaining separate SQLAlchemy + Pydantic models

**Alternatives Rejected**:
- Raw SQLAlchemy: Requires separate Pydantic models, more boilerplate
- Prisma: Not Python-native, adds JavaScript dependency

### ADR-004: Better Auth for Frontend Authentication

**Decision**: Use Better Auth library for frontend authentication.

**Rationale**:
- Purpose-built for Next.js App Router
- Handles JWT generation, session management, password hashing
- Reduces custom auth code and security risks

**Alternatives Rejected**:
- NextAuth.js: Heavier, more complex for simple email/password
- Custom implementation: Security risk, more development time

## Integration Points

### Frontend ↔ Backend Communication

```
[Next.js Frontend] --HTTPS--> [FastAPI Backend] --SQL--> [Neon PostgreSQL]
       |                              |
   Better Auth                  JWT Validation
   (generates JWT)              (verifies JWT)
```

**Flow**:
1. User signs in via Better Auth (frontend)
2. Better Auth issues JWT with `user_id` claim
3. Frontend attaches JWT to all API requests via httpOnly cookie
4. FastAPI middleware validates JWT signature and expiration
5. API extracts `user_id` from JWT for all queries

### CORS Configuration

Backend must allow:
- Origin: `https://your-frontend-domain.com` (production)
- Origin: `http://localhost:3000` (development)
- Credentials: `true` (for httpOnly cookies)
- Methods: `GET, POST, PATCH, DELETE`
- Headers: `Content-Type, Authorization`

## Security Implementation

### Zero-Trust Backend

Every API endpoint (except `/health`) MUST:
1. Extract JWT from `Authorization` header or httpOnly cookie
2. Verify JWT signature using shared secret
3. Check JWT expiration (24-hour window)
4. Extract `user_id` claim for query filtering

### User Isolation (Golden Rule)

All task queries MUST include user filter:

```python
# CORRECT
tasks = session.exec(
    select(Task).where(Task.user_id == current_user.id)
).all()

# INCORRECT - Never query without user filter
tasks = session.exec(select(Task)).all()  # SECURITY VIOLATION
```

### Password Security

Better Auth handles:
- bcrypt hashing (cost factor 10+)
- Salt generation per password
- Timing-safe comparison

## Performance Considerations

### Database Indexing

```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

### Connection Pooling

Neon Serverless requires connection pooling for cold start mitigation:

```python
# backend/src/db/session.py
from sqlmodel import create_engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)
```

### Optimistic UI Updates

Frontend should update UI immediately on user action, then sync with backend:

```typescript
// Optimistic toggle
setTasks(tasks.map(t => t.id === taskId ? {...t, is_completed: !t.is_completed} : t));
// Then API call
await api.patch(`/tasks/${taskId}`, { is_completed: !task.is_completed });
```

## Testing Strategy

### Backend Tests

| Type | Scope | Tools |
|------|-------|-------|
| Unit | Services, models | pytest, pytest-mock |
| Integration | API endpoints | pytest, httpx, TestClient |
| Contract | OpenAPI compliance | schemathesis |

### Frontend Tests

| Type | Scope | Tools |
|------|-------|-------|
| Unit | Components | Jest, React Testing Library |
| Integration | User flows | Playwright |
| E2E | Full stack | Playwright |

### Security Tests

- JWT expiration handling
- User isolation (cross-user access attempts)
- SQL injection prevention
- XSS prevention

## Deployment Considerations

### Environment Variables

**Backend** (`.env`):
```
DATABASE_URL=postgresql://...@neon.tech/...
JWT_SECRET=<32-byte-random>
CORS_ORIGINS=https://frontend.com
```

**Frontend** (`.env.local`):
```
NEXT_PUBLIC_API_URL=https://api.yourapp.com
BETTER_AUTH_SECRET=<32-byte-random>
```

### Production Checklist

- [ ] HTTPS enforced on both frontend and backend
- [ ] JWT_SECRET and BETTER_AUTH_SECRET are unique, secure values
- [ ] CORS_ORIGINS restricted to production frontend domain
- [ ] Database connection uses SSL
- [ ] Error messages do not leak sensitive information
