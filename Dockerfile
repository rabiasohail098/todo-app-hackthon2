# ============================================
# Single container: Frontend + Backend + Nginx
# For HuggingFace Spaces (port 7860)
# ============================================

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .

# Build-time env vars - frontend talks to backend internally
ARG BETTER_AUTH_SECRET=build-placeholder-secret-that-is-long-enough-32chars
ARG NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
ARG NEXT_PUBLIC_BASE_URL=
ARG DATABASE_URL=postgresql://placeholder:placeholder@localhost:5432/placeholder

ENV BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_PUBLIC_BASE_URL=${NEXT_PUBLIC_BASE_URL}
ENV DATABASE_URL=${DATABASE_URL}

RUN npm run build

# Stage 2: Final image
FROM python:3.12-slim

# Install Node.js, Nginx, and supervisord
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    supervisor \
    gettext-base \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---- Backend Setup ----
WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/src ./src
COPY backend/migrations ./migrations
COPY backend/alembic.ini .

# ---- Frontend Setup ----
WORKDIR /app/frontend

# Copy standalone build from builder
COPY --from=frontend-builder /app/frontend/.next/standalone ./
COPY --from=frontend-builder /app/frontend/.next/static ./.next/static
COPY --from=frontend-builder /app/frontend/public ./public

# ---- Nginx Config ----
RUN rm /etc/nginx/sites-enabled/default

COPY <<'NGINX_CONF' /etc/nginx/conf.d/app.conf
server {
    listen 7860;
    server_name _;

    client_max_body_size 10M;

    # Increase timeouts for slow operations
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Frontend (Next.js)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API (FastAPI) - direct access via /backend/
    location /backend/ {
        rewrite ^/backend/(.*) /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
NGINX_CONF

# ---- Wrapper Scripts for Services ----
COPY <<'BACKEND_SCRIPT' /app/run-backend.sh
#!/bin/bash
cd /app/backend
export PYTHONPATH="/app/backend"
exec python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
BACKEND_SCRIPT

COPY <<'FRONTEND_SCRIPT' /app/run-frontend.sh
#!/bin/bash
cd /app/frontend
export PORT=3000
export HOSTNAME=0.0.0.0
export NODE_ENV=production
exec node server.js
FRONTEND_SCRIPT

RUN chmod +x /app/run-backend.sh /app/run-frontend.sh

# ---- Supervisord Config Template ----
COPY <<'SUPERVISORD_CONF' /etc/supervisor/conf.d/app.conf
[supervisord]
nodaemon=true
logfile=/var/log/supervisord.log
pidfile=/var/run/supervisord.pid
user=root

[program:backend]
command=/app/run-backend.sh
directory=/app/backend
autostart=true
autorestart=true
startretries=5
startsecs=5
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:frontend]
command=/app/run-frontend.sh
directory=/app/frontend
autostart=true
autorestart=true
startretries=5
startsecs=5
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
startretries=5
startsecs=3
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
SUPERVISORD_CONF

# ---- Startup Script ----
COPY <<'STARTUP_SCRIPT' /app/start.sh
#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Starting Todo App (Combined Container)"
echo "=========================================="
echo "📅 Date: $(date)"

# Set defaults for environment variables
export DATABASE_URL="${DATABASE_URL}"
export JWT_SECRET="${JWT_SECRET:-default-jwt-secret-change-me}"
export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:3000,http://127.0.0.1:3000,https://*.hf.space}"
export BETTER_AUTH_SECRET="${BETTER_AUTH_SECRET}"
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://127.0.0.1:8000}"
export NEXT_PUBLIC_BASE_URL="${NEXT_PUBLIC_BASE_URL}"
export OPENAI_API_KEY="${OPENAI_API_KEY}"
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
export AI_MODEL="${AI_MODEL:-openai/gpt-4o-mini}"

echo "✅ Environment configured"
echo "   DATABASE_URL: $(echo $DATABASE_URL | sed 's/:[^:@]*@/:***@/')"
echo "   CORS_ORIGINS: ${CORS_ORIGINS}"
echo "   NEXT_PUBLIC_BASE_URL: ${NEXT_PUBLIC_BASE_URL}"

# Check required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is required"
    exit 1
fi

if [ -z "$BETTER_AUTH_SECRET" ]; then
    echo "❌ ERROR: BETTER_AUTH_SECRET is required"
    exit 1
fi

echo "✅ All required environment variables set"
echo "=========================================="

# Start supervisord
exec supervisord -c /etc/supervisor/conf.d/app.conf
STARTUP_SCRIPT

RUN chmod +x /app/start.sh

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:7860/api/health || exit 1

WORKDIR /app

CMD ["/app/start.sh"]
