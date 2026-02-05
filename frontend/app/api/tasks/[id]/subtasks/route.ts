/**
 * Subtasks API Proxy
 * Forwards subtask requests to the Python FastAPI backend
 */

import { getUserId, createBackendToken } from "@/lib/api-auth";

// Use BACKEND_API_URL for server-side API forwarding (internal container communication)
// Falls back to NEXT_PUBLIC_API_URL for backward compatibility, then localhost
const BACKEND_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * GET /api/tasks/{id}/subtasks
 * Get all subtasks for a parent task
 */
export async function GET(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    const userId = await getUserId();

    if (!userId) {
      return new Response(
        JSON.stringify({ error: "Authentication required" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    const backendToken = await createBackendToken(userId);

    const response = await fetch(`${BACKEND_URL}/api/tasks/${id}/subtasks`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
      },
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to fetch subtasks" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching subtasks:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch subtasks" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

/**
 * POST /api/tasks/{id}/subtasks
 * Create a new subtask for a parent task
 */
export async function POST(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    const userId = await getUserId();

    if (!userId) {
      return new Response(
        JSON.stringify({ error: "Authentication required" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    const backendToken = await createBackendToken(userId);
    const body = await req.json();

    const response = await fetch(`${BACKEND_URL}/api/tasks/${id}/subtasks`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to create subtask" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { status: 201, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error creating subtask:", error);
    return new Response(
      JSON.stringify({ error: "Failed to create subtask" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
