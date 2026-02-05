import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  serverExternalPackages: ["better-auth", "pg"],
  output: "standalone",
  typedRoutes: true,
};

export default nextConfig;