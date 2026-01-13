# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Set build-time environment variables
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG BETTER_AUTH_SECRET=SMpypQSUUyLDNIX8mXe7laTA3DxExPWCEJNqYAHbcYw=
ARG BETTER_AUTH_URL=http://localhost:3000

ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
ENV BETTER_AUTH_URL=${BETTER_AUTH_URL}

# Build Next.js app
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Set production environment
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV BETTER_AUTH_SECRET=SMpypQSUUyLDNIX8mXe7laTA3DxExPWCEJNqYAHbcYw=
ENV BETTER_AUTH_URL=http://localhost:3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Copy package files
COPY package*.json ./

# Install production dependencies only
RUN npm ci --omit=dev

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# Expose port
EXPOSE 3000

# Health check using /api/health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Start application
CMD ["npm", "start"]
