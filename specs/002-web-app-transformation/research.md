# Research: Web Application Transformation

**Feature**: 002-web-app-transformation
**Date**: 2025-12-10

## Research Tasks Completed

### 1. Better Auth Integration with FastAPI Backend

**Decision**: Better Auth handles frontend authentication only; backend verifies JWT independently.

**Rationale**:
- Better Auth is a JavaScript/TypeScript library designed for Next.js
- Backend cannot use Better Auth directly (Python)
- Backend must independently verify JWT using shared secret
- This is the standard pattern for decoupled frontend/backend auth

**Alternatives Considered**:
- Single auth service: Adds complexity, single point of failure
- Backend-only auth: Loses Better Auth's Next.js integration benefits

**Implementation Notes**:
- Frontend: Better Auth generates JWT with `user_id` claim
- Backend: PyJWT library validates JWT signature and extracts claims
- Shared secret must be configured identically in both environments

### 2. Neon PostgreSQL Connection Best Practices

**Decision**: Use SQLAlchemy connection pooling with `pool_pre_ping=True`.

**Rationale**:
- Neon serverless can drop idle connections
- `pool_pre_ping` validates connections before use
- `pool_recycle=300` prevents stale connections
- Neon's connection pooler (PgBouncer) recommended for production

**Alternatives Considered**:
- No pooling: Connection failures on cold starts
- External pooler only: Less control over connection lifecycle

**Implementation Notes**:
```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)
```

### 3. JWT Token Structure and Validation

**Decision**: JWT contains `sub` (user_id), `exp` (expiration), `iat` (issued at).

**Rationale**:
- Standard JWT claims for interoperability
- `sub` (subject) is the conventional claim for user identifier
- 24-hour expiration balances security and UX
- No refresh token in Phase 2 (simplicity)

**Alternatives Considered**:
- Custom claims: Less standard, harder to debug
- Shorter expiration with refresh: More complex implementation

**Implementation Notes**:
```json
{
  "sub": "user_uuid_here",
  "exp": 1702339200,
  "iat": 1702252800
}
```

### 4. Next.js 16+ App Router Patterns

**Decision**: Use Server Components for static content, Client Components for interactive elements.

**Rationale**:
- Server Components reduce JavaScript bundle size
- Client Components needed for state (task list, forms)
- Better Auth requires Client Components for auth state
- Route handlers for API proxying if needed

**Alternatives Considered**:
- All Client Components: Larger bundle, slower initial load
- Pages Router: Older pattern, less optimized

**Implementation Notes**:
- Landing page: Server Component
- Auth pages: Client Components (Better Auth)
- Dashboard: Client Component (interactive task list)

### 5. SQLModel Entity Design

**Decision**: Single `Task` model extending `SQLModel` with Pydantic validation.

**Rationale**:
- SQLModel combines SQLAlchemy table definition with Pydantic validation
- Same model for database operations and API serialization
- Type safety throughout the application

**Alternatives Considered**:
- Separate SQLAlchemy + Pydantic models: More boilerplate, sync issues
- Raw SQL: No type safety, more error-prone

**Implementation Notes**:
```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key="user.id")
    title: str = Field(max_length=200)
    description: str | None = None
    is_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 6. Frontend-Backend Type Synchronization

**Decision**: Manual TypeScript interfaces matching Pydantic models.

**Rationale**:
- Phase 2 scope: Manual sync is sufficient for small schema
- Codegen adds build complexity
- Schema is stable (Task entity only)

**Alternatives Considered**:
- OpenAPI codegen: Adds build step, overkill for 1 entity
- JSON Schema sharing: Complex toolchain

**Implementation Notes**:
```typescript
// frontend/src/types/index.ts
interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string; // ISO 8601
}
```

### 7. CORS Configuration for Cookie-Based Auth

**Decision**: Enable credentials with specific origin allowlist.

**Rationale**:
- httpOnly cookies require `credentials: 'include'` on fetch
- CORS must allow credentials and specify exact origins (no wildcards)
- Development and production origins must be explicitly listed

**Alternatives Considered**:
- `Access-Control-Allow-Origin: *`: Incompatible with credentials
- Bearer token in header: Vulnerable to XSS

**Implementation Notes**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://prod.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)
```

## Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| How does Better Auth integrate with Python backend? | Frontend-only; backend verifies JWT independently |
| Neon connection handling? | SQLAlchemy pooling with pre_ping and recycle |
| JWT claim structure? | Standard claims: sub, exp, iat |
| Next.js component strategy? | Server Components default, Client for interactivity |
| Type sync between frontend/backend? | Manual TypeScript interfaces |

## Remaining Risks

1. **Better Auth JWT Secret Sharing**: Must ensure identical secret in both environments
   - Mitigation: Use environment variable with same name in both
2. **Neon Cold Start Latency**: First request may be slow
   - Mitigation: Connection pooling, monitor in development
3. **CORS Debugging**: Cross-origin issues can be hard to diagnose
   - Mitigation: Test CORS early with actual frontend deployment
