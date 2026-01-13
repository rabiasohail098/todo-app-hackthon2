#!/bin/bash

# Setup script for Phase IV Kubernetes Deployment

set -e

echo "Phase IV: Kubernetes Setup"
echo "=========================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v minikube &> /dev/null; then
    echo -e "${RED}❌ Minikube not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Minikube found${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ kubectl found${NC}"

if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ Helm not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Helm found${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Start Minikube
echo -e "\n${YELLOW}Starting Minikube cluster...${NC}"
minikube start --cpus=4 --memory=4096 --driver=docker
echo -e "${GREEN}✓ Minikube started${NC}"

# Enable metrics-server for HPA
echo -e "\n${YELLOW}Enabling metrics-server addon...${NC}"
minikube addons enable metrics-server
echo -e "${GREEN}✓ metrics-server enabled${NC}"

# Verify cluster
echo -e "\n${YELLOW}Verifying cluster...${NC}"
kubectl cluster-info
echo -e "${GREEN}✓ Cluster verified${NC}"

# Create namespace
echo -e "\n${YELLOW}Creating namespace...${NC}"
kubectl create namespace todo-app || echo "Namespace already exists"
echo -e "${GREEN}✓ Namespace created${NC}"

# Create secrets (with placeholder values)
echo -e "\n${YELLOW}Creating secrets...${NC}"
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL='postgresql://postgres:postgres123@postgres:5432/todo_db' \
  --from-literal=OPENAI_API_KEY='sk-test-key-change-this' \
  --from-literal=JWT_SECRET='your-secret-key-change-this' \
  --from-literal=CLOUDINARY_CLOUD_NAME='changeme' \
  --from-literal=CLOUDINARY_API_KEY='changeme' \
  --from-literal=CLOUDINARY_API_SECRET='changeme' \
  -n todo-app --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Secrets created${NC}"

echo -e "\n${GREEN}=== Phase IV Setup Complete ===${NC}"
echo -e "\nNext steps:"
echo "1. Build Docker images: docker build -t todo-frontend:latest ./frontend"
echo "2. Deploy Helm chart: helm install todo-app helm/todo-app -n todo-app -f helm/todo-app/values-dev.yaml"
echo "3. Check pods: kubectl get pods -n todo-app"
echo "4. Port-forward: kubectl port-forward svc/frontend 3000:3000 -n todo-app"
