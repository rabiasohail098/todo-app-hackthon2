# Phase IV: Pre/Post Deployment Checklist

Use this checklist to ensure successful Kubernetes deployment of the Todo App.

---

## 1. Pre-Deployment Checklist

Complete these items before deploying to Minikube.

### 1.1 Environment & Prerequisites

- [ ] **Docker Desktop installed**
  ```bash
  docker --version  # Should be 4.53 or higher
  ```

- [ ] **Minikube installed**
  ```bash
  minikube version  # Should be latest
  ```

- [ ] **kubectl installed**
  ```bash
  kubectl version --client
  ```

- [ ] **Helm installed**
  ```bash
  helm version  # Should be 3.12 or higher
  ```

- [ ] **Git latest changes pulled**
  ```bash
  git status  # Should be clean or have only expected changes
  ```

### 1.2 Code & Configuration

- [ ] **Backend requirements installed**
  ```bash
  cd backend
  pip install -r requirements.txt
  python -m pytest tests/ -v  # All tests pass
  ```

- [ ] **Frontend dependencies installed**
  ```bash
  cd frontend
  npm install
  npm run build  # No build errors
  npm test  # All tests pass (or skip if none)
  ```

- [ ] **Environment variables configured**
  ```bash
  # Backend - check if all required vars are set
  grep -r "os.getenv" backend/src/ | cut -d: -f2 | sort -u
  
  # Frontend - check NEXT_PUBLIC vars
  grep -r "process.env" frontend/app/ frontend/lib/
  ```

- [ ] **Database connection tested**
  ```bash
  # Test with local PostgreSQL or verify Neon credentials
  psql $DATABASE_URL -c "SELECT 1"  # Should work
  ```

### 1.3 Docker Images

- [ ] **Frontend image builds without errors**
  ```bash
  docker build -t todo-frontend:latest ./frontend
  docker images | grep todo-frontend  # Should exist
  ```

- [ ] **Backend image builds without errors**
  ```bash
  docker build -t todo-backend:latest ./backend
  docker images | grep todo-backend  # Should exist
  ```

- [ ] **Images run locally without errors**
  ```bash
  # Backend test
  docker run --rm -p 8000:8000 todo-backend:latest &
  sleep 2
  curl http://localhost:8000/health  # Should return 200
  kill %1
  
  # Frontend test
  docker run --rm -p 3000:3000 todo-frontend:latest &
  sleep 2
  curl http://localhost:3000  # Should return HTML
  kill %1
  ```

- [ ] **Image sizes are reasonable**
  ```bash
  docker images | grep todo-
  # Frontend should be <500MB
  # Backend should be <300MB
  ```

### 1.4 Helm Chart

- [ ] **Helm chart passes validation**
  ```bash
  helm lint helm/todo-app
  # Should show 0 warnings and 0 errors
  ```

- [ ] **Chart renders without errors**
  ```bash
  helm template todo-app helm/todo-app
  # Should show YAML manifests
  ```

- [ ] **Chart values are correct**
  ```bash
  # Check frontend replicas and resources
  grep -A 5 "frontend:" helm/todo-app/values.yaml
  
  # Check backend replicas and resources
  grep -A 5 "backend:" helm/todo-app/values.yaml
  ```

- [ ] **Development values file exists**
  ```bash
  test -f helm/todo-app/values-dev.yaml && echo "OK"
  ```

- [ ] **Production values file exists**
  ```bash
  test -f helm/todo-app/values-prod.yaml && echo "OK"
  ```

### 1.5 Configuration & Secrets

- [ ] **ConfigMap contains all required variables**
  ```bash
  grep -A 20 "kind: ConfigMap" helm/todo-app/templates/configmap.yaml
  # Should include: LOG_LEVEL, CORS_ORIGINS, JWT_SECRET, etc.
  ```

- [ ] **Secret template has required fields**
  ```bash
  grep -A 20 "kind: Secret" helm/todo-app/templates/secret.yaml
  # Should include: DATABASE_URL, OPENAI_API_KEY, Cloudinary creds
  ```

- [ ] **Database credentials available**
  ```bash
  # For Neon PostgreSQL:
  # Should have DATABASE_URL environment variable
  echo $DATABASE_URL | grep postgresql  # Should work
  ```

### 1.6 Documentation

- [ ] **All spec files present**
  ```bash
  ls -la specs/006-phase-4-kubernetes/
  # Should include: spec.md, plan.md, tasks.md, quickstart.md, 
  # research.md, data-model.md, DEPLOYMENT.md, DEVOPS.md, TROUBLESHOOTING.md
  ```

- [ ] **README.md updated with Phase 4 reference**
  ```bash
  grep -i "phase 4\|kubernetes" README.md
  ```

- [ ] **Dockerfiles documented**
  ```bash
  head -20 frontend/Dockerfile  # Should have comments
  head -20 backend/Dockerfile   # Should have comments
  ```

---

## 2. Deployment Checklist

Complete these items during deployment.

### 2.1 Start Minikube

- [ ] **Minikube starting successfully**
  ```bash
  minikube start --cpus=4 --memory=4096
  # Should show "Done! kubectl is now configured..."
  ```

- [ ] **kubectl connected to Minikube**
  ```bash
  kubectl cluster-info
  # Should show "Kubernetes master is running at..."
  ```

- [ ] **Node is ready**
  ```bash
  kubectl get nodes
  # Should show STATUS: Ready
  ```

### 2.2 Configure Minikube

- [ ] **Metrics server addon enabled**
  ```bash
  minikube addons enable metrics-server
  kubectl get deployment metrics-server -n kube-system
  # Should be running
  ```

- [ ] **Minikube dashboard available (optional)**
  ```bash
  minikube dashboard &  # Opens web dashboard
  ```

### 2.3 Load Docker Images

- [ ] **Images loaded into Minikube**
  ```bash
  minikube image load todo-frontend:latest
  minikube image load todo-backend:latest
  
  # Verify
  minikube image ls | grep todo-
  ```

- [ ] **Images accessible from Minikube**
  ```bash
  kubectl run test-image --image=todo-frontend:latest --restart=Never --rm -it -- echo "OK"
  # Should complete successfully
  ```

### 2.4 Create Namespace

- [ ] **Namespace created**
  ```bash
  kubectl create namespace todo-app
  # Or should be created by Helm
  kubectl get namespace todo-app
  ```

- [ ] **Namespace default context set (optional)**
  ```bash
  kubectl config set-context --current --namespace=todo-app
  ```

### 2.5 Create Secrets

- [ ] **Database secret created**
  ```bash
  kubectl create secret generic app-secret \
    --from-literal=DATABASE_URL="$DATABASE_URL" \
    -n todo-app
  
  # Verify
  kubectl get secret app-secret -n todo-app
  ```

- [ ] **API keys secret created**
  ```bash
  kubectl create secret generic api-keys \
    --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
    --from-literal=CLOUDINARY_CLOUD_NAME="$CLOUDINARY_CLOUD_NAME" \
    --from-literal=CLOUDINARY_API_KEY="$CLOUDINARY_API_KEY" \
    --from-literal=CLOUDINARY_API_SECRET="$CLOUDINARY_API_SECRET" \
    -n todo-app
  
  # Verify
  kubectl get secret api-keys -n todo-app
  ```

### 2.6 Deploy Helm Chart

- [ ] **Helm install without errors**
  ```bash
  helm install todo-app helm/todo-app -n todo-app \
    -f helm/todo-app/values-dev.yaml
  # Should show: "STATUS: deployed"
  ```

- [ ] **Release status is deployed**
  ```bash
  helm status todo-app -n todo-app
  # Should show STATUS: deployed
  ```

- [ ] **All release resources created**
  ```bash
  helm get manifest todo-app -n todo-app | head -20
  # Should show created resources
  ```

### 2.7 Verify Pods

- [ ] **All pods are running**
  ```bash
  kubectl get pods -n todo-app
  # All pods should show STATUS: Running
  # READY should be 1/1 or correct count
  ```

- [ ] **Pods didn't restart**
  ```bash
  kubectl get pods -n todo-app --sort-by='.status.containerStatuses[0].restartCount'
  # RESTARTS column should show 0 for all
  ```

- [ ] **No pods in error state**
  ```bash
  kubectl get pods -n todo-app
  # Should show no: ImagePullBackOff, CrashLoopBackOff, Pending, Evicted
  ```

- [ ] **Pod startup times reasonable**
  ```bash
  kubectl get pods -n todo-app -o wide
  # AGE column should show recent times (not stuck)
  ```

### 2.8 Verify Services

- [ ] **Services are created**
  ```bash
  kubectl get services -n todo-app
  # Should show: frontend, backend services
  ```

- [ ] **Services have endpoints**
  ```bash
  kubectl get endpoints -n todo-app
  # frontend and backend endpoints should list pod IPs
  ```

- [ ] **Service types are correct**
  ```bash
  kubectl get services -n todo-app -o wide
  # frontend: NodePort or LoadBalancer
  # backend: ClusterIP
  ```

### 2.9 Verify ConfigMap & Secrets

- [ ] **ConfigMap created**
  ```bash
  kubectl get configmap -n todo-app
  # Should have app-config or similar
  ```

- [ ] **Secrets created**
  ```bash
  kubectl get secrets -n todo-app
  # Should have DATABASE_URL and API_KEYS secrets
  ```

- [ ] **ConfigMap mounted in pods**
  ```bash
  kubectl describe pod <frontend-pod> -n todo-app | grep Mounts
  # Should show config volume mounted
  ```

---

## 3. Post-Deployment Checklist

Verify application works after deployment.

### 3.1 Network Connectivity

- [ ] **Port-forward frontend**
  ```bash
  kubectl port-forward service/frontend 3000:3000 -n todo-app &
  sleep 2
  # Should show "Forwarding from 127.0.0.1:3000 -> 3000"
  ```

- [ ] **Frontend responds**
  ```bash
  curl http://localhost:3000
  # Should return HTML content (not error)
  ```

- [ ] **Port-forward backend**
  ```bash
  kubectl port-forward service/backend 8000:8000 -n todo-app &
  sleep 2
  # Should show "Forwarding from 127.0.0.1:8000 -> 8000"
  ```

- [ ] **Backend health check**
  ```bash
  curl http://localhost:8000/health
  # Should return {"status": "healthy"} or similar
  ```

### 3.2 Application Functionality

- [ ] **Frontend loads in browser**
  ```bash
  # Open http://localhost:3000
  # Should show todo app interface
  # No "Connection refused" errors
  ```

- [ ] **Frontend can reach backend**
  ```bash
  # In browser console (F12):
  # Check Network tab - API calls should return 200
  # Check Console - no "CORS" errors
  ```

- [ ] **Create todo works**
  ```bash
  # Add a new todo via UI
  # Should appear in list without errors
  ```

- [ ] **Todos persist**
  ```bash
  # Refresh page
  # Previously created todos should still be there
  ```

- [ ] **Chat feature works (if configured)**
  ```bash
  # Try sending a message
  # Should get response from backend
  # Check for any error messages
  ```

### 3.3 Logs & Monitoring

- [ ] **No error logs in frontend**
  ```bash
  kubectl logs <frontend-pod> -n todo-app
  # Should not contain ERROR or Exception
  ```

- [ ] **No error logs in backend**
  ```bash
  kubectl logs <backend-pod> -n todo-app
  # Should not contain ERROR or Exception
  ```

- [ ] **Database connection successful**
  ```bash
  kubectl logs <backend-pod> -n todo-app | grep -i database
  # Should show connection successful
  # Should NOT show "Connection refused"
  ```

- [ ] **Resource usage is reasonable**
  ```bash
  kubectl top pods -n todo-app
  # CPU: Each pod <500m (ideally <250m)
  # Memory: Each pod <500Mi (ideally <256Mi)
  ```

### 3.4 Health Checks

- [ ] **Liveness probes passing**
  ```bash
  kubectl get pods -n todo-app -o custom-columns=NAME:.metadata.name,READY:.status.conditions[?(@.type=="Ready")].status
  # All should show: NAME    READY
  #                 ...     True
  ```

- [ ] **Readiness probes passing**
  ```bash
  # Use kubectl describe instead
  kubectl describe pod <pod-name> -n todo-app | grep -A 5 "Readiness"
  # Should show: Readiness: ... success count 3
  ```

- [ ] **Pod endpoints active**
  ```bash
  kubectl get endpoints -n todo-app
  # All pods should be listed in endpoints
  ```

### 3.5 Persistence & State

- [ ] **Todos survive pod restart**
  ```bash
  # Create a todo
  # Delete the backend pod
  kubectl delete pod <backend-pod> -n todo-app
  # Pod will auto-restart
  # Todos should still exist
  ```

- [ ] **Database connection state preserved**
  ```bash
  # App should continue working after pod restart
  # No "database connection refused" errors
  ```

---

## 4. Scaling & Load Testing Checklist

Verify auto-scaling and high availability.

### 4.1 Manual Scaling

- [ ] **Can scale frontend up**
  ```bash
  kubectl scale deployment frontend --replicas=3 -n todo-app
  kubectl get deployment frontend -n todo-app
  # READY should show 3/3
  ```

- [ ] **Can scale backend up**
  ```bash
  kubectl scale deployment backend --replicas=3 -n todo-app
  kubectl get deployment backend -n todo-app
  # READY should show 3/3
  ```

- [ ] **All pods serve traffic**
  ```bash
  # Load test or repeated requests
  for i in {1..10}; do curl http://localhost:3000; done
  # Should get quick responses
  ```

- [ ] **Can scale down**
  ```bash
  kubectl scale deployment frontend --replicas=1 -n todo-app
  kubectl scale deployment backend --replicas=1 -n todo-app
  # Should return to 1/1
  ```

### 4.2 Auto-Scaling Configuration (Optional)

- [ ] **HPA is created**
  ```bash
  kubectl get hpa -n todo-app
  # Should list frontend and backend HPA
  ```

- [ ] **HPA scaling rules correct**
  ```bash
  kubectl describe hpa frontend -n todo-app | grep -A 10 "Metrics"
  # Should show CPU threshold (70%)
  # Should show min/max replicas (2-5)
  ```

- [ ] **Metrics server running**
  ```bash
  kubectl get deployment metrics-server -n kube-system
  # Should show READY 1/1
  ```

### 4.3 Load Testing (Optional)

- [ ] **Simple load test passes**
  ```bash
  # Use Apache Bench or k6
  ab -n 100 -c 10 http://localhost:3000/
  # Should show reasonable response times
  # Should not show connection failures
  ```

- [ ] **No pod crashes under load**
  ```bash
  # During/after load test
  kubectl get pods -n todo-app
  # All pods should still be Running
  # RESTARTS should not increase
  ```

- [ ] **Memory doesn't leak**
  ```bash
  # Monitor memory during load test
  watch -n 1 'kubectl top pods -n todo-app'
  # Memory should stabilize, not continuously increase
  ```

---

## 5. Production Readiness Checklist

Before moving to production environment.

### 5.1 Security

- [ ] **Secrets are not in code**
  ```bash
  grep -r "PASSWORD\|SECRET\|KEY" . --include="*.yaml" --include="*.yml"
  # Should not find secrets, only placeholder references
  ```

- [ ] **Image pull secrets configured**
  ```bash
  kubectl get secrets -n todo-app | grep pull
  # If using private registry, should exist
  ```

- [ ] **RBAC configured**
  ```bash
  kubectl get rolebindings -n todo-app
  # Should have minimal RBAC rules
  ```

- [ ] **Network policies optional**
  ```bash
  kubectl get networkpolicies -n todo-app
  # Should exist for production (optional for dev)
  ```

### 5.2 Reliability

- [ ] **Pod disruption budgets (optional)**
  ```bash
  kubectl get pdb -n todo-app
  # Should exist for production (optional for dev)
  ```

- [ ] **Resource limits are set**
  ```bash
  kubectl get deployment frontend -n todo-app -o yaml | grep -A 5 "limits:"
  # Should have CPU and memory limits
  ```

- [ ] **Multiple replicas configured**
  ```bash
  kubectl get deployment -n todo-app
  # Frontend and backend should have 3+ replicas
  ```

### 5.3 Monitoring & Logging

- [ ] **Pod logs accessible**
  ```bash
  kubectl logs <pod-name> -n todo-app
  # Should be readable and informative
  ```

- [ ] **Metrics collection working**
  ```bash
  kubectl top pods -n todo-app
  # Should show metrics, not "Unable to calculate"
  ```

- [ ] **Events tracked**
  ```bash
  kubectl get events -n todo-app
  # Should show recent events
  ```

### 5.4 Upgrade Path

- [ ] **Helm values-prod.yaml configured**
  ```bash
  test -f helm/todo-app/values-prod.yaml && echo "OK"
  ```

- [ ] **Can perform zero-downtime upgrade**
  ```bash
  # Test with development first
  helm upgrade todo-app helm/todo-app -n todo-app \
    -f helm/todo-app/values-prod.yaml --dry-run
  # Should succeed without --dry-run too
  ```

- [ ] **Rollback procedure documented**
  ```bash
  grep -r "rollback\|revert" specs/006-phase-4-kubernetes/
  # Should have documented procedure
  ```

---

## 6. Post-Deployment Issues Troubleshooting

If something goes wrong, follow this checklist.

### 6.1 Pod Won't Start

- [ ] **Check pod status**
  ```bash
  kubectl describe pod <pod-name> -n todo-app
  # Look at "Events" section for error
  ```

- [ ] **Check container logs**
  ```bash
  kubectl logs <pod-name> -n todo-app
  # Look for "Error" or exception messages
  ```

- [ ] **Check resource availability**
  ```bash
  kubectl top nodes
  # Check if enough CPU/memory available
  ```

### 6.2 Service Not Responding

- [ ] **Check service exists**
  ```bash
  kubectl get service -n todo-app
  # Service should be listed
  ```

- [ ] **Check endpoints**
  ```bash
  kubectl get endpoints -n todo-app
  # Should list pod IPs
  ```

- [ ] **Test from within pod**
  ```bash
  kubectl exec -it <pod> -n todo-app -- curl http://backend:8000
  # Should work if service is properly configured
  ```

### 6.3 Application Not Responding

- [ ] **Check logs for errors**
  ```bash
  kubectl logs <pod-name> -n todo-app
  # Look for specific errors
  ```

- [ ] **Restart pod**
  ```bash
  kubectl delete pod <pod-name> -n todo-app
  # Pod will auto-restart
  ```

- [ ] **Check environment variables**
  ```bash
  kubectl exec -it <pod> -n todo-app -- env | sort
  # Verify all required vars are present
  ```

---

## Quick Reference Commands

```bash
# Get all resources in namespace
kubectl get all -n todo-app

# Describe everything
kubectl describe all -n todo-app

# View logs
kubectl logs <pod> -n todo-app -f

# Execute command in pod
kubectl exec -it <pod> -n todo-app -- /bin/sh

# Port forward
kubectl port-forward service/<service> <port>:<port> -n todo-app

# Check resource usage
kubectl top pods -n todo-app
kubectl top nodes

# Helm commands
helm status todo-app -n todo-app
helm get values todo-app -n todo-app
helm rollback todo-app -n todo-app

# Scale deployment
kubectl scale deployment <name> --replicas=N -n todo-app
```

---

## Sign-Off

- [ ] **Deployment completed successfully**
- [ ] **All checklist items verified**
- [ ] **Application tested and working**
- [ ] **Team notified of deployment**
- [ ] **Documentation updated**

Date: ________________
Deployed By: ________________
Reviewed By: ________________

