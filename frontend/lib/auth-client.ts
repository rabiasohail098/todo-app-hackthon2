/**
 * Client-side Better Auth configuration.
 * This file creates a client-side only auth client to avoid server-side code in bundles.
 */

import { createAuthClient } from "better-auth/react";

// Get the base URL for auth - defaults to current origin
const getBaseURL = () => {
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
};

// Create a client-only auth instance with explicit baseURL
export const authClient = createAuthClient({
  baseURL: getBaseURL(),
});

export const {
  signIn,
  signUp,
  signOut,
  useSession
} = authClient;