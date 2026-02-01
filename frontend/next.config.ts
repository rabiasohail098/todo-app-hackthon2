import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  serverExternalPackages: ["better-auth", "pg"],
  output: "standalone",
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // For client-side builds, provide empty implementations for Node.js-specific modules
      config.resolve.fallback = {
        ...config.resolve.fallback,
        "node:module": false,
        "node:util": false,
        "node:fs": false,
        "node:stream": false,
        "node:buffer": false,
        "node:events": false,
        "node:url": false,
        "node:path": false,
        "node:crypto": false,
        "node:process": false,
      };
    }
    return config;
  },
};

export default nextConfig;
