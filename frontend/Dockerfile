# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm install

# Copy source code
COPY . .

# Build-time environment variables (needed for Next.js static generation)
ARG BETTER_AUTH_SECRET=build-placeholder
ARG NEXT_PUBLIC_API_URL=https://rabiasohail098-todo-app-backend.hf.space
ARG NEXT_PUBLIC_BASE_URL=https://rabiasohail098-todo-app-frontend.hf.space
ARG DATABASE_URL=postgresql://placeholder:placeholder@localhost:5432/placeholder

ENV BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_PUBLIC_BASE_URL=${NEXT_PUBLIC_BASE_URL}
ENV DATABASE_URL=${DATABASE_URL}

# Build Next.js app (standalone mode)
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Set production environment
ENV NODE_ENV=production
ENV PORT=7860
ENV HOSTNAME=0.0.0.0

# Copy standalone build
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Expose port (Hugging Face uses 7860)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:7860/api/health || exit 1

# Start application
CMD ["node", "server.js"]
