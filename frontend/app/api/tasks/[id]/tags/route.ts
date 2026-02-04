/**
 * Task Tags API Proxy
 * Forwards task-tag association requests to the Python FastAPI backend
 */

import { getUserId, createBackendToken } from "@/lib/api-auth";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * GET /api/tasks/{id}/tags
 * Get all tags for a task
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

    const response = await fetch(`${BACKEND_URL}/api/tasks/${id}/tags`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
      },
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to fetch task tags" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching task tags:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch task tags" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

/**
 * POST /api/tasks/{id}/tags
 * Add a tag to a task
 * Body: { tag_id: number }
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
    const tagId = body.tag_id;

    if (!tagId) {
      return new Response(
        JSON.stringify({ error: "tag_id is required" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const response = await fetch(`${BACKEND_URL}/api/tasks/${id}/tags/${tagId}`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to add tag to task" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { status: 201, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error adding tag to task:", error);
    return new Response(
      JSON.stringify({ error: "Failed to add tag to task" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

/**
 * DELETE /api/tasks/{id}/tags
 * Remove a tag from a task
 * Body: { tag_id: number }
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
    const body = await req.json();
    const tagId = body.tag_id;

    if (!tagId) {
      return new Response(
        JSON.stringify({ error: "tag_id is required" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const response = await fetch(`${BACKEND_URL}/api/tasks/${id}/tags/${tagId}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
      },
    });

    if (!response.ok && response.status !== 204) {
      return new Response(
        JSON.stringify({ error: "Failed to remove tag from task" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    return new Response(null, { status: 204 });
  } catch (error) {
    console.error("Error removing tag from task:", error);
    return new Response(
      JSON.stringify({ error: "Failed to remove tag from task" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
