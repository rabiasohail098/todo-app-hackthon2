/**
 * Category Statistics API Proxy
 */

import { getUserId, createBackendToken } from "@/lib/api-auth";

// Use BACKEND_API_URL for server-side API forwarding (internal container communication)
// Falls back to NEXT_PUBLIC_API_URL for backward compatibility, then localhost
const BACKEND_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

    const response = await fetch(`${BACKEND_URL}/api/statistics/categories`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
      },
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: "Failed to fetch category statistics" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching category statistics:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch category statistics" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
