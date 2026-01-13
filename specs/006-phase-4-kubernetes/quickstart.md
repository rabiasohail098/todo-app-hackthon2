# Phase IV: Quick Start Guide

Get your Todo Chatbot running on Kubernetes in 30 minutes.

---

## Prerequisites (5 minutes)

### Check Prerequisites
```bash
# Docker Desktop (4.53+ with Kubernetes enabled)
docker --version
docker ps

# kubectl
kubectl version --client

# Helm
helm version

# Minikube
minikube version
```

### Install Missing Tools
**Windows (using Chocolatey):**
```bash
choco install docker-desktop
choco install kubernetes-cli
choco install helm
choco install minikube
```

**macOS (using Brew):**
```bash
brew install docker
brew install kubectl
brew install helm
brew install minikube
```

**Linux:**
```bash
# Docker (follow official docs)
# kubectl
curl -LO https://dl.k8s.io/release/stable.txt
curl -LO "https://dl.k8s.io/release/$(cat stable.txt)/bin/linux/amd64/kubectl"

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Minikube
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

---

## Step 1: Start Minikube (2 minutes)

```bash
# Start with sufficient resources
minikube start --cpus=4 --memory=4096 --driver=docker

# Verify
kubectl cluster-info
kubectl get nodes
```

**Expected Output:**
```
cluster-info: Kubernetes control plane is running at https://127.0.0.1:56234
coredns is running at https://127.0.0.1:56234/api/v1/namespaces/kube-system/services/coredns:dns/proxy

NAME       STATUS   ROLES                  AGE   VERSION
minikube   Ready    control-plane,worker   5m    v1.28.0
```

---

## Step 2: Build Docker Images (5 minutes)

### Option A: Build locally (recommended)
```bash
# Frontend
cd frontend
docker build -t todo-frontend:latest .
docker run -p 3000:3000 todo-frontend:latest
# Test: http://localhost:3000 then Ctrl+C

cd ..

# Backend
cd backend
docker build -t todo-backend:latest .
cd ..
```

### Option B: Use Minikube Docker daemon (no Docker Hub needed)
```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build (images stored in Minikube)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Verify
docker images
```

---

## Step 3: Create Kubernetes Namespace & Secrets (2 minutes)

```bash
# Create namespace
kubectl create namespace todo-app

# Create ConfigMap
kubectl create configmap app-config \
  --from-literal=LOG_LEVEL=debug \
  --from-literal=API_HOST=backend-service \
  -n todo-app

# Create Secret (database credentials)
kubectl create secret generic db-secret \
  --from-literal=DATABASE_URL=postgresql://postgres:password@postgres:5432/todo_db \
  -n todo-app
```

---

## Step 4: Deploy with Helm (3 minutes)

```bash
# Validate chart
helm lint helm/todo-app

# Preview manifests
helm template todo-app helm/todo-app -n todo-app | head -50

# Install
helm install todo-app helm/todo-app \
  -n todo-app \
  -f helm/todo-app/values-dev.yaml

# Wait for pods to start
kubectl wait --for=condition=ready pod \
  -l app=frontend \
  -n todo-app \
  --timeout=300s
```

---

## Step 5: Verify Deployment (3 minutes)

```bash
# Check pods
kubectl get pods -n todo-app
# Expected: all pods should be Running

# Check services
kubectl get svc -n todo-app

# Check events
kubectl get events -n todo-app

# Check logs
kubectl logs deployment/frontend -n todo-app
kubectl logs deployment/backend -n todo-app
```

---

## Step 6: Access the App (5 minutes)

### Port Forward

```bash
# Terminal 1: Frontend
kubectl port-forward -n todo-app svc/frontend 3000:3000

# Terminal 2: Backend
kubectl port-forward -n todo-app svc/backend 8000:8000
```

### Test

**Frontend:**
```bash
# Browser or curl
curl http://localhost:3000
```

**Backend API:**
```bash
# Browser (opens Swagger UI)
open http://localhost:8000/docs

# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "From kubectl"}'
```

---

## Step 7: Test Auto-Healing (5 minutes)

```bash
# Get pod name
POD_NAME=$(kubectl get pod -n todo-app -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Delete a pod
kubectl delete pod $POD_NAME -n todo-app

# Watch it restart
kubectl get pods -n todo-app -w

# Verify logs of new pod
kubectl logs deployment/backend -n todo-app
```

---

## Common Tasks

### View Logs
```bash
# Frontend logs
kubectl logs deployment/frontend -n todo-app -f

# Backend logs
kubectl logs deployment/backend -n todo-app -f

# All logs
kubectl logs -n todo-app -f --all-containers
```

### Scale Deployment
```bash
# Scale backend to 3 replicas
kubectl scale deployment backend --replicas=3 -n todo-app

# Verify
kubectl get deployment backend -n todo-app
```

### Update Deployment
```bash
# Modify values.yaml then upgrade
helm upgrade todo-app helm/todo-app \
  -n todo-app \
  -f helm/todo-app/values-dev.yaml

# Watch rollout
kubectl rollout status deployment/frontend -n todo-app
```

### Delete Everything
```bash
# Uninstall Helm release
helm uninstall todo-app -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Stop Minikube
minikube stop
```

---

## Troubleshooting

### Pods stuck in Pending
```bash
kubectl describe pod <pod-name> -n todo-app
# Check: Insufficient CPU/memory
# Fix: Increase Minikube resources
minikube delete
minikube start --cpus=4 --memory=4096
```

### ImagePullBackOff
```bash
# If using local images (not in registry)
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
# Redeploy

# Or push to Docker Hub:
docker push <user>/todo-frontend:latest
```

### Connection refused
```bash
# Verify port-forward is running
kubectl port-forward -n todo-app svc/frontend 3000:3000

# Verify pod is running
kubectl get pods -n todo-app

# Check events
kubectl get events -n todo-app
```

### Database connection error
```bash
# Verify ConfigMap
kubectl get configmap -n todo-app -o yaml

# Verify Secret
kubectl get secret -n todo-app -o yaml

# Check backend logs
kubectl logs deployment/backend -n todo-app
```

---

## Next Steps

1. **Verify everything works**: Test all endpoints
2. **Read full documentation**: See `DEPLOYMENT.md`
3. **Use kubectl-ai**: `kubectl-ai "list all deployed services"`
4. **Load test**: Run performance tests
5. **Commit to Git**: Push Helm charts to repo

---

## Quick Reference

| Task | Command |
|------|---------|
| Start Minikube | `minikube start --cpus=4 --memory=4096` |
| Deploy | `helm install todo-app helm/todo-app -n todo-app` |
| Check Status | `kubectl get all -n todo-app` |
| View Logs | `kubectl logs deployment/frontend -n todo-app` |
| Port Forward Frontend | `kubectl port-forward svc/frontend 3000:3000 -n todo-app` |
| Port Forward Backend | `kubectl port-forward svc/backend 8000:8000 -n todo-app` |
| Scale Backend | `kubectl scale deployment backend --replicas=3 -n todo-app` |
| Upgrade Release | `helm upgrade todo-app helm/todo-app -n todo-app` |
| Delete All | `helm uninstall todo-app -n todo-app && kubectl delete namespace todo-app` |
| Stop Minikube | `minikube stop` |

---

## Need Help?

- Check logs: `kubectl logs`
- Describe pod: `kubectl describe pod <name> -n todo-app`
- Check events: `kubectl get events -n todo-app`
- Full troubleshooting: See `TROUBLESHOOTING.md`
