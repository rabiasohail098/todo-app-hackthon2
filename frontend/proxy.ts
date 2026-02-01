import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Middleware for route protection.
 *
 * Protects /dashboard route by checking for authentication.
 * Redirects unauthenticated users to sign-in page.
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if accessing protected dashboard route
  if (pathname.startsWith("/dashboard")) {
    // Check for authentication token in cookies
    const authToken = request.cookies.get("better-auth.session_token");

    // If no auth token, redirect to sign-in
    if (!authToken) {
      const signInUrl = new URL("/auth/sign-in", request.url);
      // Add redirect parameter to return to dashboard after sign-in
      signInUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(signInUrl);
    }
  }

  // Allow request to proceed
  return NextResponse.next();
}

/**
 * Configure which routes this middleware should run on.
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes (/api/*)
     * - static files (/_next/static/*)
     * - images (/_next/image/*)
     * - favicon and other static assets
     */
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)"
  ],
};
