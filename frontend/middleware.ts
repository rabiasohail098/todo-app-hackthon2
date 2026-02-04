import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Middleware for route protection.
 *
 * Note: On HuggingFace Spaces, cookies may not work properly due to proxy.
 * Client-side auth checking is used as fallback.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip middleware for API routes and static files
  if (pathname.startsWith("/api") || pathname.startsWith("/_next")) {
    return NextResponse.next();
  }

  // Check if accessing protected routes
  if (pathname.startsWith("/dashboard") || pathname.startsWith("/chat") || pathname.startsWith("/categories")) {
    // Check for authentication token in cookies
    const authToken = request.cookies.get("better-auth.session_token") ||
                      request.cookies.get("better-auth_session_token") ||
                      request.cookies.get("__Secure-better-auth.session_token");

    // On HuggingFace, cookies may not work - let client-side handle auth
    // Only redirect if we're sure there's no session
    const isHuggingFace = request.headers.get("host")?.includes("hf.space");

    if (!authToken && !isHuggingFace) {
      const signInUrl = new URL("/auth/sign-in", request.url);
      signInUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(signInUrl);
    }
  }

  // Allow request to proceed - client-side will check auth
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
