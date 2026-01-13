# Phase IV: Research & Architecture

Exploration of Kubernetes, Docker, Helm, and DevOps tools for Phase IV implementation.

---

## 1. Container Architecture Decisions

### Base Images

#### Frontend (Next.js)
```dockerfile
FROM node:20-alpine
# Alternatives:
# - node:20-slim (smaller than full, larger than alpine)
# - node:20 (largest, most compatible)
```

**Decision**: Use `node:20-alpine`  
**Rationale**: 
- ~200MB vs 900MB (full image)
- Fast builds
- Sufficient for Next.js production

#### Backend (FastAPI)
```dockerfile
FROM python:3.12-alpine
# Alternatives:
# - python:3.12-slim
# - python:3.12
```

**Decision**: Use `python:3.12-alpine`  
**Rationale**:
- ~150MB base image
- Minimal dependencies needed
- Good C library support for psycopg2

### Multi-Stage Builds

**Frontend Example:**
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

# Runtime stage
FROM node:20-alpine
COPY --from=builder /app/node_modules ./node_modules
COPY . .
CMD ["npm", "start"]
```

**Benefit**: Reduces final image size by 50-70%

---

## 2. Kubernetes Architecture

### Cluster Architecture

```
┌─ Control Plane (Minikube)
│  ├─ API Server
│  ├─ Scheduler
│  ├─ Controller Manager
│  └─ etcd (data store)
│
└─ Worker Nodes
   └─ kubelet + kube-proxy + container runtime
```

### Pod Design

**Frontend Pod:**
- 1 container: Next.js app
- 1 replica minimum, 5 replicas max
- CPU: 100m-500m
- Memory: 128Mi-512Mi

**Backend Pod:**
- 1 container: FastAPI + MCP
- 1 replica minimum, 5 replicas max
- CPU: 200m-1000m
- Memory: 256Mi-1Gi

**Database Pod (optional):**
- 1 container: PostgreSQL
- 1 replica (StatefulSet)
- CPU: 100m-500m
- Memory: 256Mi-1Gi

### Service Discovery

```
Frontend Service (NodePort:30000)
    ↓
Frontend Pods (backend-service-svc.todo-app.svc.cluster.local:3000)
    ↓
Backend Service (ClusterIP:8000)
    ↓
Backend Pods → PostgreSQL Service (postgres:5432)
```

---

## 3. Helm Chart Strategy

### Chart Hierarchy

```
helm/todo-app/
├── Chart.yaml                 (metadata)
├── values.yaml                (defaults)
├── values-dev.yaml            (development overrides)
├── values-prod.yaml           (production overrides)
├── templates/
│   ├── _helpers.tpl           (macros)
│   ├── deployment-frontend.yaml
│   ├── deployment-backend.yaml
│   ├── service-frontend.yaml
│   ├── service-backend.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml
│   └── ingress.yaml (optional)
└── README.md
```

### Values Structure

```yaml
# values.yaml
frontend:
  image:
    repository: todo-frontend
    tag: latest
  replicas: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

backend:
  image:
    repository: todo-backend
    tag: latest
  replicas: 2
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi

database:
  url: postgresql://localhost:5432/todo_db
```

---

## 4. Health Check Strategy

### Liveness Probe (Restart if unhealthy)

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

**Timing:**
- Wait 10s for startup
- Check every 10s
- 3 failures = restart

### Readiness Probe (Remove from service if not ready)

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Timing:**
- Wait 5s for startup
- Check every 5s
- 2 failures = remove from service

---

## 5. Resource Management

### Resource Requests & Limits

**Why?**
- Requests: Scheduler guarantees minimum
- Limits: Container can't exceed
- Prevents resource starvation

**Recommendation:**

```yaml
resources:
  requests:
    cpu: 100m          # Minimum guaranteed
    memory: 128Mi      # Minimum guaranteed
  limits:
    cpu: 500m          # Maximum allowed
    memory: 512Mi      # Maximum allowed
```

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Scaling Logic:**
- Min 2 replicas always running
- Scale to 5 max if CPU > 70%
- Scale down if CPU < 70%

---

## 6. Container Registry Options

### Option 1: Docker Hub (Public)
```bash
docker tag todo-frontend:latest username/todo-frontend:latest
docker push username/todo-frontend:latest
```

**Pros:**
- Free tier available
- Easy to use
- Public sharing

**Cons:**
- Rate limiting (100 pulls per 6 hours, unauthenticated)
- Public by default

### Option 2: Minikube Local Registry (Dev)
```bash
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
# No push needed, images available in Minikube
```

**Pros:**
- No external dependencies
- Fast for development
- No rate limiting

**Cons:**
- Not usable from outside Minikube
- Images lost if Minikube deleted

### Option 3: GitHub Container Registry (Private)
```bash
docker tag todo-frontend ghcr.io/username/todo-frontend:latest
docker login ghcr.io
docker push ghcr.io/username/todo-frontend:latest
```

**Pros:**
- Free private storage
- GitHub integration
- GitHub Actions CI/CD

**Cons:**
- Requires authentication
- Slightly slower than Docker Hub

**Decision for Phase IV**: Use Option 2 (Minikube local) for dev, Option 1 (Docker Hub) for production-ready.

---

## 7. Persistent Data Strategy

### Kubernetes PersistentVolumes (PV)

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data"
```

### PersistentVolumeClaims (PVC)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### For Phase IV (Dev/Testing)

**Decision**: Use external Neon PostgreSQL (no K8s database)

**Rationale**:
- Simpler setup
- Persistent across Minikube restarts
- No StatefulSet complexity
- Production-like setup

---

## 8. Network Architecture

### Service Types

| Type | Use Case |
|------|----------|
| **ClusterIP** | Internal services (backend, database) |
| **NodePort** | External access in dev (frontend) |
| **LoadBalancer** | Production external access |
| **Ingress** | Production routing and SSL |

### DNS Service Discovery

```
Service Format: <service>.<namespace>.svc.cluster.local

Examples:
- backend-service.todo-app.svc.cluster.local:8000
- postgres.default.svc.cluster.local:5432
```

### Port-Forward for Development

```bash
kubectl port-forward svc/frontend 3000:3000 -n todo-app
# Client → localhost:3000 → K8s Service → Pod:3000
```

---

## 9. AI DevOps Tools Research

### Gordon (Docker AI)

**Status**: Available in Docker Desktop 4.53+  
**Capabilities**:
- Image optimization suggestions
- Dockerfile analysis
- Layer recommendations
- Multi-stage build generation

**Usage**:
```bash
docker ai "Optimize this Dockerfile"
docker ai "Analyze image layers"
```

### kubectl-ai

**Status**: Standalone CLI tool  
**Capabilities**:
- Generate kubectl commands from English
- Generate Kubernetes manifests
- Troubleshooting assistance
- Scaling and deployment automation

**Usage**:
```bash
kubectl-ai "deploy todo app"
kubectl-ai "scale backend to 3 replicas"
kubectl-ai "troubleshoot pod errors"
```

### kagent

**Status**: AI agent for Kubernetes  
**Capabilities**:
- Cluster health analysis
- Resource optimization
- Cost estimation
- Performance recommendations

**Usage**:
```bash
kagent "analyze cluster"
kagent "optimize resource usage"
kagent "estimate costs"
```

---

## 10. Load Testing Strategy

### Tool: Apache JMeter (or k6, Locust)

**Scenarios**:
1. **Smoke Test**: 5 users, 1 minute
2. **Load Test**: 50 users, 5 minutes
3. **Stress Test**: 200 users until failure

**Metrics to Track**:
- Response time (avg, p95, p99)
- Throughput (requests/second)
- Error rate
- Pod CPU/Memory usage
- Pod replica scaling behavior

**Success Criteria**:
- p95 response time < 1000ms
- Error rate < 5%
- Auto-scaling triggers correctly
- No data loss during scaling

---

## 11. Minikube Optimization

### Resource Allocation

```bash
# Default
minikube start --cpus=2 --memory=2048

# Optimized for Phase IV
minikube start --cpus=4 --memory=4096

# Maximum
minikube start --cpus=8 --memory=8192
```

### Addons

```bash
# Enable ingress (optional)
minikube addons enable ingress

# Enable metrics-server (for HPA)
minikube addons enable metrics-server

# View addons
minikube addons list
```

### Docker Registry Access

```bash
# Option 1: Use Minikube's Docker daemon
eval $(minikube docker-env)

# Option 2: Configure Docker Hub credentials
kubectl create secret docker-registry regcred \
  --docker-server=docker.io \
  --docker-username=<username> \
  --docker-password=<token>
```

---

## 12. Logging & Monitoring Strategy

### Logging

```bash
# View logs
kubectl logs deployment/backend -n todo-app

# Stream logs
kubectl logs deployment/backend -n todo-app -f

# Multi-container logs
kubectl logs deployment/backend -n todo-app --all-containers
```

### Monitoring Metrics

```bash
# CPU and Memory usage
kubectl top pods -n todo-app

# Node metrics
kubectl top nodes
```

### Advanced: Prometheus + Grafana (Optional)

```bash
# Install via Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
```

---

## 13. Security Considerations

### Pod Security Policy

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'MustRunAs'
    seLinuxOptions:
      level: "s0:c123,c456"
  supplementalGroups:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: false
```

### Network Policy (Optional)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8000
```

---

## 14. Rollback Strategy

### Helm Rollback

```bash
# List releases
helm history todo-app -n todo-app

# Rollback to previous
helm rollback todo-app -n todo-app

# Rollback to specific revision
helm rollback todo-app 1 -n todo-app
```

### Kubernetes Rollout

```bash
# Check rollout status
kubectl rollout status deployment/backend -n todo-app

# Undo rollout
kubectl rollout undo deployment/backend -n todo-app

# Undo to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n todo-app
```

---

## 15. Key Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Base Image (Frontend) | node:20-alpine | Small, fast |
| Base Image (Backend) | python:3.12-alpine | Small, fast |
| Multi-Stage Build | Yes | Reduces image size 50-70% |
| Container Registry | Minikube (dev), Docker Hub (prod) | Fast dev, accessible prod |
| Database | Neon PostgreSQL (external) | Persistent, simplified |
| Service Discovery | DNS (ClusterIP + names) | Standard, reliable |
| HPA | CPU > 70% trigger | Responsive scaling |
| Logging | kubectl logs | Simple, sufficient for dev |
| AI Tools | Gordon + kubectl-ai + kagent | Comprehensive automation |

---

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
