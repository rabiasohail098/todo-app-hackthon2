/**
 * Tags API Proxy
 * Forwards tag requests to the Python FastAPI backend
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
 * GET /api/tags
 * Get all tags for the authenticated user
 */
export async function GET(req: Request) {
  try {
    const userId = await getUserId();

    if (!userId) {
      return new Response(
        JSON.stringify({ error: "Authentication required" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    const backendToken = await createBackendToken(userId);

    // Forward query parameters
    const url = new URL(req.url);
    const queryParams = url.searchParams.toString();

    const response = await fetchWithTimeout(
      `${BACKEND_URL}/api/tags${queryParams ? `?${queryParams}` : ""}`,
      {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${backendToken}`,
        },
      }
    );

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to fetch tags" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching tags:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch tags" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

/**
 * POST /api/tags
 * Create a new tag
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

    const response = await fetchWithTimeout(`${BACKEND_URL}/api/tags`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to create tag" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { status: 201, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error creating tag:", error);
    return new Response(
      JSON.stringify({ error: "Failed to create tag" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
