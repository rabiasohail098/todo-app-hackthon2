/**
 * Chat API Proxy
 * Forwards chat requests to the Python FastAPI backend
 */

import { getUserId, createBackendToken } from "@/lib/api-auth";

// Use BACKEND_API_URL for server-side API forwarding (internal container communication)
// Falls back to NEXT_PUBLIC_API_URL for backward compatibility, then localhost
const BACKEND_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const FETCH_TIMEOUT = 60000; // 60 seconds for chat (LLM calls can be slow)

// Helper to create fetch with timeout
function fetchWithTimeout(url: string, options: RequestInit, timeout: number = FETCH_TIMEOUT): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  return fetch(url, {
    ...options,
    signal: controller.signal,
  }).finally(() => clearTimeout(timeoutId));
}

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

    const response = await fetchWithTimeout(`${BACKEND_URL}/api/chat`, {
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

      // Try to parse the error response to get a more specific message
      let errorMessage = "Failed to send message";
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.error || errorJson.detail || "Failed to send message";
      } catch {
        // If parsing fails, use the raw error text if it's not empty
        if (errorText.trim()) {
          errorMessage = errorText;
        }
      }

      return new Response(
        JSON.stringify({ error: errorMessage }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error sending message:", error);
    return new Response(
      JSON.stringify({ error: "Failed to send message" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
