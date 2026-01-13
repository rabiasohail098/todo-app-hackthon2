/**
 * Category Statistics API Proxy
 */

import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { SignJWT } from "jose";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const JWT_SECRET = process.env.BETTER_AUTH_SECRET;

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
