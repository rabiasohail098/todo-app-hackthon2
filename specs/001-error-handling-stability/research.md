# Research: Error Handling and Stability Improvements

**Feature**: Error Handling and Stability Improvements
**Date**: 2026-01-03
**Status**: Complete

## Overview

This document consolidates research findings for implementing robust error handling and eliminating stability issues (infinite render loops, network error crashes) in the Todo application.

---

## Decision 1: React useEffect Dependency Array Fixes

**Context**: Components like TagInput, TaskFilters, and TaskForm are causing infinite render loops due to incorrect useEffect dependency arrays.

**Decision**: Use empty dependency array `[]` for effects that should run only on mount, and explicitly include all used variables in effects that should re-run.

**Rationale**:
- React's exhaustive-deps ESLint rule requires all variables used inside useEffect to be in the dependency array
- However, for mount-only effects (like initial data fetching), an empty array prevents infinite loops
- The pattern `useEffect(() => { fetchData(); }, [])` is correct for one-time data loading

**Alternatives Considered**:
1. ❌ **useCallback for all functions**: Would require wrapping fetch functions in useCallback, adding complexity
2. ❌ **Moving fetch functions outside component**: Would prevent access to component state/props
3. ✅ **Empty dependency array for mount-only effects**: Standard React pattern, simple and effective

**Implementation**:
```typescript
// ✅ CORRECT: Fetch only on mount
useEffect(() => {
  fetchCategories();
  fetchTags();
}, []); // Empty array = run once on mount

// ❌ WRONG: Would cause infinite loop
useEffect(() => {
  fetchCategories();
}); // No dependency array = runs on every render

// ❌ WRONG: Would cause infinite loop if onFilterChange recreates every render
useEffect(() => {
  onFilterChange(filters);
}, [filters, onFilterChange]); // onFilterChange changes = infinite loop
```

---

## Decision 2: Error State Pattern for API Calls

**Context**: Components need to handle API failures gracefully with loading states, error messages, and retry buttons.

**Decision**: Implement a three-state pattern (loading/success/error) with React state hooks.

**Rationale**:
- Three explicit states (loading, success with data, error with message) cover all API call scenarios
- State machines are a well-established pattern for async operations
- Provides clear UI feedback to users

**Alternatives Considered**:
1. ❌ **React Query library**: Adds new dependency (violates constraint)
2. ❌ **SWR library**: Adds new dependency (violates constraint)
3. ✅ **Manual state management**: Uses existing React hooks, no new dependencies

**Implementation**:
```typescript
interface ComponentState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

const [state, setState] = useState<ComponentState<Category[]>>({
  data: null,
  isLoading: true,
  error: null
});

const fetchData = async () => {
  setState({ data: null, isLoading: true, error: null });
  try {
    const response = await fetch('/api/categories');
    if (!response.ok) throw new Error('Failed to load');
    const data = await response.json();
    setState({ data, isLoading: false, error: null });
  } catch (err) {
    setState({ data: null, isLoading: false, error: err.message });
  }
};
```

---

## Decision 3: Database Connection Retry Strategy

**Context**: Backend fails to start when Neon PostgreSQL has temporary connection issues (cold starts, network latency).

**Decision**: Implement exponential backoff retry logic with max 3 attempts (delays: 1s, 2s, 4s).

**Rationale**:
- Exponential backoff prevents overwhelming the database with retry requests
- 3 attempts balance reliability (handles transient issues) with fail-fast (doesn't hang indefinitely)
- Total timeout ~7 seconds is acceptable for startup (within 15-second success criterion)

**Alternatives Considered**:
1. ❌ **Immediate retries**: Could overwhelm database, worsen connection issues
2. ❌ **Linear backoff (1s, 1s, 1s)**: Less effective at avoiding thundering herd problem
3. ❌ **Infinite retries**: Would hang server startup indefinitely on persistent failures
4. ✅ **Exponential backoff (1s, 2s, 4s)**: Industry standard, balances reliability and fail-fast

**Implementation** (Python):
```python
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

def connect_with_retry(database_url: str, max_retries: int = 3):
    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(database_url, connect_args={"connect_timeout": 10})
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"✅ Database connected (attempt {attempt})")
            return engine
        except OperationalError as e:
            if attempt < max_retries:
                delay = 2 ** (attempt - 1)  # 1s, 2s, 4s
                logger.warning(f"⚠️ Database connection failed (attempt {attempt}/{max_retries}). Retrying in {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"❌ Database connection failed after {max_retries} attempts. Check DATABASE_URL.")
                raise
```

---

## Decision 4: User-Friendly Error Messages

**Context**: Current error messages expose technical details (stack traces, HTTP status codes) confusing users.

**Decision**: Map technical errors to user-friendly messages with actionable guidance.

**Rationale**:
- Users don't understand HTTP 500 or "ECONNREFUSED"
- Actionable messages ("Check your connection" vs "Network error") improve UX
- Security best practice: don't expose internal implementation details

**Error Message Mapping**:
| Technical Error | User-Friendly Message | Actionable Guidance |
|----------------|----------------------|---------------------|
| `fetch failed`, `ECONNREFUSED` | "Unable to connect to server" | "Please check your internet connection and try again." |
| `HTTP 500` | "Something went wrong" | "We're working on it. Please try again in a few minutes." |
| `HTTP 401` | "Not authenticated" | "Please sign in to continue." |
| `HTTP 404` | "Not found" | "The requested item could not be found." |
| `HTTP 422` | "Invalid input" | "Please check your input and try again." |

**Implementation** (TypeScript):
```typescript
function getUser FriendlyErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    if (error.message.includes('fetch failed') || error.message.includes('ECONNREFUSED')) {
      return 'Unable to connect to server. Please check your connection.';
    }
    if (error.message.includes('500')) {
      return 'Something went wrong on our end. Please try again later.';
    }
  }
  return 'An unexpected error occurred. Please try again.';
}
```

---

## Decision 5: Retry Button Pattern

**Context**: Users need ability to manually retry failed requests without refreshing the entire page.

**Decision**: Show "Retry" button in error states that re-invokes the same fetch function.

**Rationale**:
- Gives users control and reduces frustration
- Avoids full page refresh (better UX)
- Standard pattern in modern web apps (Gmail, Twitter, etc.)

**Implementation**:
```typescript
{state.error && (
  <div className="error-state">
    <p>{state.error}</p>
    <button onClick={fetchData} disabled={state.isLoading}>
      {state.isLoading ? 'Retrying...' : 'Retry'}
    </button>
  </div>
)}
```

---

## Decision 6: Environment Variable Validation

**Context**: Missing environment variables (DATABASE_URL, JWT_SECRET) cause cryptic errors during runtime.

**Decision**: Validate all required environment variables on application startup and fail fast with clear messages.

**Rationale**:
- Fail-fast principle: better to crash immediately with clear error than partially work
- Easier debugging: error message includes variable name and fix instructions
- Prevents security issues: missing JWT_SECRET would silently break authentication

**Implementation** (Python):
```python
# backend/src/api/main.py
from dotenv import load_dotenv
import os
import sys

load_dotenv()

REQUIRED_ENV_VARS = ["DATABASE_URL", "JWT_SECRET", "CORS_ORIGINS"]

for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        print(f"❌ ERROR: {var} environment variable is not set", file=sys.stderr)
        print(f"Fix: Add {var}=your-value to your .env file", file=sys.stderr)
        sys.exit(1)
```

---

## Summary

All decisions prioritize:
1. **Simplicity**: Use existing patterns and libraries (no new dependencies)
2. **User Experience**: Clear error messages, loading states, retry functionality
3. **Reliability**: Proper error handling prevents crashes and infinite loops
4. **Fail-Fast**: Validate configuration early to catch issues during development

These choices align with the project's constitution (Principle VI: User Experience, Principle XII: Observability) and technical constraints (no new dependencies, maintain backward compatibility).
