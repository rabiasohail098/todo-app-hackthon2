/**
 * Individual Category API Proxy
 * Forwards requests to the Python FastAPI backend
 */

import { getUserId, createBackendToken } from "@/lib/api-auth";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * GET /api/categories/[id] - Get a specific category
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

    const response = await fetch(`${BACKEND_URL}/api/categories/${id}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
      },
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Category not found" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching category:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch category" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

/**
 * PUT /api/categories/[id] - Update a category
 */
export async function PUT(
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

    const response = await fetch(`${BACKEND_URL}/api/categories/${id}`, {
      method: "PUT",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to update category" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error updating category:", error);
    return new Response(
      JSON.stringify({ error: "Failed to update category" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

/**
 * DELETE /api/categories/[id] - Delete a category
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

    const response = await fetch(`${BACKEND_URL}/api/categories/${id}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
      },
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to delete category" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    return new Response(null, { status: 204 });
  } catch (error) {
    console.error("Error deleting category:", error);
    return new Response(
      JSON.stringify({ error: "Failed to delete category" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
