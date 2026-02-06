#!/bin/bash

# Backend Setup for WSL
# Sets up Python virtual environment and dependencies

set -e

echo "🐍 Backend Setup for WSL"
echo "========================"

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source .venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✓ pip upgraded"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env || cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/todo_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_LOG_LEVEL=debug

# OpenAI
OPENAI_API_KEY=your-key-here

# JWT/Auth
JWT_SECRET=your-secret-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# APScheduler
SCHEDULER_ENABLED=true

# Logging
LOG_LEVEL=debug
EOF
    echo "✓ .env file created (configure with your values)"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your database credentials"
echo "2. Run migrations: alembic upgrade head"
echo "3. Start backend: uvicorn main:app --reload"
echo ""
