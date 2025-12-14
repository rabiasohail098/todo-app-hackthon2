/**
 * TypeScript interfaces matching backend Pydantic models.
 *
 * These types ensure type safety between frontend and backend.
 */

/**
 * Base task fields (shared between Task and TaskCreate).
 */
export interface TaskBase {
  title: string;
  description?: string | null;
  is_completed?: boolean;
}

/**
 * Task entity as returned from the API.
 */
export interface Task extends TaskBase {
  id: number;
  user_id: string; // UUID as string
  created_at: string; // ISO 8601 datetime string
  is_completed: boolean; // Required in read model
}

/**
 * Task creation request payload.
 */
export interface TaskCreate extends TaskBase {
  // user_id is NOT included - it comes from JWT token
  // is_completed defaults to false on backend
}

/**
 * Task update request payload (all fields optional for PATCH).
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  is_completed?: boolean;
}

/**
 * User entity (Better Auth managed).
 */
export interface User {
  id: string; // UUID as string
  email: string;
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string
}

/**
 * Form validation error.
 */
export interface FormError {
  field: string; // Field name or "general" for non-field errors
  message: string;
}

/**
 * API error response.
 */
export interface ApiErrorResponse {
  detail: string;
  status_code?: number;
}
