#!/bin/bash

echo "============================================================"
echo "Starting Todo App Backend (FastAPI)"
echo "============================================================"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Start uvicorn server
echo "Starting FastAPI server on http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
