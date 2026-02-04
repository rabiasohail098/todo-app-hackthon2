/**
 * Better Auth configuration for JWT-based authentication.
 *
 * This module configures Better Auth with JWT tokens that have
 * a 24-hour expiration period.
 */

import { betterAuth } from "better-auth";
import { Pool } from "pg";

const AUTH_SECRET = process.env.BETTER_AUTH_SECRET;
const DATABASE_URL = process.env.DATABASE_URL;

if (!AUTH_SECRET) {
  throw new Error("BETTER_AUTH_SECRET environment variable is not set");
}

// Create a PostgreSQL pool for better-auth
const pool = DATABASE_URL ? new Pool({
  connectionString: DATABASE_URL,
}) : undefined;

/**
 * Better Auth instance configured for the Todo App.
 *
 * Configuration:
 * - JWT tokens with 24-hour expiration
 * - httpOnly cookies for secure token storage
 * - Neon PostgreSQL database for user storage
 */
export const auth = betterAuth({
  // Database configuration - Neon PostgreSQL using Pool
  database: pool,

  // Session configuration
  session: {
    // Token expiration: 24 hours (in seconds)
    expiresIn: 60 * 60 * 24, // 86400 seconds

    // Store in httpOnly cookies for security
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24, // 24 hours
    },
  },

  // Secret key for signing tokens
  secret: AUTH_SECRET,

  // Base URL for the application
  baseURL: process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000",

  // Trusted origins - includes HuggingFace Spaces
  trustedOrigins: [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "https://rabiasohail098-todo-app-frontend.hf.space",
    "https://rabiasohail098-todo-app.hf.space",
    // Dynamic origins from env
    process.env.NEXT_PUBLIC_BASE_URL || "",
    // Additional trusted origins (comma-separated)
    ...(process.env.TRUSTED_ORIGINS?.split(",").map(o => o.trim()) || []),
  ].filter(Boolean),

  // Email/password authentication
  emailAndPassword: {
    enabled: true,
    // Password requirements
    minPasswordLength: 8,
  },
});

// Export the API handlers
export const authApi = auth.api;

export default auth;
