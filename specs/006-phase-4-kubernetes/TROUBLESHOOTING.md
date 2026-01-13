# Phase IV: Kubernetes Troubleshooting Guide

Comprehensive guide to diagnose and resolve common Kubernetes, Docker, Helm, and Minikube issues.

---

## Quick Diagnosis Flowchart

```
┌─────────────────────────────────────────┐
│ Deployment Not Working?                 │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴─────────┐
       │                 │
   Pods Running?     Check Minikube
       │                 │
    Yes/No          Running/Not Running
       │                 │
       ├─────────────────┤
       ▼
   Pod State?
   │
   ├─ Pending → Check resource requests (sec 1)
   ├─ ImagePullBackOff → Check image registry (sec 2)
   ├─ CrashLoopBackOff → Check logs (sec 3)
   ├─ Running but not responding → Check network (sec 4)
   └─ Evicted → Check node resources (sec 5)
```

---

## 1. Pending Pods (Pod Stuck in Pending State)

### Symptoms
- Pod status shows "Pending" for more than 2-3 minutes
- Pod not starting or scheduling
- No progress in `kubectl get pods`

### Diagnosis

```bash
# Check pod status details
kubectl describe pod <pod-name> -n todo-app

# Look for Events section - shows blocking reason
# Common reasons:
# - Insufficient CPU
# - Insufficient memory
# - No node available
# - PVC not bound
```

### Solutions

#### 1.1 Insufficient Resources

**Problem**: Pod requests more resources than available

```bash
# Check node resources
kubectl top nodes

# Example output:
# NAME       CPU(cores)   CPU%   MEMORY(Mi)   MEMORY%
# minikube   500m         12%    768Mi        38%

# Check what the pod requests
kubectl get pod <pod-name> -n todo-app -o yaml | grep -A 5 resources
```

**Fix: Reduce resource requests**

```bash
# Edit deployment
kubectl edit deployment backend -n todo-app

# Change:
# resources:
#   requests:
#     memory: "512Mi"    <- Was 1Gi
#     cpu: "500m"        <- Was 1000m
#   limits:
#     memory: "512Mi"
#     cpu: "500m"

# Save and exit (:wq in vim)
# Deployment will recreate pods with new resources
```

**Or: Increase Minikube resources**

```bash
# Stop Minikube
minikube stop

# Delete and restart with more resources
minikube delete
minikube start --cpus=4 --memory=4096

# Redeploy
helm install todo-app helm/todo-app -n todo-app -f helm/todo-app/values-dev.yaml
```

#### 1.2 PersistentVolumeClaim Not Bound

**Problem**: Pod waiting for PVC

```bash
# Check PVC status
kubectl get pvc -n todo-app

# If STATUS is Pending:
kubectl describe pvc <pvc-name> -n todo-app
```

**Fix**: For todo-app, we use external database (no K8s PVC needed)

```bash
# Remove PVC requirement from deployment
kubectl edit deployment backend -n todo-app

# Remove volumeMounts section
# Remove volumes section
```

---

## 2. ImagePullBackOff

### Symptoms
- Pod status shows "ImagePullBackOff"
- Cannot pull Docker image
- Authentication or registry issues

### Diagnosis

```bash
# Check the exact error
kubectl describe pod <pod-name> -n todo-app

# Look for:
# Failed to pull image "todo-frontend:latest": error pulling image...

# Check if image exists locally
docker images | grep todo-frontend

# Check image registry access
kubectl get events -n todo-app --sort-by='.lastTimestamp' | tail -10
```

### Solutions

#### 2.1 Image Not Built Locally

**Problem**: Using image that hasn't been built yet

```bash
# Build the image
cd frontend
docker build -t todo-frontend:latest .

# Or backend
cd backend
docker build -t todo-backend:latest .

# Verify image exists
docker images | grep todo-
```

#### 2.2 Using Docker Hub Registry (Minikube)

**Problem**: Minikube can't access Docker Hub credentials

```bash
# Check if image is in Docker Hub
# If not, build and push locally

# For local Minikube:
# Build image in Docker, then load into Minikube
docker build -t todo-frontend:latest ./frontend

# Load into Minikube's Docker daemon
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Verify
minikube image ls | grep todo-
```

#### 2.3 Wrong Image Tag in Helm Values

**Problem**: Deployment looking for wrong image tag

```bash
# Check what tag is configured
helm get values todo-app -n todo-app | grep image

# Check Helm values file
cat helm/todo-app/values.yaml | grep -A 2 image

# Edit and redeploy
helm upgrade todo-app helm/todo-app -n todo-app \
  --set frontend.image.tag="latest" \
  --set backend.image.tag="latest"
```

#### 2.4 Using Private Registry

**Problem**: Pulling from private Docker Hub or private registry

```bash
# Create docker registry secret
kubectl create secret docker-registry regcred \
  --docker-server=docker.io \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email> \
  -n todo-app

# Update deployment to use secret
kubectl patch serviceaccount default -n todo-app \
  -p '{"imagePullSecrets": [{"name": "regcred"}]}'

# Or add to values.yaml:
# imagePullSecrets:
#   - name: regcred
```

---

## 3. CrashLoopBackOff

### Symptoms
- Pod keeps crashing and restarting
- Status shows "CrashLoopBackOff"
- Restart count keeps increasing

### Diagnosis

```bash
# Check pod logs
kubectl logs <pod-name> -n todo-app

# Check previous crash logs
kubectl logs <pod-name> -n todo-app --previous

# Get pod events
kubectl describe pod <pod-name> -n todo-app

# Check exit code (last line)
kubectl get pod <pod-name> -n todo-app -o jsonpath='{.status.containerStatuses[0].lastState.terminated.exitCode}'
```

### Common Exit Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 1 | General error | Check logs for specific error |
| 127 | Command not found | Check entry point/CMD in Dockerfile |
| 137 | Kill signal (out of memory) | Increase memory limit |
| 139 | Segmentation fault | Application issue |
| Exit 0 but restart | Application exiting normally | Add readiness probe |

### Solutions

#### 3.1 Missing Environment Variables

**Problem**: Application fails without required env vars

```bash
# Check what env vars are being set
kubectl exec -it <pod-name> -n todo-app -- env | sort

# Compare with required vars
# Check Dockerfile for ENV statements
# Check values.yaml for env section

# Add missing variable
kubectl set env deployment/backend \
  DATABASE_URL="postgresql://..." \
  -n todo-app
```

#### 3.2 Database Connection Failed

**Problem**: Application can't connect to database

```bash
# Check database URL
kubectl logs <pod-name> -n todo-app | grep -i database

# Common error: "Connection refused"
# Solution: Check if DATABASE_URL is correct

# Test database connectivity
kubectl exec -it <backend-pod> -n todo-app -- /bin/sh

# Inside pod:
curl https://your-database-url  # Test if reachable
psql $DATABASE_URL -c "SELECT 1"  # Test PostgreSQL
```

**Fix:**

```bash
# Verify database exists and is accessible
# Update DATABASE_URL in values.yaml or secret

# Redeploy
helm upgrade todo-app helm/todo-app -n todo-app \
  --set backend.env.DATABASE_URL="postgresql://user:pass@host/db"
```

#### 3.3 Port Already in Use

**Problem**: Application port conflict

```bash
# Check what ports are configured
kubectl get deployment backend -n todo-app -o yaml | grep -i port

# Check if port is bound in container
kubectl exec -it <backend-pod> -n todo-app -- netstat -tlnp
```

**Fix:**

```bash
# Change port in deployment
kubectl edit deployment backend -n todo-app

# Update containerPort to unused port
# Change service port accordingly
```

#### 3.4 Readiness Probe Failing

**Problem**: Application running but readiness probe says otherwise

```bash
# Check readiness probe configuration
kubectl get deployment backend -n todo-app -o yaml | grep -A 10 readinessProbe

# Common issue: Probe checks /health but app serves on /api/health

# Check what endpoint app exposes
kubectl logs <pod-name> -n todo-app | grep -i health
```

**Fix:**

```bash
# Update readiness probe in values.yaml
cat helm/todo-app/values.yaml | grep -A 5 readinessProbe

# Change httpGet.path to match application endpoint
# Change initialDelaySeconds if app needs more startup time

helm upgrade todo-app helm/todo-app -n todo-app
```

---

## 4. Pods Running But Not Responding

### Symptoms
- Pod status shows "Running"
- But application doesn't respond to requests
- Connection timeout or refused

### Diagnosis

```bash
# Check pod is actually running
kubectl get pods -n todo-app

# Check logs for errors
kubectl logs <pod-name> -n todo-app -f

# Test connectivity from within pod
kubectl exec -it <pod-name> -n todo-app -- /bin/sh

# Inside pod, test backend
wget -qO- http://localhost:3000 or :8000  # Depends on service

# Exit pod
exit
```

### Solutions

#### 4.1 Service Not Exposing Pod

**Problem**: Service selector doesn't match pod labels

```bash
# Check pod labels
kubectl get pods <pod-name> -n todo-app --show-labels

# Check service selector
kubectl get service <service-name> -n todo-app -o yaml | grep -A 3 selector

# Labels should match selector
# Example:
# Pod labels: app=frontend,tier=frontend
# Service selector: app: frontend,tier: frontend
```

**Fix:**

```bash
# Update deployment labels to match service selector
kubectl patch deployment frontend \
  -p '{"spec":{"selector":{"matchLabels":{"app":"frontend"}}}}' \
  -n todo-app
```

#### 4.2 Network Policy Blocking Traffic

**Problem**: Pod can't talk to other pods due to network policy

```bash
# Check network policies
kubectl get networkpolicies -n todo-app

# Describe the policy
kubectl describe networkpolicy <policy-name> -n todo-app

# Test connectivity
kubectl exec -it <frontend-pod> -n todo-app -- \
  wget -qO- http://backend:8000/health
```

**Fix:**

```bash
# If connectivity fails, delete restrictive policy
kubectl delete networkpolicy <policy-name> -n todo-app

# Or update policy to allow traffic
# Edit and reapply
```

#### 4.3 Service Port Mismatch

**Problem**: Service port doesn't match container port

```bash
# Check service and deployment ports
kubectl get service frontend -n todo-app -o yaml | grep -A 3 ports:
kubectl get deployment frontend -n todo-app -o yaml | grep -A 2 containerPort:

# They should match!
```

**Fix:**

```bash
# Update values.yaml to match
# frontend.service.port and frontend.containerPort should align

helm upgrade todo-app helm/todo-app -n todo-app
```

---

## 5. Pod Evicted (Out of Memory or Disk)

### Symptoms
- Pod status shows "Evicted"
- Cannot restart pod
- Cannot describe pod (already deleted)

### Diagnosis

```bash
# Check node resources
kubectl top nodes

# Check events for eviction reason
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Look for: "Evicted" reason = "MemoryPressure" or "DiskPressure"
```

### Solutions

#### 5.1 Out of Memory

**Problem**: Pod using more memory than limit

```bash
# Check actual memory usage
kubectl top pods -n todo-app

# Check memory limits in deployment
kubectl get deployment backend -n todo-app -o yaml | grep -A 3 limits:
```

**Fix:**

```bash
# Increase memory limit
helm upgrade todo-app helm/todo-app -n todo-app \
  --set backend.resources.limits.memory="512Mi" \
  --set backend.resources.requests.memory="256Mi"

# Or increase Minikube memory
minikube stop
minikube start --memory=4096
```

#### 5.2 Out of Disk Space

**Problem**: Minikube running out of disk space

```bash
# Check disk usage
kubectl describe node minikube

# Clean up images
docker rmi $(docker images -q)

# Clean up Docker volumes
docker volume prune -f
```

**Fix:**

```bash
# Restart Minikube with more disk
minikube delete
minikube start --memory=4096 --disk-size=50GB

# Redeploy
```

---

## 6. Helm Deployment Issues

### Symptoms
- `helm install` fails with errors
- `helm upgrade` doesn't update deployment
- Chart validation errors

### Diagnosis

```bash
# Validate Helm chart
helm lint helm/todo-app

# Check chart rendering
helm template todo-app helm/todo-app

# Check what values were used
helm get values todo-app -n todo-app

# Compare with values file
diff <(helm get values todo-app -n todo-app) helm/todo-app/values-dev.yaml
```

### Solutions

#### 6.1 Chart Validation Fails

**Problem**: Helm lint shows errors

```bash
# Check error
helm lint helm/todo-app

# Common issues:
# - YAML syntax error
# - Missing required fields
# - Invalid template syntax
```

**Fix:**

```bash
# Fix YAML formatting in values.yaml
# Ensure proper indentation
# Use yamllint to validate
yamllint helm/todo-app/values.yaml

# Fix template syntax
# Check for missing double braces {{ }}
# Check quote escaping
```

#### 6.2 Values Not Applied

**Problem**: Changed values.yaml but deployment not updated

```bash
# Did you run helm upgrade?
helm get values todo-app -n todo-app

# This should show current values
```

**Fix:**

```bash
# Must use helm upgrade (not reinstall)
helm upgrade todo-app helm/todo-app -n todo-app -f helm/todo-app/values-dev.yaml

# Or set values directly
helm upgrade todo-app helm/todo-app -n todo-app \
  --set backend.replicas=3 \
  --set frontend.replicas=2
```

#### 6.3 Old Pod Still Running

**Problem**: Old pod not terminated after upgrade

```bash
# Check pod creation time
kubectl get pods -n todo-app -o wide

# If old pod still running:
# Force delete old pods
kubectl delete pod <old-pod-name> -n todo-app --grace-period=0 --force
```

---

## 7. Docker Issues

### Problem: Docker Won't Build Image

```bash
# Check Docker is running
docker ps

# Check build logs
docker build -t todo-frontend:latest ./frontend 2>&1 | tail -20

# Common issues:
# - Dockerfile not found: ls -la frontend/Dockerfile
# - Build context wrong: cd frontend && docker build ...
```

### Problem: Docker Image Too Large

```bash
# Check image size
docker images | grep todo-

# Use Gordon to optimize
docker ai "reduce size of this Dockerfile"

# Or manually optimize
# - Use Alpine base image
# - Remove build tools in final stage
# - Combine RUN commands
```

### Problem: Cannot Connect to Docker Hub

```bash
# Check Docker login
docker info | grep "Username"

# If not logged in:
docker login

# Or use local images only
minikube image load todo-frontend:latest
```

---

## 8. Minikube Issues

### Minikube Won't Start

```bash
# Check if Docker is running
docker ps

# Check Minikube status
minikube status

# If problematic:
minikube stop
minikube delete
minikube start --cpus=4 --memory=4096

# Re-enable required addons
minikube addons enable metrics-server
```

### Metrics Server Not Available

**Problem**: `kubectl top` shows "Unable to calculate metrics"

```bash
# Check if metrics-server is enabled
minikube addons list | grep metrics-server

# Enable it
minikube addons enable metrics-server

# Wait 1-2 minutes for metrics to populate
sleep 60
kubectl top nodes
```

### Cannot Access Service from Host

```bash
# Use port-forward instead of service IP
kubectl port-forward service/frontend 3000:3000 -n todo-app

# Or use Minikube tunnel
minikube tunnel
# Then access service at <service-cluster-ip>:port
```

---

## 9. Database Connection Issues

### Cannot Connect to Database

```bash
# Check database URL is set
kubectl get secret -n todo-app -o yaml | grep DATABASE_URL

# Check if database is accessible
kubectl exec -it <backend-pod> -n todo-app -- \
  psql "$DATABASE_URL" -c "SELECT 1"

# If connection refused:
# - Check DATABASE_URL format
# - Check database server is running
# - Check firewall allows connection
# - Check credentials are correct
```

### Database Migrations Failed

```bash
# Check migration logs
kubectl logs <backend-pod> -n todo-app | grep -i migration

# Common issues:
# - Database doesn't exist: Create it manually
# - Connection string wrong: Update secret
# - Permissions missing: Update database user

# Re-run migrations manually
kubectl exec -it <backend-pod> -n todo-app -- \
  alembic upgrade head
```

---

## 10. Debugging Workflow

### Step-by-Step Debugging

```bash
# 1. Get pod status
kubectl get pods -n todo-app

# 2. Describe failing pod
kubectl describe pod <pod-name> -n todo-app

# 3. Check logs
kubectl logs <pod-name> -n todo-app

# 4. Check previous logs if crashing
kubectl logs <pod-name> -n todo-app --previous

# 5. Interactive debugging
kubectl exec -it <pod-name> -n todo-app -- /bin/sh

# 6. Check environment variables
env | sort

# 7. Test connectivity
curl http://backend:8000/health

# 8. Check resource usage
kubectl top pods -n todo-app

# 9. Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# 10. Check deployment status
kubectl rollout status deployment/backend -n todo-app
```

### Saving Diagnostic Info

```bash
# Collect all diagnostic info
mkdir diagnostics
kubectl get all -n todo-app -o yaml > diagnostics/all-resources.yaml
kubectl describe all -n todo-app > diagnostics/descriptions.txt
kubectl logs -n todo-app --all-containers=true > diagnostics/logs.txt
kubectl get events -n todo-app > diagnostics/events.txt

# Share with team for debugging
zip -r diagnostics.zip diagnostics/
```

---

## 11. Performance Issues

### Pod Consuming Too Much CPU

```bash
# Identify high-cpu pod
kubectl top pods -n todo-app --sort-by=cpu

# Check if it's legitimate or memory leak
kubectl logs <pod-name> -n todo-app

# Limit CPU
kubectl set resources deployment backend \
  --limits=cpu=500m --requests=cpu=250m \
  -n todo-app
```

### Response Slow

```bash
# Check database query performance
# Check if database is accessible from pod
# Check service endpoints
kubectl get endpoints -n todo-app

# If no endpoints:
# Service selector doesn't match pod labels
# Check both must match
```

---

## Escalation Path

**If you can't fix it yourself:**

1. **Collect Diagnostics**: Run commands from section 10
2. **Check Logs**: `kubectl logs` and `--previous`
3. **Check Events**: `kubectl get events -n todo-app`
4. **Try Rollback**: `helm rollback todo-app` if recent change caused issue
5. **Delete and Redeploy**: Last resort, nuke and rebuild

```bash
# Complete reset
helm uninstall todo-app -n todo-app
kubectl delete namespace todo-app
minikube delete
minikube start --cpus=4 --memory=4096
minikube addons enable metrics-server

# Redeploy from scratch
helm install todo-app helm/todo-app -n todo-app -f helm/todo-app/values-dev.yaml
```

---

## Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Troubleshooting](https://minikube.sigs.k8s.io/docs/handbook/troubleshooting/)
- [Docker Troubleshooting](https://docs.docker.com/config/daemon/)
- [Helm Troubleshooting](https://helm.sh/docs/helm/helm_get/)

