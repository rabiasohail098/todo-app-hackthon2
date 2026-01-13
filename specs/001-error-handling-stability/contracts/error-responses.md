# API Contract: Standardized Error Responses

**Feature**: Error Handling and Stability Improvements
**Date**: 2026-01-03
**Version**: 1.0.0

## Overview

This document defines the standardized error response format for all API endpoints. These contracts ensure consistent error handling between frontend and backend.

---

## Error Response Format

All API errors MUST return a JSON response with the following structure:

```typescript
interface ErrorResponse {
  error: string;          // User-friendly error message
  detail?: string;        // Optional technical details (development only)
  status: number;         // HTTP status code
  timestamp?: string;     // ISO 8601 timestamp (optional)
}
```

**Example**:
```json
{
  "error": "Unable to load tasks. Please try again.",
  "status": 500
}
```

---

## HTTP Status Codes

| Status Code | Meaning | User-Friendly Message | When to Use |
|------------|---------|----------------------|-------------|
| `400` | Bad Request | "Invalid input. Please check your data and try again." | Validation errors, malformed requests |
| `401` | Unauthorized | "Please sign in to continue." | Missing or invalid JWT token |
| `403` | Forbidden | "You don't have permission to access this resource." | User trying to access another user's data |
| `404` | Not Found | "The requested item could not be found." | Task/category/tag doesn't exist |
| `422` | Unprocessable Entity | "Invalid input. Please check the highlighted fields." | Pydantic validation errors |
| `500` | Internal Server Error | "Something went wrong on our end. Please try again later." | Database errors, unexpected exceptions |
| `503` | Service Unavailable | "The service is temporarily unavailable. Please try again in a few minutes." | Database connection failed after retries |

---

## Contract 1: Database Connection Error (503)

**Endpoint**: ALL (affects all endpoints if database is unavailable)

**Scenario**: Database connection fails after all retry attempts.

**Request**: (any API request)
```http
GET /api/tasks HTTP/1.1
Authorization: Bearer <token>
```

**Response**:
```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json

{
  "error": "The service is temporarily unavailable. Please try again in a few minutes.",
  "status": 503
}
```

**Frontend Handling**:
```typescript
if (response.status === 503) {
  showError("The service is temporarily unavailable. Please try again in a few minutes.");
  showRetryButton(true);
}
```

---

## Contract 2: Network/Fetch Error (Client-Side)

**Scenario**: Frontend cannot reach backend (ECONNREFUSED, fetch failed, timeout).

**Request**:
```typescript
const response = await fetch('/api/tasks');
```

**Error** (JavaScript Error object):
```javascript
{
  name: "TypeError",
  message: "fetch failed" // or "Failed to fetch" or "Network request failed"
}
```

**Frontend Handling**:
```typescript
try {
  const response = await fetch('/api/tasks');
  // handle response
} catch (error) {
  if (error instanceof TypeError &&
      (error.message.includes('fetch failed') ||
       error.message.includes('Failed to fetch') ||
       error.message.includes('Network request failed'))) {
    showError("Unable to connect to server. Please check your connection.");
    showRetryButton(true);
  }
}
```

**User-Facing Error**:
```
Unable to connect to server. Please check your connection.
[Retry Button]
```

---

## Contract 3: Validation Error (422)

**Endpoint**: `POST /api/tasks`, `PATCH /api/tasks/:id`

**Scenario**: Request body fails Pydantic validation (e.g., title too long, invalid priority).

**Request**:
```http
POST /api/tasks HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "",  // Empty title (invalid)
  "priority": "super-urgent"  // Invalid priority (not in enum)
}
```

**Response**:
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "error": "Invalid input. Please check the highlighted fields.",
  "detail": "Validation error",
  "errors": [
    {
      "field": "title",
      "message": "Title cannot be empty"
    },
    {
      "field": "priority",
      "message": "Priority must be one of: critical, high, medium, low"
    }
  ],
  "status": 422
}
```

**Frontend Handling**:
```typescript
if (response.status === 422) {
  const data = await response.json();
  // Show field-level validation errors
  data.errors.forEach(err => {
    highlightField(err.field, err.message);
  });
}
```

---

## Contract 4: Authentication Error (401)

**Endpoint**: ALL protected endpoints

**Scenario**: Missing or invalid JWT token.

**Request**:
```http
GET /api/tasks HTTP/1.1
Authorization: Bearer invalid-token
```

**Response**:
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": "Please sign in to continue.",
  "detail": "Invalid or expired token",
  "status": 401
}
```

**Frontend Handling**:
```typescript
if (response.status === 401) {
  clearAuthToken();
  redirectToLogin();
  showError("Your session has expired. Please sign in again.");
}
```

---

## Contract 5: Resource Not Found (404)

**Endpoint**: `GET /api/tasks/:id`, `PATCH /api/tasks/:id`, `DELETE /api/tasks/:id`

**Scenario**: Task/category/tag with specified ID doesn't exist or belongs to another user.

**Request**:
```http
GET /api/tasks/99999 HTTP/1.1
Authorization: Bearer <token>
```

**Response**:
```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "The requested task could not be found.",
  "status": 404
}
```

**Frontend Handling**:
```typescript
if (response.status === 404) {
  showError("The requested item could not be found.");
  // Remove from local state if it was there
  removeFromCache(resourceId);
}
```

---

## Contract 6: Unexpected Server Error (500)

**Endpoint**: ALL

**Scenario**: Unhandled exception in backend code (bug, database query error, etc.).

**Request**: (any valid request)
```http
POST /api/tasks HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Valid task"
}
```

**Response**:
```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "Something went wrong on our end. Please try again later.",
  "status": 500
}
```

**Backend Behavior**:
- Log full stack trace to server logs (for debugging)
- **DO NOT** send stack trace to client (security risk)
- Return generic user-friendly message

**Frontend Handling**:
```typescript
if (response.status === 500) {
  showError("Something went wrong. Please try again later.");
  logErrorToMonitoring(error); // Optional: send to Sentry/LogRocket
}
```

---

## Frontend Error Handling Pattern

**Standard Pattern** (use across all components):

```typescript
interface ErrorState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

async function fetchData(): Promise<void> {
  setState({ data: null, isLoading: true, error: null });

  try {
    const response = await fetch('/api/endpoint');

    if (!response.ok) {
      // Handle HTTP errors
      if (response.status === 401) {
        throw new Error("Please sign in to continue.");
      } else if (response.status === 404) {
        throw new Error("The requested item could not be found.");
      } else if (response.status === 503) {
        throw new Error("The service is temporarily unavailable. Please try again in a few minutes.");
      } else {
        throw new Error("Something went wrong. Please try again later.");
      }
    }

    const data = await response.json();
    setState({ data, isLoading: false, error: null });

  } catch (error) {
    // Handle network errors
    let message = "An unexpected error occurred.";

    if (error instanceof Error) {
      if (error.message.includes('fetch failed') ||
          error.message.includes('Failed to fetch')) {
        message = "Unable to connect to server. Please check your connection.";
      } else {
        message = error.message; // Use our custom error messages
      }
    }

    console.error("Error fetching data:", error); // Log for debugging
    setState({ data: null, isLoading: false, error: message });
  }
}
```

---

## Backend Error Response Pattern

**Standard Pattern** (use in FastAPI exception handlers):

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with user-friendly messages."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": get_user_friendly_message(exc.status_code),
            "status": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    # Log full error for debugging
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Return generic message to client (don't expose internals)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Something went wrong on our end. Please try again later.",
            "status": 500
        }
    )

def get_user_friendly_message(status_code: int) -> str:
    """Map HTTP status codes to user-friendly messages."""
    messages = {
        400: "Invalid input. Please check your data and try again.",
        401: "Please sign in to continue.",
        403: "You don't have permission to access this resource.",
        404: "The requested item could not be found.",
        422: "Invalid input. Please check the highlighted fields.",
        500: "Something went wrong on our end. Please try again later.",
        503: "The service is temporarily unavailable. Please try again in a few minutes."
    }
    return messages.get(status_code, "An error occurred. Please try again.")
```

---

## Testing Contracts

**How to verify each contract**:

1. **503 Service Unavailable**: Set DATABASE_URL to invalid value, start backend, make any API request
2. **Network Error**: Stop backend, refresh frontend, observe error message
3. **422 Validation Error**: Submit task form with empty title
4. **401 Unauthorized**: Remove JWT token from browser storage, make API request
5. **404 Not Found**: Request `/api/tasks/99999` (non-existent ID)
6. **500 Internal Error**: Temporarily break backend code (e.g., divide by zero), make request

---

## Backward Compatibility

**Changes from previous implementation**:
- ❌ REMOVED: Technical error details in production responses
- ❌ REMOVED: Stack traces in error responses
- ✅ ADDED: Consistent `error` field with user-friendly messages
- ✅ ADDED: Standardized status codes across all endpoints
- ✅ MAINTAINED: Existing API endpoints (no breaking changes)
- ✅ MAINTAINED: Request/response formats for success cases

**Migration Guide**:
- Frontend code expecting `{detail: string}` should update to `{error: string}`
- Backend exception handlers should map to user-friendly messages
- Existing success responses are unchanged (no frontend changes needed)

---

## Summary

**Key Principles**:
1. **User-Friendly**: Error messages must be understandable by non-technical users
2. **Actionable**: Messages should guide users on what to do next
3. **Consistent**: All endpoints use the same error format
4. **Secure**: Never expose stack traces, internal paths, or sensitive details
5. **Logged**: All errors are logged server-side for debugging, even if hidden from users

**Implementation Checklist**:
- [ ] All API endpoints return standardized error format
- [ ] Frontend catches both HTTP errors and network errors
- [ ] Error messages are user-friendly (no technical jargon)
- [ ] Retry buttons appear for recoverable errors
- [ ] Server logs include full error details for debugging
- [ ] No stack traces or sensitive info sent to client
