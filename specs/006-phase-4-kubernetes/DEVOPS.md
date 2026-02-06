# Phase IV: DevOps Tools Guide

Using Gordon, kubectl-ai, and kagent for intelligent Kubernetes operations.

---

## Overview

Phase IV integrates three AI-powered DevOps tools:

| Tool | Purpose | Status |
|------|---------|--------|
| **Gordon** | Docker image optimization & analysis | Available in Docker Desktop 4.53+ |
| **kubectl-ai** | Generate kubectl commands from English | Standalone CLI tool |
| **kagent** | Kubernetes cluster intelligence | Standalone CLI tool |

---

## 1. Gordon (Docker AI)

### Installation

Gordon is built into Docker Desktop 4.53+.

**Enable Gordon:**
1. Open Docker Desktop
2. Go to **Settings** → **Beta features**
3. Toggle **Docker AI** on
4. Restart Docker

**Verify:**
```bash
docker ai "Hello"
```

Expected response: AI responds to your message

### Usage Examples

#### 1.1 Optimize Dockerfile

```bash
# Get optimization suggestions for your Dockerfile
docker ai "Analyze and optimize this Dockerfile for size and performance"

# Response will suggest:
# - Remove unnecessary layers
# - Use multi-stage builds
# - Choose smaller base images
# - Combine RUN commands
```

**Example Optimization:**

Before (400MB):
```dockerfile
FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

After (150MB) with Gordon suggestions:
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY package*.json ./
RUN npm ci --omit=dev
EXPOSE 3000
CMD ["npm", "start"]
```

#### 1.2 Analyze Image Layers

```bash
# Understand what's in your Docker image
docker ai "What are the largest layers in my todo-frontend:latest image?"

# Response shows:
# - Layer sizes
# - What each layer contains
# - Optimization opportunities
```

#### 1.3 Generate Dockerfile

```bash
# Ask Gordon to generate a Dockerfile
docker ai "Generate a production Dockerfile for a Python FastAPI app with PostgreSQL"

# Generates complete Dockerfile with:
# - Multi-stage build
# - Health checks
# - Security best practices
```

#### 1.4 Troubleshoot Build Issues

```bash
# Diagnose build failures
docker ai "My Docker build failed with 'permission denied' error"

# Response suggests:
# - Possible causes
# - Solutions to try
# - Better practices
```

### Best Practices with Gordon

1. **Ask Specific Questions**: "Reduce image size" vs "What's the largest layer?"
2. **Follow Suggestions**: Multi-stage builds reduce size by 50-70%
3. **Test Changes**: Verify optimizations with `docker run`
4. **Document Decisions**: Record why you chose certain layers/commands

---

## 2. kubectl-ai

### Installation

**macOS (Homebrew):**
```bash
brew tap sozercan/kubectl-ai
brew install kubectl-ai
```

**Linux/Windows (Binary):**
```bash
# Download from GitHub releases
# https://github.com/sozercan/kubectl-ai/releases

# Add to PATH and verify
kubectl-ai "help"
```

### Usage Examples

#### 2.1 Deploy Application

```bash
# Ask kubectl-ai to deploy your app
kubectl-ai "deploy todo app with helm on minikube to namespace todo-app"

# Output: Suggested kubectl/helm commands
# Review before executing:
helm install todo-app helm/todo-app -n todo-app
```

#### 2.2 Scale Deployment

```bash
# Scale backend to 3 replicas
kubectl-ai "scale backend deployment to 3 replicas in todo-app namespace"

# Output:
# kubectl scale deployment backend --replicas=3 -n todo-app

# Execute the command
kubectl scale deployment backend --replicas=3 -n todo-app

# Verify
kubectl get deployment backend -n todo-app
```

#### 2.3 Generate Kubernetes Manifests

```bash
# Ask for a specific manifest
kubectl-ai "create a deployment for a Node.js app with 2 replicas and resource limits"

# Output: Complete YAML manifest
# Copy/paste into a file and apply:
# kubectl apply -f deployment.yaml
```

#### 2.4 Troubleshoot Failures

```bash
# Ask kubectl-ai what's wrong
kubectl-ai "why are my pods in CrashLoopBackOff in todo-app namespace"

# Output: Diagnostic commands
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app
kubectl get events -n todo-app

# Execute suggestions
```

#### 2.5 Configure Autoscaling

```bash
# Generate HPA configuration
kubectl-ai "create horizontal pod autoscaler for backend with min 2 max 5 replicas and 70% cpu target"

# Output: HPA YAML
# Review and apply
```

#### 2.6 Setup Network Policies

```bash
# Generate network policy
kubectl-ai "create network policy allowing frontend pods to talk to backend"

# Output: NetworkPolicy YAML
```

#### 2.7 Manage Resources

```bash
# Get resource usage suggestions
kubectl-ai "what are the resource requests and limits for my frontend deployment"

# Output:
kubectl get deployment frontend -n todo-app -o yaml | grep -A 10 resources

# Optimize based on suggestions
kubectl-ai "suggest resource limits for a Node.js frontend app"
```

### Advanced kubectl-ai Usage

#### Multi-step Operations

```bash
# Step 1: Deploy
kubectl-ai "install helm chart todo-app"

# Step 2: Verify
kubectl-ai "check if all pods are running"

# Step 3: Expose
kubectl-ai "port-forward frontend service to 3000"
```

#### Debugging Workflow

```bash
# Get pod name
PODS=$(kubectl get pods -n todo-app -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Debug with kubectl-ai
kubectl-ai "analyze logs from pod $PODS in todo-app namespace"

# Execute suggestions
kubectl logs $PODS -n todo-app
kubectl exec -it $PODS -n todo-app -- /bin/sh
```

### Best Practices with kubectl-ai

1. **Review Commands First**: Always review suggested commands before executing
2. **Start Simple**: "Scale to 2" before "Setup complex network policies"
3. **Check Namespaces**: Always specify correct namespace
4. **Test in Dev First**: Practice on minikube before production
5. **Document Generated Manifests**: Save to git for version control

---

## 3. kagent (Kubernetes Intelligence Agent)

### Installation

**macOS:**
```bash
brew install bagel-ai/kagent/kagent
```

**Linux/Windows:**
```bash
# Download from GitHub
# https://github.com/bagel-ai/kagent/releases

# Verify installation
kagent --help
```

### Usage Examples

#### 3.1 Analyze Cluster Health

```bash
# Get overall cluster status
kagent "analyze cluster health"

# Output:
# ✓ Nodes: All healthy
# ✓ Control plane: Running
# ⚠ Warnings: 2 pods pending
# ✓ Network: OK
```

#### 3.2 Optimize Resources

```bash
# Get resource optimization suggestions
kagent "suggest resource optimization for my workload in todo-app"

# Output:
# Frontend deployment:
#   Current: 1 CPU, 512Mi memory
#   Recommended: 500m CPU, 256Mi memory
#   Estimated savings: 50%
```

#### 3.3 Cost Estimation

```bash
# Estimate cluster costs (if using cloud)
kagent "estimate monthly cost for this cluster configuration"

# Output:
# Estimated cost: $X/month for 2 replicas per service
# With 5 replicas: $Y/month
# Recommendations: Use spot instances, horizontal scaling
```

#### 3.4 Performance Analysis

```bash
# Identify performance bottlenecks
kagent "analyze performance bottlenecks in production cluster"

# Output:
# - Memory: 85% utilized (too high)
# - CPU: 45% utilized (healthy)
# - Network: 120Mbps average (consider upgrading)
```

#### 3.5 Security Assessment

```bash
# Check security posture
kagent "assess cluster security"

# Output:
# ✓ RBAC: Configured
# ✓ Network policies: Active
# ⚠ Pod security: Missing constraints
# ⚠ Secrets: No encryption at rest
```

#### 3.6 Capacity Planning

```bash
# Plan for growth
kagent "if we scale to 100 users, what resources do we need"

# Output:
# Current: 2 nodes, 8GB RAM total
# Recommended: 4 nodes, 16GB RAM total
# Timeline: Scale in next 30 days
```

#### 3.7 Upgrade Path

```bash
# Check Kubernetes upgrade readiness
kagent "check if our cluster is ready to upgrade to kubernetes 1.29"

# Output:
# ✓ All pods compatible
# ✓ API changes: None critical
# ⚠ Requires node drain procedure
```

### kagent Workflow Example

```bash
# Morning health check
kagent "cluster health report"

# Performance review
kagent "are there any performance issues I should know about"

# Cost optimization
kagent "suggest 20% cost reduction measures"

# Security review
kagent "security assessment report"

# Capacity planning
kagent "forecast resource needs for next quarter"
```

### Best Practices with kagent

1. **Regular Checks**: Run cluster health analysis weekly
2. **Act on Recommendations**: Implement cost/performance suggestions
3. **Track Metrics**: Monitor trends over time
4. **Automate Reporting**: Schedule kagent reports via cron
5. **Document Insights**: Save reports for audit/compliance

---

## Workflow: Using All Three Tools Together

### Scenario: Deploy Optimized Todo App

```bash
# Step 1: Optimize Docker images with Gordon
docker ai "optimize dockerfile for production size and security"
# Review suggestions and apply

# Step 2: Build and test images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Step 3: Create Kubernetes manifests with kubectl-ai
kubectl-ai "create helm deployment for todo app with 3 replicas and autoscaling"
# Review and save manifests

# Step 4: Deploy with kubectl-ai
kubectl-ai "install helm chart todo-app with values-prod.yaml"
# Review commands and execute

# Step 5: Verify with kubectl-ai
kubectl-ai "verify all pods are running and healthy in todo-app"
# Monitor output

# Step 6: Analyze with kagent
kagent "cluster health check and resource optimization"
# Review recommendations

# Step 7: Monitor and optimize
kubectl-ai "setup monitoring for todo app deployments"
kagent "weekly health and cost report"
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Deploy with AI Tools

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build with Gordon assistance
        run: |
          docker build -t todo-app:${{ github.sha }} .
      
      - name: Generate Helm manifests with kubectl-ai
        run: |
          kubectl-ai "generate helm values for production deployment"
      
      - name: Deploy with kubectl-ai
        run: |
          kubectl-ai "deploy todo-app helm chart to production"
      
      - name: Analyze with kagent
        run: |
          kagent "cluster health report after deployment"
```

---

## Troubleshooting AI Tools

### Gordon Not Responding

```bash
# Restart Docker
docker restart

# Or verify it's enabled
open "docker://preferences?tab=beta"
```

### kubectl-ai Generating Wrong Commands

```bash
# Be more specific in your request
# Bad: "scale deployment"
# Good: "scale backend deployment to 3 replicas in todo-app namespace"

# Provide full context
# Include: resource name, namespace, specific parameters
```

### kagent Shows Confusing Metrics

```bash
# Install metrics-server
minikube addons enable metrics-server
kubectl top pods -n todo-app

# Wait a few minutes for metrics to populate
# Then run kagent analysis again
```

---

## Limitations & Workarounds

| Limitation | Workaround |
|-----------|-----------|
| Gordon needs Docker image to analyze | Build/pull image first |
| kubectl-ai might suggest outdated patterns | Always review suggestions |
| kagent needs cluster metrics | Enable metrics-server addon |
| AI tools sometimes generate verbose output | Ask for "concise" or "summary" format |

---

## Resources

- [Gordon Documentation](https://docs.docker.com/)
- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [kagent GitHub](https://github.com/bagel-ai/kagent)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

## Next Steps

1. **Enable Gordon**: Configure in Docker Desktop settings
2. **Install kubectl-ai**: Use your OS package manager
3. **Install kagent**: Download binary or use package manager
4. **Test with Sample Deployments**: Practice commands on minikube first
5. **Integrate into CI/CD**: Add to GitHub Actions workflow
6. **Monitor and Optimize**: Run weekly health checks with kagent

