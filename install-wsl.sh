#!/bin/bash

# WSL Complete Installation Setup for Todo App Phase 4
# This script sets up everything needed for Phase 4 Kubernetes deployment on WSL

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Todo App Phase 4 - WSL Installation Script                ║"
echo "║  Complete setup for Docker, Kubernetes, and Application       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Update system packages
echo -e "\n${YELLOW}[Step 1/8] Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y
echo -e "${GREEN}✓ System packages updated${NC}"

# Step 2: Install system dependencies
echo -e "\n${YELLOW}[Step 2/8] Installing system dependencies...${NC}"
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    docker.io \
    docker-compose \
    postgresql-client \
    net-tools \
    htop

echo -e "${GREEN}✓ System dependencies installed${NC}"

# Step 3: Install Python tools
echo -e "\n${YELLOW}[Step 3/8] Installing Python tools...${NC}"
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade pipenv uv poetry
echo -e "${GREEN}✓ Python tools installed${NC}"

# Step 4: Setup Docker daemon
echo -e "\n${YELLOW}[Step 4/8] Setting up Docker...${NC}"
sudo usermod -aG docker $USER
sudo systemctl start docker || echo "Docker service not available in WSL, will use Docker Desktop"
echo -e "${GREEN}✓ Docker configured${NC}"

# Step 5: Install kubectl and Helm
echo -e "\n${YELLOW}[Step 5/8] Installing Kubernetes tools...${NC}"
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

echo -e "${GREEN}✓ kubectl and Helm installed${NC}"

# Step 6: Install Minikube
echo -e "\n${YELLOW}[Step 6/8] Installing Minikube...${NC}"
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64
echo -e "${GREEN}✓ Minikube installed${NC}"

# Step 7: Setup application environment
echo -e "\n${YELLOW}[Step 7/8] Setting up application directories...${NC}"
cd "$(dirname "$0")"
cd ../..

# Create Python virtual environment for backend
if [ ! -d "backend/.venv" ]; then
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✓ Backend virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Backend virtual environment already exists${NC}"
fi

# Install frontend dependencies
if [ ! -d "frontend/node_modules" ]; then
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

# Step 8: Verify installations
echo -e "\n${YELLOW}[Step 8/8] Verifying installations...${NC}"

echo "Checking Python..."
python3 --version

echo "Checking pip..."
python3 -m pip --version

echo "Checking Node.js..."
node --version

echo "Checking npm..."
npm --version

echo "Checking Docker..."
docker --version

echo "Checking kubectl..."
kubectl version --client

echo "Checking Helm..."
helm version

echo "Checking Minikube..."
minikube version

echo -e "\n${GREEN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           Installation Complete! 🎉                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Configure environment variables:"
echo "   - cp backend/.env.example backend/.env"
echo "   - Edit backend/.env with your values"
echo "   - cp frontend/.env.local.example frontend/.env.local"
echo ""
echo "2. Start the application:"
echo "   - For development: ./scripts/start-dev.sh"
echo "   - For Kubernetes: ./scripts/start-k8s.sh"
echo ""
echo "3. Quick start options:"
echo "   - Docker Compose: docker-compose up"
echo "   - Minikube: ./k8s/setup.sh && helm install todo-app helm/todo-app -n todo-app"
echo ""
echo -e "${YELLOW}Pro tip: Read specs/006-phase-4-kubernetes/quickstart.md for more details${NC}\n"
