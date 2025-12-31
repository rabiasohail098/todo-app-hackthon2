/**
 * Conversation Messages API Proxy
 * Forwards requests to the Python FastAPI backend for conversation messages
 */

import { NextRequest } from "next/server";
import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { SignJWT } from "jose";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const JWT_SECRET = process.env.BETTER_AUTH_SECRET;

// Create a JWT token for the backend
async function createBackendToken(userId: string): Promise<string> {
  if (!JWT_SECRET) {
    throw new Error("BETTER_AUTH_SECRET is not set");
  }

  const secret = new TextEncoder().encode(JWT_SECRET);

  const token = await new SignJWT({ sub: userId })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("24h")
    .sign(secret);

  return token;
}

/**
 * GET /api/conversations/[id]/messages - Get all messages from a conversation
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: conversationId } = await params;

    // Get session from better-auth
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session?.user?.id) {
      return new Response(
        JSON.stringify({ error: "Authentication required" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    // Create JWT token for backend
    const backendToken = await createBackendToken(session.user.id);

    // Forward request to backend
    const backendResponse = await fetch(
      `${BACKEND_URL}/api/chat/conversations/${conversationId}/messages`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${backendToken}`,
        },
      }
    );

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error("=== BACKEND ERROR (Load Messages) ===");
      console.error("URL:", `${BACKEND_URL}/api/chat/conversations/${conversationId}/messages`);
      console.error("Status:", backendResponse.status);
      console.error("Error:", errorText);
      console.error("=================================");
      return new Response(
        JSON.stringify({ error: "Failed to fetch conversation messages", detail: errorText }),
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
    console.error("Get Conversation Messages API Error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
