/**
 * Statistics API Proxy
 * Forwards statistics requests to the Python FastAPI backend
 */

import { getUserId, createBackendToken } from "@/lib/api-auth";

// Use BACKEND_API_URL for server-side API forwarding (internal container communication)
// Falls back to NEXT_PUBLIC_API_URL for backward compatibility, then localhost
const BACKEND_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * GET /api/statistics
 * Get overall task statistics
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

    // Forward query parameters from request URL
    const url = new URL(req.url);
    const queryParams = url.searchParams.toString();

    const response = await fetch(
      `${BACKEND_URL}/api/statistics${queryParams ? `?${queryParams}` : ""}`,
      {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${backendToken}`,
        },
      }
    );

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to fetch statistics" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching statistics:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch statistics" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
