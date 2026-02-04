/**
 * Client-side Better Auth configuration.
 * This file creates a client-side only auth client to avoid server-side code in bundles.
 */

import { createAuthClient } from "better-auth/react";

// Create a client-only auth instance
export const {
  signIn,
  signUp,
  signOut,
  useSession
} = createAuthClient();