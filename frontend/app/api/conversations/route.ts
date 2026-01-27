/**
 * Conversations API Proxy
 * Forwards requests to the Python FastAPI backend
 */

import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { SignJWT } from "jose";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const JWT_SECRET = process.env.BETTER_AUTH_SECRET;
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

export async function GET() {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session?.user?.id) {
      return new Response(
        JSON.stringify({ error: "Authentication required" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    const backendToken = await createBackendToken(session.user.id);

    const response = await fetchWithTimeout(`${BACKEND_URL}/api/chat/conversations`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
      },
    });

    if (!response.ok) {
      console.error("Backend error:", response.status);
      return new Response(
        JSON.stringify({ error: "Failed to fetch conversations" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();

    // Backend returns {"conversations": [...]}
    // Transform backend response to match frontend expectations
    const backendConversations = data.conversations || [];
    const conversations = backendConversations.map((conv: any) => ({
      id: conv.id,
      created_at: conv.created_at || new Date().toISOString(),
      updated_at: conv.updated_at || conv.created_at || new Date().toISOString(),
      preview: conv.preview || null,
    }));

    return new Response(
      JSON.stringify({ conversations }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching conversations:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch conversations" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function POST() {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session?.user?.id) {
      return new Response(
        JSON.stringify({ error: "Authentication required" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    const backendToken = await createBackendToken(session.user.id);

    const response = await fetchWithTimeout(`${BACKEND_URL}/api/chat/conversations`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.error("Backend error:", response.status);
      return new Response(
        JSON.stringify({ error: "Failed to create conversation" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();

    return new Response(
      JSON.stringify({
        id: data.id,
        title: "New Chat",
        updatedAt: data.created_at || new Date().toISOString(),
      }),
      { status: 201, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error creating conversation:", error);
    return new Response(
      JSON.stringify({ error: "Failed to create conversation" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
