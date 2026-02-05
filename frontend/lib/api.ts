/**
 * API client wrapper with automatic JWT token attachment.
 *
 * This module provides a fetch wrapper that automatically includes
 * the Authorization header with the JWT token from Better Auth session.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Log API_URL for debugging (FR-019: The default API_URL MUST be logged to console)
if (typeof window !== 'undefined') {
  console.log(`[API] Using API URL: ${API_URL}`);
}

/**
 * API request options extending standard fetch options.
 */
export interface ApiRequestOptions extends RequestInit {
  /** Skip automatic token attachment */
  skipAuth?: boolean;
}

/**
 * API error class for structured error handling.
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any
  ) {
    super(`API Error ${status}: ${statusText}`);
    this.name = "ApiError";
  }
}

/**
 * Get user ID from localStorage session (HuggingFace fallback).
 *
 * @returns User ID string or null if not authenticated
 */
function getUserIdFromStorage(): string | null {
  if (typeof window === 'undefined') return null;

  try {
    const storedSession = localStorage.getItem("better-auth-session");
    if (storedSession) {
      const session = JSON.parse(storedSession);
      // Check if session is valid (less than 23 hours old to account for clock differences)
      if (session.timestamp && Date.now() - session.timestamp < 23 * 60 * 60 * 1000) {
        return session.user?.id || null;
      }
    }
  } catch (e) {
    console.error("Failed to get user ID from storage:", e);
  }
  return null;
}

/**
 * Make an authenticated API request.
 *
 * Automatically attaches JWT token from Better Auth session
 * to the Authorization header.
 *
 * @param endpoint - API endpoint path (e.g., "/api/tasks")
 * @param options - Fetch options with optional skipAuth flag
 * @returns Promise with parsed JSON response
 * @throws ApiError if request fails
 *
 * @example
 * ```ts
 * // GET request
 * const tasks = await api("/api/tasks");
 *
 * // POST request
 * const newTask = await api("/api/tasks", {
 *   method: "POST",
 *   body: JSON.stringify({ title: "Buy groceries" }),
 * });
 *
 * // Request without authentication
 * const health = await api("/health", { skipAuth: true });
 * ```
 */
export async function api<T = any>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const { skipAuth, ...fetchOptions } = options;

  // Build full URL
  const url = `${API_URL}${endpoint}`;

  // Prepare headers
  const headers = {
    "Content-Type": "application/json",
    ...(fetchOptions.headers || {}),
  } as Record<string, string>;

  // Attach user ID from localStorage (HuggingFace fallback)
  if (!skipAuth) {
    const userId = getUserIdFromStorage();
    if (userId) {
      headers["X-User-Id"] = userId;
    }
  }

  // Make request
  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });

  // Handle non-2xx responses
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = await response.text();
    }

    throw new ApiError(response.status, response.statusText, errorData);
  }

  // Parse and return JSON response
  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

/**
 * Convenience methods for common HTTP verbs.
 */
export const apiClient = {
  /**
   * GET request
   */
  get: <T = any>(endpoint: string, options?: ApiRequestOptions) =>
    api<T>(endpoint, { ...options, method: "GET" }),

  /**
   * POST request
   */
  post: <T = any>(
    endpoint: string,
    data?: any,
    options?: ApiRequestOptions
  ) =>
    api<T>(endpoint, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),

  /**
   * PATCH request
   */
  patch: <T = any>(
    endpoint: string,
    data?: any,
    options?: ApiRequestOptions
  ) =>
    api<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    }),

  /**
   * DELETE request
   */
  delete: <T = any>(endpoint: string, options?: ApiRequestOptions) =>
    api<T>(endpoint, { ...options, method: "DELETE" }),
};

/**
 * Authenticated fetch wrapper for Next.js API routes.
 *
 * On HuggingFace Spaces, cookies may be stripped by the reverse proxy.
 * This wrapper attaches the X-User-Id header from localStorage so
 * server-side API routes can identify the user via the header fallback.
 */
export async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };

  // Attach user ID from localStorage for HuggingFace fallback
  const userId = getUserIdFromStorage();
  if (userId) {
    headers["X-User-Id"] = userId;
  }

  // Also try to get session token and add to Authorization header as fallback
  const sessionData = await getSessionFromStorage();
  if (sessionData?.token) {
    headers["Authorization"] = `Bearer ${sessionData.token}`;
  }

  return fetch(url, {
    ...options,
    headers,
    credentials: "include",
  });
}

/**
 * Get session data from localStorage with validation.
 *
 * @returns Session data if valid, null otherwise
 */
async function getSessionFromStorage(): Promise<{user: any, token: string, timestamp: number} | null> {
  if (typeof window === 'undefined') return null;

  try {
    const storedSession = localStorage.getItem("better-auth-session");
    if (storedSession) {
      const session = JSON.parse(storedSession);

      // Check if session is still valid (less than 23 hours old to account for clock differences)
      if (session.timestamp && Date.now() - session.timestamp < 23 * 60 * 60 * 1000) {
        return session;
      }
    }
  } catch (e) {
    console.error("Failed to get session from storage:", e);
  }
  return null;
}

export default api;
