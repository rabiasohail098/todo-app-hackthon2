#!/bin/bash

# Start development environment (Backend + Frontend)
# Runs both services in parallel with proper cleanup

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🚀 Starting Todo App Development Environment"
echo "=============================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "⏸  Shutting down services..."
    
    # Kill all child processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    echo "✓ Services stopped"
    exit 0
}

# Setup cleanup trap
trap cleanup EXIT INT TERM

# Check if backend is set up
if [ ! -d "$PROJECT_ROOT/backend/.venv" ]; then
    echo "❌ Backend virtual environment not found"
    echo "Run: ./scripts/setup-backend.sh"
    exit 1
fi

# Check if frontend is set up
if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo "❌ Frontend node_modules not found"
    echo "Run: ./scripts/setup-frontend.sh"
    exit 1
fi

# Check .env files
if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
    echo "❌ backend/.env not found"
    echo "Run: ./scripts/setup-backend.sh"
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/frontend/.env.local" ]; then
    echo "❌ frontend/.env.local not found"
    echo "Run: ./scripts/setup-frontend.sh"
    exit 1
fi

# Start backend
echo ""
echo "📍 Starting backend (http://localhost:8000)..."
cd "$PROJECT_ROOT/backend"
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
sleep 3
echo "Testing backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend is healthy"
else
    echo "⚠️  Backend might not be ready yet, continuing anyway..."
fi

# Start frontend
echo ""
echo "📍 Starting frontend (http://localhost:3000)..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
echo "✓ Frontend started (PID: $FRONTEND_PID)"

# Wait for frontend to be ready
sleep 5

echo ""
echo "✅ All services started!"
echo ""
echo "📚 Available:"
echo "   • Frontend:  http://localhost:3000"
echo "   • Backend:   http://localhost:8000"
echo "   • API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait
