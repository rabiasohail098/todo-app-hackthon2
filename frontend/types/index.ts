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
 * Tag entity (Phase 4).
 */
export interface Tag {
  id: number;
  name: string;
}

/**
 * Task entity as returned from the API.
 */
export interface Task extends TaskBase {
  id: number;
  user_id: string; // UUID as string
  created_at: string; // ISO 8601 datetime string
  is_completed: boolean; // Required in read model
  category_id?: number | null;
  priority?: string | null;
  due_date?: string | null;
  tags?: Tag[];
  recurrence_pattern?: string | null;
  next_recurrence_date?: string | null;
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

/**
 * Subtask entity (Phase 4).
 */
export interface Subtask {
  id: number;
  parent_task_id: number;
  title: string;
  is_completed: boolean;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface SubtaskCreate {
  title: string;
  is_completed?: boolean;
  order?: number;
}

/**
 * Generic error state interface for async operations (API calls).
 *
 * Represents the three possible states of an asynchronous operation:
 * - Loading: isLoading=true, data=null, error=null
 * - Success: isLoading=false, data=T, error=null
 * - Error: isLoading=false, data=null, error=string
 *
 * @template T - The type of data being loaded
 *
 * @example
 * ```ts
 * const [state, setState] = useState<ErrorState<Category[]>>({
 *   data: null,
 *   isLoading: true,
 *   error: null
 * });
 *
 * // On success:
 * setState({ data: categories, isLoading: false, error: null });
 *
 * // On error:
 * setState({ data: null, isLoading: false, error: "Failed to load categories" });
 * ```
 */
export interface ErrorState<T> {
  /** The successfully loaded data, or null if not loaded yet or error occurred */
  data: T | null;
  /** True while API request is in progress, false otherwise */
  isLoading: boolean;
  /** Error message if request failed, null otherwise */
  error: string | null;
}

/**
 * Props interface for components that need error handling capabilities.
 *
 * Provides optional callbacks for error handling and retry functionality.
 *
 * @example
 * ```ts
 * interface MyComponentProps extends ComponentErrorProps {
 *   userId: string;
 * }
 *
 * function MyComponent({ userId, onError, onRetry }: MyComponentProps) {
 *   const handleFetch = async () => {
 *     try {
 *       // fetch logic
 *     } catch (error) {
 *       onError?.(error as Error);
 *     }
 *   };
 *
 *   return (
 *     <div>
 *       {error && <button onClick={onRetry}>Retry</button>}
 *     </div>
 *   );
 * }
 * ```
 */
export interface ComponentErrorProps {
  /** Callback function when error occurs */
  onError?: (error: Error) => void;
  /** Callback function when retry button is clicked */
  onRetry?: () => void;
  /** Custom error message to display (overrides default) */
  fallbackMessage?: string;
}
