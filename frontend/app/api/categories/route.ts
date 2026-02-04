/**
 * Categories API Proxy
 * Forwards requests to the Python FastAPI backend
 */

import { getUserId, createBackendToken } from "@/lib/api-auth";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const FETCH_TIMEOUT = 30000; // 30 seconds

// Helper to create fetch with timeout
function fetchWithTimeout(url: string, options: RequestInit, timeout: number = FETCH_TIMEOUT): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  return fetch(url, {
    ...options,
    signal: controller.signal,
  }).finally(() => clearTimeout(timeoutId));
}

/**
 * GET /api/categories - List all categories for the authenticated user
 */
export async function GET() {
  try {
    const userId = await getUserId();

    if (!userId) {
      return new Response(
        JSON.stringify({ error: "Authentication required" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    const backendToken = await createBackendToken(userId);

    const response = await fetchWithTimeout(`${BACKEND_URL}/api/categories`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
      },
    });

    if (!response.ok) {
      console.error("Backend error:", response.status);
      return new Response(
        JSON.stringify({ error: "Failed to fetch categories" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching categories:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch categories" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

/**
 * POST /api/categories - Create a new category
 */
export async function POST(req: Request) {
  try {
    const userId = await getUserId();

    if (!userId) {
      return new Response(
        JSON.stringify({ error: "Authentication required" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    const backendToken = await createBackendToken(userId);
    const body = await req.json();

    const response = await fetchWithTimeout(`${BACKEND_URL}/api/categories`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Backend error:", response.status, errorText);
      return new Response(
        JSON.stringify({ error: "Failed to create category" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { status: 201, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error creating category:", error);
    return new Response(
      JSON.stringify({ error: "Failed to create category" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
