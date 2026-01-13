# Phase IV: Deployment Guide

Complete step-by-step guide for deploying Todo Chatbot to Kubernetes using Minikube and Helm.

---

## Overview

This guide walks you through:
1. **Preparing** Docker images
2. **Setting up** Minikube cluster
3. **Deploying** with Helm charts
4. **Verifying** the deployment
5. **Managing** the application

**Estimated Time**: 45 minutes (assuming tools are already installed)

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Docker Desktop** 4.53+ installed
  - macOS/Windows: Download from [docker.com](https://docker.com)
  - Linux: Install via package manager
  - Verify: `docker --version`

- [ ] **Minikube** installed
  - Verify: `minikube version`

- [ ] **kubectl** installed
  - Verify: `kubectl version --client`

- [ ] **Helm 3** installed
  - Verify: `helm version`

- [ ] **Git** repository cloned
  - All source code available locally
  - Phase III (AI chatbot) working

- [ ] **Resources available**
  - 4GB+ RAM free
  - 50GB+ disk space
  - Stable internet connection

---

## Step 1: Prepare Docker Images (15 minutes)

### 1.1 Build Frontend Image

```bash
cd frontend

# Build the Docker image
docker build -t todo-frontend:latest .

# Verify the build was successful
docker images | grep todo-frontend
# Expected: todo-frontend    latest    <image-id>    <size>

cd ..
```

**Expected output:**
```
Successfully tagged todo-frontend:latest
```

### 1.2 Test Frontend Image Locally

```bash
# Run the image
docker run -p 3000:3000 todo-frontend:latest

# In another terminal, test the app
curl http://localhost:3000

# Stop the container (Ctrl+C in first terminal)
```

**Expected**: HTTP 200 response from frontend

### 1.3 Build Backend Image

```bash
cd backend

# Build the Docker image
docker build -t todo-backend:latest .

# Verify the build
docker images | grep todo-backend

cd ..
```

### 1.4 Test Backend Image Locally

```bash
# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/todo_db"
export OPENAI_API_KEY="sk-test-key"
export JWT_SECRET="test-secret"

# Run the image
docker run \
  -p 8000:8000 \
  -e DATABASE_URL \
  -e OPENAI_API_KEY \
  -e JWT_SECRET \
  todo-backend:latest

# In another terminal, test the API
curl http://localhost:8000/docs

# Stop the container (Ctrl+C)
```

**Expected**: API documentation page loads at /docs

### 1.5 (Optional) Push Images to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag images for your account
docker tag todo-frontend:latest YOUR_USERNAME/todo-frontend:latest
docker tag todo-backend:latest YOUR_USERNAME/todo-backend:latest

# Push to registry
docker push YOUR_USERNAME/todo-frontend:latest
docker push YOUR_USERNAME/todo-backend:latest

# Update helm values.yaml with your image names
# frontend.image.repository: YOUR_USERNAME/todo-frontend
# backend.image.repository: YOUR_USERNAME/todo-backend
```

---

## Step 2: Setup Minikube Cluster (10 minutes)

### 2.1 Start Minikube

```bash
# Start with recommended resources
minikube start \
  --cpus=4 \
  --memory=4096 \
  --driver=docker

# Verify cluster is running
kubectl cluster-info
minikube status
```

**Expected output:**
```
minikube: Running
cluster: Running
kubectl: Correctly Configured
```

### 2.2 Enable Required Addons

```bash
# Enable metrics-server (required for HPA/auto-scaling)
minikube addons enable metrics-server

# Verify
minikube addons list | grep metrics-server
# Should show: metrics-server (enabled)
```

### 2.3 Create Namespace

```bash
# Create the namespace
kubectl create namespace todo-app

# Verify
kubectl get namespaces
# Expected output includes: todo-app    Active
```

### 2.4 Create Secrets

```bash
# Create secret with database and API keys
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL='postgresql://postgres:postgres123@postgres:5432/todo_db' \
  --from-literal=OPENAI_API_KEY='sk-your-key-here' \
  --from-literal=JWT_SECRET='your-secret-key-here' \
  --from-literal=CLOUDINARY_CLOUD_NAME='your-cloud-name' \
  --from-literal=CLOUDINARY_API_KEY='your-api-key' \
  --from-literal=CLOUDINARY_API_SECRET='your-api-secret' \
  -n todo-app

# Verify
kubectl get secrets -n todo-app
# Expected: app-secrets    Opaque    6
```

---

## Step 3: Deploy with Helm (10 minutes)

### 3.1 Validate Helm Chart

```bash
# Check for syntax errors
helm lint helm/todo-app
# Expected: No warnings or errors

# Preview the manifests that will be created
helm template todo-app helm/todo-app -n todo-app | head -100
```

### 3.2 Deploy to Minikube (Development)

```bash
# Deploy using development values (single replica)
helm install todo-app helm/todo-app \
  -n todo-app \
  -f helm/todo-app/values-dev.yaml

# Monitor the installation
watch kubectl get all -n todo-app
# Or: kubectl get pods -n todo-app -w (watch mode)
```

**Expected output:**
```
NAME: todo-app
LAST DEPLOYED: <time>
NAMESPACE: todo-app
STATUS: deployed
REVISION: 1
```

### 3.3 Wait for Pods to be Ready

```bash
# Check pod status
kubectl get pods -n todo-app

# Wait for all pods to show "Running" and "1/1" ready
# Expected:
# NAME                       READY   STATUS    RESTARTS   AGE
# frontend-xxxxx             1/1     Running   0          2m
# backend-xxxxx              1/1     Running   0          2m

# Wait for readiness
kubectl wait --for=condition=ready pod \
  -l app=frontend \
  -n todo-app \
  --timeout=300s
```

---

## Step 4: Verify Deployment (10 minutes)

### 4.1 Check All Resources

```bash
# List all resources
kubectl get all -n todo-app

# Expected output shows:
# - Deployment: frontend (1 replica), backend (1 replica)
# - Pod: frontend pod, backend pod
# - Service: frontend-service, backend-service
# - ReplicaSet: frontend and backend
```

### 4.2 Check Pod Logs

```bash
# Frontend logs
kubectl logs deployment/frontend -n todo-app | tail -20

# Backend logs
kubectl logs deployment/backend -n todo-app | tail -20

# Expected: No error messages, app started successfully
```

### 4.3 Check Pod Details

```bash
# Get detailed info about a pod
kubectl describe pod <pod-name> -n todo-app

# Look for:
# - Status: Running
# - Containers: all Running
# - Events: no warning/error events
```

### 4.4 Check Services

```bash
kubectl get svc -n todo-app

# Expected:
# NAME                 TYPE        CLUSTER-IP       PORT(S)
# backend-service      ClusterIP   10.X.X.X         8000/TCP
# frontend-service     NodePort    10.X.X.X         30000:30000/TCP
```

---

## Step 5: Access the Application (5 minutes)

### 5.1 Port-Forward Frontend

**Terminal 1:**
```bash
# Forward frontend service to localhost
kubectl port-forward -n todo-app svc/frontend 3000:3000

# Output shows:
# Forwarding from 127.0.0.1:3000 -> 3000
# Forwarding from [::1]:3000 -> 3000
```

**Terminal 2 or Browser:**
```bash
# Open in browser
open http://localhost:3000

# Or test with curl
curl http://localhost:3000

# Expected: HTML response (200 OK)
```

### 5.2 Port-Forward Backend

**Terminal 3:**
```bash
# Forward backend service
kubectl port-forward -n todo-app svc/backend 8000:8000

# Output shows:
# Forwarding from 127.0.0.1:8000 -> 8000
```

**Terminal 2 or Browser:**
```bash
# Test API docs
open http://localhost:8000/docs

# Or test health endpoint
curl http://localhost:8000/health

# Expected: {"status": "ok"} or Swagger UI
```

### 5.3 Test Full End-to-End

```bash
# 1. Create a task via API
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "From Kubernetes"}'

# Expected: Task created response with ID

# 2. Verify it appears in frontend
# Open http://localhost:3000 in browser

# 3. Test chatbot (if available)
# Send a message via the chat interface
```

---

## Step 6: Configure Auto-Scaling (Optional)

### 6.1 Check HPA Status

```bash
# View Horizontal Pod Autoscaler
kubectl get hpa -n todo-app

# Expected:
# NAME              REFERENCE             TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
# backend-hpa       Deployment/backend    0%/70%    2         5         1          2m
# frontend-hpa      Deployment/frontend   0%/70%    2         5         1          2m
```

### 6.2 Monitor CPU Usage

```bash
# Watch metrics (requires metrics-server)
watch kubectl top pods -n todo-app

# Shows CPU and memory usage per pod
```

### 6.3 Test Auto-Scaling (Optional - Load Testing)

```bash
# Install Apache Bench (macOS)
brew install httpd

# Run load test
ab -n 1000 -c 50 http://localhost:3000/

# Monitor scaling in another terminal
watch kubectl get pods -n todo-app

# Watch HPA
watch kubectl get hpa -n todo-app

# Expected: Replicas increase to 2-3 during load
```

---

## Step 7: Upgrade & Rollback

### 7.1 Update Application

```bash
# Modify values.yaml or update image tags

# Upgrade the release
helm upgrade todo-app helm/todo-app \
  -n todo-app \
  -f helm/todo-app/values-dev.yaml

# Monitor the rollout
kubectl rollout status deployment/backend -n todo-app
```

### 7.2 Rollback if Issues Occur

```bash
# View release history
helm history todo-app -n todo-app

# Rollback to previous version
helm rollback todo-app -n todo-app

# Or rollback to specific revision
helm rollback todo-app 1 -n todo-app
```

---

## Step 8: Cleanup (When Done)

### 8.1 Delete Helm Release

```bash
# Delete the deployment
helm uninstall todo-app -n todo-app

# Verify resources deleted
kubectl get all -n todo-app
# Should be empty
```

### 8.2 Delete Namespace

```bash
kubectl delete namespace todo-app
```

### 8.3 Stop Minikube

```bash
# Stop cluster (keeps data)
minikube stop

# Or delete cluster (removes all data)
minikube delete
```

---

## Troubleshooting During Deployment

### Pods Stuck in Pending

```bash
# Check what's wrong
kubectl describe pod <pod-name> -n todo-app

# Common causes:
# 1. Insufficient memory: Increase Minikube memory
#    minikube delete && minikube start --memory=4096
# 2. Image pull error: Build image locally or push to registry
```

### ImagePullBackOff

```bash
# Solution 1: Build image locally (if using minikube docker-env)
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend

# Solution 2: Push to Docker Hub and update values.yaml
docker tag todo-frontend:latest YOUR_USERNAME/todo-frontend:latest
docker push YOUR_USERNAME/todo-frontend:latest
# Then update helm/todo-app/values-dev.yaml:
# frontend.image.repository: YOUR_USERNAME/todo-frontend
```

### CrashLoopBackOff

```bash
# Check logs for error
kubectl logs <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app --previous

# Common causes:
# 1. Database connection failed: Verify DATABASE_URL in Secret
# 2. Missing environment variable: Check Secret creation
# 3. Health check failing: Check app logs for startup errors
```

### Connection Refused

```bash
# Verify port-forward is running
ps aux | grep port-forward
# Should show port-forward process

# Restart port-forward if needed
kubectl port-forward -n todo-app svc/frontend 3000:3000

# Test connection
curl -v http://localhost:3000
```

---

## Next Steps

1. **Run Load Tests**: See `specs/006-phase-4-kubernetes/tasks.md` for load testing procedure
2. **Enable Monitoring**: Install Prometheus/Grafana for metrics
3. **Setup CI/CD**: Configure GitHub Actions for automated builds
4. **Deploy to Cloud**: Use Phase IV concepts for cloud deployment (Phase V)
5. **Implement Security**: Add Network Policies, Pod Security Policies

---

## Quick Reference Commands

```bash
# Get cluster info
kubectl cluster-info
minikube status

# Manage namespace
kubectl create namespace todo-app
kubectl get namespaces

# Deploy
helm install todo-app helm/todo-app -n todo-app -f helm/todo-app/values-dev.yaml
helm upgrade todo-app helm/todo-app -n todo-app -f helm/todo-app/values-dev.yaml
helm uninstall todo-app -n todo-app

# Monitor
kubectl get pods -n todo-app
kubectl logs deployment/frontend -n todo-app
kubectl describe pod <pod-name> -n todo-app

# Port forwarding
kubectl port-forward svc/frontend 3000:3000 -n todo-app
kubectl port-forward svc/backend 8000:8000 -n todo-app

# Scaling
kubectl scale deployment frontend --replicas=3 -n todo-app
kubectl get hpa -n todo-app

# Troubleshoot
kubectl get events -n todo-app
kubectl exec -it <pod-name> -n todo-app -- /bin/sh
kubectl logs <pod-name> -n todo-app --tail=100 -f
```

---

## Support

For issues:
1. Check logs: `kubectl logs <pod-name> -n todo-app`
2. Describe pod: `kubectl describe pod <pod-name> -n todo-app`
3. List events: `kubectl get events -n todo-app`
4. See TROUBLESHOOTING.md for detailed solutions
