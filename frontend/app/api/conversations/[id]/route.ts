/**
 * Conversation Management API
 * Handles individual conversation operations (delete, get)
 */

import { NextRequest } from "next/server";
import { getUserId, createBackendToken } from "@/lib/api-auth";

// Use BACKEND_API_URL for server-side API forwarding (internal container communication)
// Falls back to NEXT_PUBLIC_API_URL for backward compatibility, then localhost
const BACKEND_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * DELETE /api/conversations/[id] - Delete a conversation
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: conversationId } = await params;

    const userId = await getUserId();

    if (!userId) {
      return new Response(
        JSON.stringify({ error: "Authentication required. Please sign in." }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    // Create JWT token for backend
    const backendToken = await createBackendToken(userId);

    // Forward delete request to backend
    const backendResponse = await fetch(
      `${BACKEND_URL}/api/chat/conversations/${conversationId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${backendToken}`,
        },
      }
    );

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error("=== BACKEND ERROR (Delete Conversation) ===");
      console.error("URL:", `${BACKEND_URL}/api/chat/conversations/${conversationId}`);
      console.error("Status:", backendResponse.status);
      console.error("Error:", errorText);
      console.error("=========================================");

      let errorMessage = "Failed to delete conversation";
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorJson.error || errorMessage;
      } catch {
        errorMessage = errorText || errorMessage;
      }

      return new Response(JSON.stringify({ error: errorMessage, detail: errorText }), {
        status: backendResponse.status,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Return success (204 No Content)
    return new Response(null, { status: 204 });
  } catch (error: unknown) {
    console.error("Delete Conversation API Error:", error);
    const errorMessage =
      error instanceof Error ? error.message : "Internal server error";
    return new Response(JSON.stringify({ error: errorMessage }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}

/**
 * GET /api/conversations/[id] - Get a specific conversation
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: conversationId } = await params;

    const userId = await getUserId();

    if (!userId) {
      return new Response(
        JSON.stringify({ error: "Authentication required. Please sign in." }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    // Create JWT token for backend
    const backendToken = await createBackendToken(userId);

    // Forward request to backend
    const backendResponse = await fetch(
      `${BACKEND_URL}/api/chat/conversations/${conversationId}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${backendToken}`,
        },
      }
    );

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error("Backend error:", backendResponse.status, errorText);
      return new Response(
        JSON.stringify({ error: "Failed to fetch conversation" }),
        {
          status: backendResponse.status,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    const data = await backendResponse.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error: unknown) {
    console.error("Get Conversation API Error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
