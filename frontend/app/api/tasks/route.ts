/**
 * Tasks API Proxy
 * Forwards requests to the Python FastAPI backend
 */

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

export async function GET(req: Request) {
  try {
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

    const backendToken = await createBackendToken(session.user.id);

    // Extract query parameters from request URL
    const { searchParams } = new URL(req.url);
    const queryString = searchParams.toString();

    // Build backend URL with query parameters
    const backendUrl = `${BACKEND_URL}/api/tasks${queryString ? `?${queryString}` : ""}`;

    const response = await fetch(backendUrl, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${backendToken}`,
      },
    });

    if (!response.ok) {
      console.error("Backend error:", response.status);
      return new Response(
        JSON.stringify({ error: "Failed to fetch tasks" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching tasks:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch tasks" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function POST(req: Request) {
  try {
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

    const backendToken = await createBackendToken(session.user.id);
    const body = await req.json();

    const response = await fetch(`${BACKEND_URL}/api/tasks`, {
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
        JSON.stringify({ error: "Failed to create task" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    return new Response(
      JSON.stringify(data),
      { status: 201, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error creating task:", error);
    return new Response(
      JSON.stringify({ error: "Failed to create task" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
