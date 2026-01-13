#!/bin/bash

# Frontend Setup for WSL
# Installs Node dependencies and configures environment

set -e

echo "⚛️  Frontend Setup for WSL"
echo "=========================="

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

cd "$FRONTEND_DIR"

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Install with: sudo apt-get install nodejs npm"
    exit 1
fi

echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
    echo "✓ Dependencies installed"
else
    echo "✓ node_modules already exists"
    echo "Updating dependencies..."
    npm update
    echo "✓ Dependencies updated"
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cp .env.local.example .env.local || cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_LOG_LEVEL=debug
EOF
    echo "✓ .env.local file created"
else
    echo "✓ .env.local file already exists"
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit frontend/.env.local if needed"
echo "2. Start frontend: npm run dev"
echo "3. Open browser: http://localhost:3000"
echo ""
