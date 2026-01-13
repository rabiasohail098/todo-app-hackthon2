# Environment Variables Guide

Complete guide to all environment variables used in the Todo App for different environments (development, staging, production).

---

## Backend Environment Variables

### Database Configuration

```env
# DATABASE_URL
# Format: postgresql://user:password@host:port/database
# Examples:
DATABASE_URL="postgresql://localhost/todo_dev"  # Local development
DATABASE_URL="postgresql://user:pass@db.neon.tech/todo_prod"  # Neon serverless
DATABASE_URL="postgresql://user:pass@rds.amazonaws.com/todo"  # AWS RDS

# DATABASE_ECHO (Optional, for debugging)
DATABASE_ECHO=false  # Set to true to log SQL queries
```

### API Keys

```env
# OPENAI_API_KEY
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY="sk-..."

# GROQ_API_KEY (Optional, for alternative LLM)
# Get from: https://console.groq.com
GROQ_API_KEY="gsk_..."
```

### Cloudinary (Image/File Storage)

```env
# Get from: https://cloudinary.com/console/settings/api-keys
CLOUDINARY_CLOUD_NAME="your-cloud-name"
CLOUDINARY_API_KEY="123456789"
CLOUDINARY_API_SECRET="your-secret-key"
CLOUDINARY_URL="cloudinary://key:secret@cloud-name"  # Alternative format
```

### JWT & Security

```env
# JWT_SECRET - MUST be at least 32 characters
# Generate: openssl rand -base64 32
JWT_SECRET="your-secret-key-min-32-chars-long"

# JWT Token Expiry
JWT_EXPIRY_HOURS=24
REFRESH_TOKEN_EXPIRY_DAYS=30
```

### Server Configuration

```env
# SERVER_PORT
SERVER_PORT=8000

# DEBUG Mode (development only)
DEBUG=false  # Set to true in development

# LOG_LEVEL
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Server Environment
ENVIRONMENT=development  # Options: development, staging, production
```

### CORS Configuration

```env
# CORS_ORIGINS - Comma-separated list of allowed origins
CORS_ORIGINS="http://localhost:3000,http://localhost:3001"

# For production:
CORS_ORIGINS="https://todo-app.com,https://www.todo-app.com"

# CORS_ALLOW_CREDENTIALS
CORS_ALLOW_CREDENTIALS=true

# CORS_ALLOW_METHODS
CORS_ALLOW_METHODS="GET,POST,PUT,DELETE,OPTIONS"

# CORS_ALLOW_HEADERS
CORS_ALLOW_HEADERS="Content-Type,Authorization"
```

### Scheduler Configuration

```env
# SCHEDULER_ENABLED
SCHEDULER_ENABLED=true  # Enable background task scheduler

# SCHEDULER_MAX_WORKERS
SCHEDULER_MAX_WORKERS=4  # Number of worker threads

# Task Configuration
TASK_BATCH_SIZE=100  # Process tasks in batches
TASK_TIMEOUT_SECONDS=300  # Task timeout
```

### Chat Configuration

```env
# MAX_CONVERSATION_LENGTH
MAX_CONVERSATION_LENGTH=50  # Max messages per conversation

# MAX_MESSAGE_LENGTH
MAX_MESSAGE_LENGTH=4000  # Max characters per message

# CHAT_MODEL
CHAT_MODEL="gpt-4-turbo"  # or "gpt-3.5-turbo", "groq/mixtral-8x7b"

# CHAT_TEMPERATURE
CHAT_TEMPERATURE=0.7  # 0.0-2.0, higher = more creative
```

### Session Configuration

```env
# SESSION_TIMEOUT_HOURS
SESSION_TIMEOUT_HOURS=24

# REFRESH_TOKEN_EXPIRY_DAYS
REFRESH_TOKEN_EXPIRY_DAYS=30
```

### Database Pool Configuration

```env
# DB_POOL_SIZE
DB_POOL_SIZE=10  # Number of connections to pool

# DB_POOL_RECYCLE
DB_POOL_RECYCLE=3600  # Recycle connections after this many seconds

# DB_POOL_PRE_PING
DB_POOL_PRE_PING=true  # Test connections before use
```

### Feature Flags

```env
# Enable/disable features
ENABLE_CHAT=true
ENABLE_SUBTASKS=true
ENABLE_ATTACHMENTS=true
ENABLE_CATEGORIES=true
ENABLE_TAGS=true
ENABLE_RECURRENCE=true
ENABLE_COLLABORATION=false  # Coming soon
```

---

## Frontend Environment Variables

### API Configuration

```env
# NEXT_PUBLIC_API_URL - Must be accessible from browser
NEXT_PUBLIC_API_URL="http://localhost:8000"  # Development

# Production:
NEXT_PUBLIC_API_URL="https://api.todo-app.com"

# Or in Kubernetes (port-forward or service URL):
NEXT_PUBLIC_API_URL="http://backend:8000"
```

### Logging

```env
# NEXT_PUBLIC_LOG_LEVEL
NEXT_PUBLIC_LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR

# Log to console
NEXT_PUBLIC_LOG_TO_CONSOLE=true  # Set to false in production
```

### Authentication

```env
# NEXT_PUBLIC_AUTH_URL
NEXT_PUBLIC_AUTH_URL="http://localhost:3000"

# Production:
NEXT_PUBLIC_AUTH_URL="https://todo-app.com"
```

### Analytics (Optional)

```env
# NEXT_PUBLIC_ANALYTICS_ID
NEXT_PUBLIC_ANALYTICS_ID=""  # Google Analytics, Mixpanel, etc.

# NEXT_PUBLIC_SENTRY_DSN
NEXT_PUBLIC_SENTRY_DSN=""  # Error tracking
```

### Feature Flags

```env
# Frontend feature flags
NEXT_PUBLIC_ENABLE_CHAT=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_DARK_MODE=true
```

---

## Kubernetes Environment Variables

### For Docker Image Build

```env
# Build arguments (passed to docker build)
NEXT_PUBLIC_API_URL=http://backend:8000
NODE_ENV=production
REACT_APP_VERSION=1.0.0
```

### ConfigMap Values

In Kubernetes, these are stored in ConfigMap:

```yaml
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: "https://app.example.com"
  SCHEDULER_ENABLED: "true"
  SCHEDULER_MAX_WORKERS: "4"
  TASK_BATCH_SIZE: "100"
  MAX_CONVERSATION_LENGTH: "50"
  MAX_MESSAGE_LENGTH: "4000"
  ENABLE_CHAT: "true"
  ENABLE_SUBTASKS: "true"
  ENABLE_ATTACHMENTS: "true"
  ENABLE_CATEGORIES: "true"
  ENABLE_TAGS: "true"
  ENABLE_RECURRENCE: "true"
  NEXT_PUBLIC_LOG_LEVEL: "INFO"
  NEXT_PUBLIC_ENABLE_CHAT: "true"
```

### Secret Values

In Kubernetes, these are stored in Secret:

```yaml
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  DATABASE_URL: "base64-encoded-url"
  OPENAI_API_KEY: "base64-encoded-key"
  CLOUDINARY_CLOUD_NAME: "base64-encoded-name"
  CLOUDINARY_API_KEY: "base64-encoded-key"
  CLOUDINARY_API_SECRET: "base64-encoded-secret"
  JWT_SECRET: "base64-encoded-secret"
```

---

## Environment-Specific Configurations

### Development

```bash
# backend/.env.development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL="postgresql://localhost/todo_dev"
CORS_ORIGINS="http://localhost:3000"
SCHEDULER_ENABLED=true
NEXT_PUBLIC_LOG_LEVEL=DEBUG
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

### Staging

```bash
# backend/.env.staging
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL="postgresql://user:pass@staging-db.example.com/todo"
CORS_ORIGINS="https://staging.todo-app.com"
SCHEDULER_ENABLED=true
NEXT_PUBLIC_LOG_LEVEL=INFO
NEXT_PUBLIC_API_URL="https://api-staging.todo-app.com"
```

### Production

```bash
# backend/.env.production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL="postgresql://user:pass@prod-db.example.com/todo"
CORS_ORIGINS="https://todo-app.com,https://www.todo-app.com"
SCHEDULER_ENABLED=true
DB_POOL_SIZE=20
NEXT_PUBLIC_LOG_LEVEL=WARNING
NEXT_PUBLIC_API_URL="https://api.todo-app.com"
```

---

## How to Set Environment Variables

### Local Development

```bash
# Create .env file in backend/
cd backend
cp .env.example .env
nano .env  # Edit with your values

# Source before running
source .env
python main.py
```

### Docker

```bash
# Pass via --env flag
docker run --env DATABASE_URL="..." --env OPENAI_API_KEY="..." todo-backend:latest

# Or via .env file
docker run --env-file .env todo-backend:latest

# Or in docker-compose.yml
environment:
  DATABASE_URL: "${DATABASE_URL}"
  OPENAI_API_KEY: "${OPENAI_API_KEY}"
```

### Kubernetes

```bash
# Create secret from file
kubectl create secret generic app-secrets --from-env-file=.env -n todo-app

# Create from individual values
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL="..." \
  --from-literal=OPENAI_API_KEY="..." \
  -n todo-app

# Create ConfigMap
kubectl create configmap app-config --from-literal=LOG_LEVEL=INFO -n todo-app

# Then reference in Deployment:
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: DATABASE_URL
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: LOG_LEVEL
```

### GitHub Actions / CI/CD

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      CLOUDINARY_API_KEY: ${{ secrets.CLOUDINARY_API_KEY }}
```

---

## Security Best Practices

1. **Never commit .env files to git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use .env.example for documentation**
   ```bash
   # Commit this file with placeholder values
   cp .env .env.example
   nano .env.example  # Remove actual values, keep keys only
   git add .env.example
   git commit -m "Add .env.example template"
   ```

3. **Generate strong secrets**
   ```bash
   # Generate 32-character secret
   openssl rand -base64 32
   
   # Generate API key format
   openssl rand -hex 32
   ```

4. **Rotate secrets regularly**
   - Change JWT_SECRET quarterly
   - Rotate API keys when team members leave
   - Update database passwords regularly

5. **Use different secrets per environment**
   - Never reuse production secret in development
   - Each environment has unique DATABASE_URL, API_KEY, etc.

6. **Limit secret access**
   - Only share secrets via secure channels (1Password, LastPass, etc.)
   - Never send via email or Slack
   - Use secret management tools in production (AWS Secrets Manager, Vault)

---

## Troubleshooting

### Missing Environment Variable Error

```
Error: DATABASE_URL environment variable not set
```

**Solution:**
```bash
# Check if variable is set
echo $DATABASE_URL

# If empty, set it
export DATABASE_URL="postgresql://..."

# Or add to .env file and source it
source .env
```

### API Requests Failing

```
Error: Failed to connect to http://localhost:8000
```

**Solution:** Check NEXT_PUBLIC_API_URL is correct
```bash
# Frontend (.env or values.yaml)
NEXT_PUBLIC_API_URL="http://localhost:8000"

# For Kubernetes:
NEXT_PUBLIC_API_URL="http://backend:8000"  # Service name
```

### CORS Errors

```
Error: No 'Access-Control-Allow-Origin' header
```

**Solution:** Update CORS_ORIGINS
```bash
# Backend should list frontend URL
CORS_ORIGINS="http://localhost:3000,https://todo-app.com"
```

### Database Connection Failed

```
Error: FATAL: role "user" does not exist
```

**Solution:** Verify DATABASE_URL credentials
```bash
# Check PostgreSQL user exists
psql -U postgres -c "\du"

# Update DATABASE_URL with correct credentials
DATABASE_URL="postgresql://correct-user:password@host/database"
```

---

## Resources

- [Docker ENV Documentation](https://docs.docker.com/engine/reference/builder/#env)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)
- [FastAPI Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html)

