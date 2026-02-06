# Data Model: Error Handling and Stability Improvements

**Feature**: Error Handling and Stability Improvements
**Date**: 2026-01-03
**Status**: Complete

## Overview

This feature does NOT introduce new database tables. It only adds TypeScript type definitions for error handling state management in the frontend.

---

## Type Definitions (Frontend)

### ErrorState<T>

Represents the state of an asynchronous operation (API call) with loading, success, and error states.

**Purpose**: Provide type-safe state management for API calls across all frontend components.

**Attributes**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | `T \| null` | Yes | The successfully loaded data, or null if not loaded yet or error occurred |
| `isLoading` | `boolean` | Yes | True while API request is in progress, false otherwise |
| `error` | `string \| null` | Yes | Error message if request failed, null otherwise |

**State Transitions**:
```
Initial State:    { data: null, isLoading: false, error: null }
                                    ↓
Loading State:    { data: null, isLoading: true, error: null }
                                    ↓
                          ┌─────────┴──────────┐
                          ↓                    ↓
Success State:  { data: T, isLoading: false, error: null }
                          OR
Error State:    { data: null, isLoading: false, error: "message" }
```

**TypeScript Definition**:
```typescript
export interface ErrorState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}
```

**Usage Example**:
```typescript
const [categoriesState, setCategoriesState] = useState<ErrorState<Category[]>>({
  data: null,
  isLoading: true,
  error: null
});
```

---

### RetryConfig

Configuration for retry logic in backend database connections.

**Purpose**: Define retry behavior for database connection attempts.

**Attributes**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `maxRetries` | `number` | Yes | Maximum number of retry attempts (default: 3) |
| `baseDelay` | `number` | Yes | Base delay in seconds for exponential backoff (default: 1) |
| `timeout` | `number` | Yes | Connection timeout per attempt in seconds (default: 10) |

**Exponential Backoff Calculation**:
```
Attempt 1: delay = baseDelay * 2^(0) = 1 second
Attempt 2: delay = baseDelay * 2^(1) = 2 seconds
Attempt 3: delay = baseDelay * 2^(2) = 4 seconds
```

**Python Definition** (backend/src/db/session.py):
```python
from dataclasses import dataclass

@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: int = 1  # seconds
    timeout: int = 10     # seconds
```

---

### ComponentErrorProps

Props interface for components that need error handling capabilities.

**Purpose**: Standardize error handling props across reusable components.

**Attributes**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `onError` | `(error: Error) => void` | No | Callback function when error occurs |
| `onRetry` | `() => void` | No | Callback function when retry button is clicked |
| `fallbackMessage` | `string` | No | Custom error message to display (overrides default) |

**TypeScript Definition**:
```typescript
export interface ComponentErrorProps {
  onError?: (error: Error) => void;
  onRetry?: () => void;
  fallbackMessage?: string;
}
```

---

## Validation Rules

### Error Message Validation
- Error messages MUST NOT contain technical stack traces or error codes
- Error messages MUST be under 200 characters for UI display
- Error messages MUST provide actionable guidance when possible

### Retry Logic Validation
- `maxRetries` MUST be between 1 and 5 (prevent infinite loops or excessive delays)
- `baseDelay` MUST be between 0.5 and 5 seconds (prevent too fast or too slow retries)
- `timeout` MUST be between 5 and 30 seconds (balance responsiveness vs reliability)

---

## State Machines

### API Call State Machine

```
┌─────────────┐
│   IDLE      │
│ data: null  │
└──────┬──────┘
       │ fetchData()
       ↓
┌─────────────┐
│  LOADING    │
│isLoading: T │
└──────┬──────┘
       │
   ┌───┴───┐
   ↓       ↓
┌──────┐ ┌──────┐
│SUCCESS│ │ERROR │
│data: T│ │err: │
└───┬───┘ └──┬───┘
    │        │
    │        │ retry()
    │        ↓
    │    ┌────────┐
    │    │LOADING │
    │    └────────┘
    │        │
    └────────┴──────→ ┌────────┐
                      │ IDLE   │
                      │ (reset)│
                      └────────┘
```

### Database Connection State Machine

```
┌────────────────┐
│ DISCONNECTED   │
└────────┬───────┘
         │ attempt 1
         ↓
┌────────────────┐
│  CONNECTING    │
└────────┬───────┘
         │
    ┌────┴────┐
    ↓         ↓
┌────────┐ ┌──────────┐
│CONNECTED│ │ FAILED   │
│        │ │attempt 1 │
└────────┘ └─────┬────┘
              │ wait 1s
              ↓
         ┌──────────┐
         │RETRYING  │
         │attempt 2 │
         └─────┬────┘
            ┌──┴──┐
            ↓     ↓
      ┌────────┐ ┌──────────┐
      │CONNECTED│ │ FAILED   │
      └────────┘ │attempt 2 │
                 └─────┬────┘
                    │ wait 2s
                    ↓
              ┌──────────┐
              │RETRYING  │
              │attempt 3 │
              └─────┬────┘
                 ┌──┴──┐
                 ↓     ↓
           ┌────────┐ ┌──────────────┐
           │CONNECTED│ │ FATAL_ERROR  │
           └────────┘ │ exit(1)      │
                      └──────────────┘
```

---

## Relationships

**No database relationships** - this feature only adds client-side type definitions.

**Component Dependencies**:
- `TagInput.tsx` uses `ErrorState<Tag[]>`
- `TaskFilters.tsx` uses `ErrorState<Category[]>` and `ErrorState<Tag[]>`
- `TaskForm.tsx` uses `ErrorState<Category[]>`
- All components using `ErrorState` can optionally implement `ComponentErrorProps`

---

## Migration Notes

**Database Migrations**: NONE - no schema changes required.

**Type Migration**: Add new TypeScript interfaces to `frontend/types/index.ts` without removing existing types (backward compatible).

**Runtime Migration**: No migration needed - error states initialize with safe defaults.
