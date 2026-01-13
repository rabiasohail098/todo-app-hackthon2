/**
 * Statistics API Proxy
 * Forwards statistics requests to the Python FastAPI backend
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

/**
 * GET /api/statistics
 * Get overall task statistics
 */
export async function GET(req: Request) {
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
