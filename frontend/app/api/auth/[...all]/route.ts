/**
 * Better Auth API Route Handler
 * Handles all authentication endpoints: sign-up, sign-in, sign-out, session, etc.
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
