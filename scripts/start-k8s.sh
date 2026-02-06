#!/bin/bash

# Kubernetes setup and startup for WSL
# Sets up Minikube, creates namespace, and deploys Helm chart

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "☸️  Setting up Kubernetes on WSL"
echo "=================================="

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v minikube &> /dev/null; then
    echo "❌ Minikube not found"
    echo "Install with: curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found"
    echo "Install with: curl -LO https://dl.k8s.io/release/stable.txt && curl -LO https://dl.k8s.io/release/\$(cat stable.txt)/bin/linux/amd64/kubectl && sudo install kubectl /usr/local/bin/"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ Helm not found"
    echo "Install with: curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash"
    exit 1
fi

echo "✓ Prerequisites found"

# Start Minikube
echo ""
echo "Starting Minikube cluster..."
if minikube status | grep -q "Running"; then
    echo "✓ Minikube is already running"
else
    minikube start --cpus=4 --memory=4096 --driver=docker
    echo "✓ Minikube started"
fi

# Get Minikube status
echo ""
echo "Cluster info:"
kubectl cluster-info
kubectl get nodes

# Enable metrics server for HPA
echo ""
echo "Enabling metrics-server addon..."
minikube addons enable metrics-server || echo "⚠️  metrics-server addon might already be enabled"
echo "✓ metrics-server enabled"

# Create namespace
echo ""
echo "Creating namespace..."
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -
echo "✓ Namespace created"

# Create secrets
echo "Creating secrets..."
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL='postgresql://postgres:postgres123@postgres:5432/todo_db' \
  --from-literal=OPENAI_API_KEY='sk-test-key-change-this' \
  --from-literal=JWT_SECRET='your-secret-key-change-this' \
  --from-literal=CLOUDINARY_CLOUD_NAME='changeme' \
  --from-literal=CLOUDINARY_API_KEY='changeme' \
  --from-literal=CLOUDINARY_API_SECRET='changeme' \
  -n todo-app --dry-run=client -o yaml | kubectl apply -f -
echo "✓ Secrets created"

# Validate Helm chart
echo ""
echo "Validating Helm chart..."
cd "$PROJECT_ROOT"
helm lint helm/todo-app
echo "✓ Helm chart is valid"

# Deploy with Helm
echo ""
echo "Deploying application with Helm..."
helm upgrade --install todo-app helm/todo-app \
  -n todo-app \
  -f helm/todo-app/values-dev.yaml \
  --wait
echo "✓ Application deployed"

# Wait for deployments
echo ""
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/frontend deployment/backend \
  -n todo-app || echo "⚠️  Some deployments may still be starting"

# Show status
echo ""
echo "Deployment status:"
kubectl get all -n todo-app
echo ""
echo "Pod status:"
kubectl get pods -n todo-app -o wide

echo ""
echo "✅ Kubernetes setup complete!"
echo ""
echo "Next steps:"
echo "1. Port-forward services:"
echo "   kubectl port-forward -n todo-app svc/frontend-service 3000:3000"
echo "   kubectl port-forward -n todo-app svc/backend-service 8000:8000"
echo ""
echo "2. View logs:"
echo "   kubectl logs deployment/frontend -n todo-app -f"
echo "   kubectl logs deployment/backend -n todo-app -f"
echo ""
echo "3. Access application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/docs"
echo ""
