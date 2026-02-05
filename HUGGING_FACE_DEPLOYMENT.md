# Hugging Face Deployment Guide

## Environment Variables Required

To deploy this Todo app on Hugging Face Spaces, you need to set the following environment variables:

### Backend (.env file in backend directory)

```env
# Database Configuration (Neon PostgreSQL)
DATABASE_URL=your_neon_postgres_connection_string

# JWT Secret for authentication
JWT_SECRET=your_super_secret_jwt_key_make_it_long_and_random

# CORS Origins (comma-separated) - include your Hugging Face Space URL
CORS_ORIGINS=http://localhost:3000,https://your-username-todo-app.hf.space

# OpenRouter API Key for AI chatbot (get from https://openrouter.ai)
OPENAI_API_KEY=your_openrouter_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=nousresearch/hermes-3-llama-3.1:free

# API Port
API_PORT=8000
```

### Frontend (in Hugging Face Spaces Secrets)

```env
# For single-container deployment (same origin - leave empty)
NEXT_PUBLIC_API_URL=  # Empty for same-origin requests in single container deployment
BACKEND_API_URL=http://127.0.0.1:8000  # Internal backend URL for Next.js API routes

# Better Auth Secret (should match JWT_SECRET in backend)
BETTER_AUTH_SECRET=your_super_secret_jwt_key_make_it_long_and_random

# Database URL (same as backend)
DATABASE_URL=your_neon_postgres_connection_string

# Base URL for the application
NEXT_PUBLIC_BASE_URL=https://your-username-todo-app.hf.space
```

## Hugging Face Space Configuration

### Space YAML Configuration (app.yml)

```yaml
runtime:
  accelerator: cpu
  cpu: 2
  memory: 4GiB

secrets:
  - name: NEXT_PUBLIC_API_URL
    description: URL of your backend API
  - name: NEXT_PUBLIC_BASE_URL
    description: URL of your frontend
  - name: BETTER_AUTH_SECRET
    description: Authentication secret
  - name: DATABASE_URL
    description: Database connection string

dependencies:
  - python=3.10
  - pip

pip_requirements: requirements.txt

app_port: 3000

before_start: |
  # Install dependencies
  pip install -r requirements.txt
  # Run database migrations
  cd backend && python run_migration.py
```

## Known Issues and Solutions

### 1. Cookie Stripping on Hugging Face
- Hugging Face Spaces reverse proxy strips Set-Cookie headers
- Solution: The app stores session data in localStorage as fallback
- The X-User-Id header is used to identify users server-side

### 2. Cold Start Issues
- Neon PostgreSQL has cold start delays
- Solution: Enhanced retry logic with longer timeouts in database connection

### 3. Single Container Architecture
- For Hugging Face deployment, both frontend and backend run in one container
- Solution:
  - Use empty NEXT_PUBLIC_API_URL for same-origin requests from browser
  - Use BACKEND_API_URL for internal Next.js API routes to forward to backend service
  - Nginx acts as reverse proxy routing API requests to backend and serving frontend

### 4. Authentication Flow
- Sign-in stores session in both cookies and localStorage
- API calls include X-User-Id header as fallback identification
- Proper error handling redirects to sign-in on authentication failures

### 5. Database Connection Stability
- Enhanced connection pooling for Neon Serverless
- Exponential backoff with jitter for retries
- SSL enforcement and keep-alive settings

## Deployment Steps

1. Fork this repository
2. Create a Hugging Face Space with the appropriate configuration
3. Set the required environment variables/secrets
4. Deploy the backend first
5. Update the NEXT_PUBLIC_API_URL in frontend to point to your backend
6. Deploy the frontend

## Troubleshooting

### Common Issues:

1. **"Failed to fetch tasks" after sign-in:**
   - Check that DATABASE_URL is correctly set
   - Verify JWT_SECRET matches between frontend and backend
   - Ensure CORS_ORIGINS includes your Hugging Face Space URL

2. **Chatbot not working:**
   - Verify OPENAI_API_KEY is set correctly
   - Check that the backend API is accessible from the frontend

3. **Sign-in fails:**
   - Confirm BETTER_AUTH_SECRET is identical in frontend and backend
   - Ensure CORS settings are correct