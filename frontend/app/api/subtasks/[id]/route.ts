/**
 * Individual Subtask API Proxy
 * Forwards requests to the Python FastAPI backend
 */

import { getUserId, createBackendToken } from "@/lib/api-auth";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * PATCH /api/subtasks/{id}
 * Update a subtask's title, completion status, or order
 */
export async function PATCH(
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

    const response = await fetch(`${BACKEND_URL}/api/subtasks/${id}`, {
      method: "PATCH",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to update subtask" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error updating subtask:", error);
    return new Response(
      JSON.stringify({ error: "Failed to update subtask" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

/**
 * DELETE /api/subtasks/{id}
 * Permanently delete a subtask
 */
export async function DELETE(
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

    const response = await fetch(`${BACKEND_URL}/api/subtasks/${id}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
      },
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to delete subtask" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    return new Response(null, { status: 204 });
  } catch (error) {
    console.error("Error deleting subtask:", error);
    return new Response(
      JSON.stringify({ error: "Failed to delete subtask" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
