#!/bin/bash

# Kill any running uvicorn processes
echo "Stopping any running backend servers..."
pkill -f "uvicorn.*main:app" || true
sleep 2

# Navigate to backend directory
cd "$(dirname "$0")"

# Verify .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    exit 1
fi

# Show environment variables (masked)
echo "Environment configuration:"
echo "  API_KEY: $(grep OPENAI_API_KEY .env | cut -c1-30)..."
echo "  BASE_URL: $(grep OPENAI_BASE_URL .env | cut -d= -f2)"
echo "  MODEL: $(grep AI_MODEL .env | cut -d= -f2)"

# Start the server
echo ""
echo "Starting backend server..."
echo "========================================"
python -m uvicorn src.api.main:app --reload --port 8000 --host 0.0.0.0
