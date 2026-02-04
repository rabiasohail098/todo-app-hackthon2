/**
 * API Route Authentication Helper
 * Provides user authentication for API routes with HuggingFace fallback
 */

import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { SignJWT } from "jose";

const JWT_SECRET = process.env.BETTER_AUTH_SECRET;

/**
 * Create a JWT token for the backend
 */
export async function createBackendToken(userId: string): Promise<string> {
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
 * Get user ID from session or client-provided header
 * Supports both cookie-based auth and HuggingFace localStorage fallback
 */
export async function getUserId(req?: Request): Promise<string | null> {
  // First, try to get session from better-auth cookies
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    });
    if (session?.user?.id) {
      return session.user.id;
    }
  } catch (e) {
    // Cookie session not available, try header fallback
  }

  // Fallback: Check for X-User-Id header (sent from client with localStorage data)
  const headersList = await headers();
  const userId = headersList.get("x-user-id");
  if (userId) {
    return userId;
  }

  return null;
}

/**
 * Create an unauthorized response
 */
export function unauthorizedResponse(): Response {
  return new Response(
    JSON.stringify({ error: "Authentication required" }),
    { status: 401, headers: { "Content-Type": "application/json" } }
  );
}

/**
 * Create an error response
 */
export function errorResponse(message: string, status: number = 500): Response {
  return new Response(
    JSON.stringify({ error: message }),
    { status, headers: { "Content-Type": "application/json" } }
  );
}

/**
 * Create a success response
 */
export function successResponse(data: unknown, status: number = 200): Response {
  return new Response(
    JSON.stringify(data),
    { status, headers: { "Content-Type": "application/json" } }
  );
}
