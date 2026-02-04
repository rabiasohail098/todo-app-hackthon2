/**
 * Client-side Better Auth configuration.
 * This file creates a client-side only auth client to avoid server-side code in bundles.
 */

import { createAuthClient } from "better-auth/react";

// Create auth client without baseURL - it will use relative URLs which work with same-origin
export const authClient = createAuthClient();

export const {
  signIn,
  signUp,
  signOut,
  useSession
} = authClient;