# Phase IV: Local Kubernetes Deployment Specification

**Phase**: IV (Local Kubernetes)  
**Status**: Not Started  
**Points**: 250  
**Due Date**: January 4, 2026  
**Dependencies**: Phase III (AI-Powered Todo Chatbot) must be complete

---

## Executive Summary

Phase IV transforms the containerized Todo Chatbot into a production-ready, cloud-native application deployed on a local Kubernetes cluster using Minikube. This phase introduces infrastructure-as-code practices, container orchestration, and intelligent DevOps tools.

### Phase IV Goals

1. **Containerization** - Docker containers for frontend and backend
2. **Kubernetes Deployment** - Deploy on Minikube with proper scaling
3. **Helm Chart Management** - Infrastructure-as-code with Helm
4. **AI-Assisted DevOps** - Use Gordon, kubectl-ai, and kagent for operations
5. **Local K8s Cluster** - Full working deployment on developer machine

---

## Objectives

### Primary Objective
Deploy the Phase III Todo Chatbot on a local Kubernetes cluster with:
- Containerized frontend (Next.js)
- Containerized backend (FastAPI + MCP)
- Persistent PostgreSQL database
- Health checks and auto-scaling
- Service discovery and load balancing

### Success Criteria
- [ ] Frontend and backend containerized and pushed to registry
- [ ] Minikube cluster running locally
- [ ] Helm charts created for all services
- [ ] Deployment succeeds with `helm install`
- [ ] All services accessible via kubectl port-forward
- [ ] Pods auto-restart on failure
- [ ] Resource limits configured properly
- [ ] kubectl-ai commands work for cluster management

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Containerization** | Docker Desktop | 4.53+ (with Gordon) |
| **Local K8s** | Minikube | Latest |
| **Container Registry** | Docker Hub / Local | - |
| **Package Manager** | Helm | 3.12+ |
| **AI DevOps Tools** | Gordon, kubectl-ai, kagent | Latest |
| **Orchestration** | Kubernetes | 1.28+ |
| **Monitoring** | kubectl logs, kubectl describe | Built-in |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Docker Desktop                    │
│  ┌──────────────────────────────────────────────┐   │
│  │            Minikube K8s Cluster              │   │
│  │                                               │   │
│  │  ┌──────────────┐      ┌──────────────┐      │   │
│  │  │  Frontend    │      │   Backend    │      │   │
│  │  │  Pod (N.js)  │      │  Pod (FastAPI)      │   │
│  │  │  :3000       │      │  + MCP       │      │   │
│  │  │              │      │  :8000       │      │   │
│  │  │  Replicas: 2 │      │  Replicas: 2 │      │   │
│  │  └──────────────┘      └──────────────┘      │   │
│  │           │                     │              │   │
│  │           └──────────────┬──────┘              │   │
│  │                          ▼                     │   │
│  │        ┌─────────────────────────┐             │   │
│  │        │    PostgreSQL Pod       │             │   │
│  │        │  (Neon Serverless)      │             │   │
│  │        │  Port: 5432             │             │   │
│  │        └─────────────────────────┘             │   │
│  │                                               │   │
│  │  Services:                                     │   │
│  │  - frontend-service (NodePort)                │   │
│  │  - backend-service (ClusterIP)                │   │
│  │  - postgres-service (ClusterIP)               │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  kubectl, Helm, Ingress Controller                  │
└─────────────────────────────────────────────────────┘
         Developer Machine (localhost)
```

---

## Deployment Flow

### 1. Build & Containerize (Using Gordon AI)
```
Phase III Code
    ↓
[Gordon] → Docker Containers
    ↓
Frontend Image (Next.js)
Backend Image (FastAPI + MCP)
    ↓
Docker Registry (Docker Hub or Local)
```

### 2. Create Helm Charts (Using kubectl-ai)
```
Service Manifests
    ↓
[kubectl-ai] → Helm Charts
    ↓
values.yaml (configurable)
templates/deployment.yaml
templates/service.yaml
templates/configmap.yaml
    ↓
Helm Package (Chart)
```

### 3. Deploy to Minikube
```
Helm Chart
    ↓
helm install my-todo-app ./chart
    ↓
Minikube K8s API
    ↓
Pods Running
Services Exposed
```

### 4. Manage with kubectl-ai & kagent
```
kubectl-ai "scale backend to 3 replicas"
kagent "analyze cluster health"
kubectl-ai "check pod logs for errors"
```

---

## Key Features for Phase IV

### Container Images
- **Frontend Container**: `todo-frontend:latest`
  - Based on Node.js 20 Alpine
  - PORT: 3000
  - Health check: GET /health

- **Backend Container**: `todo-backend:latest`
  - Based on Python 3.12 Alpine
  - PORT: 8000
  - Health check: GET /health

### Kubernetes Manifests

#### Deployments
- Frontend Deployment (2+ replicas)
- Backend Deployment (2+ replicas)
- PostgreSQL StatefulSet (1 replica) - for dev/testing only

#### Services
- Frontend Service (NodePort 30000)
- Backend Service (ClusterIP)
- PostgreSQL Service (ClusterIP)

#### ConfigMaps & Secrets
- App configuration (database URL, API keys)
- Database credentials

#### Resource Limits
- Frontend: CPU 100m-500m, Memory 128Mi-512Mi
- Backend: CPU 200m-1Gi, Memory 256Mi-1Gi
- PostgreSQL: CPU 100m-500m, Memory 256Mi-1Gi

### Helm Chart Structure
```
./helm/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
├── templates/
│   ├── deployment-frontend.yaml
│   ├── deployment-backend.yaml
│   ├── service-frontend.yaml
│   ├── service-backend.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── ingress.yaml (optional)
│   └── hpa.yaml (Horizontal Pod Autoscaler)
└── README.md
```

---

## User Stories

### User Story 1: Containerize Applications
**As** a DevOps engineer  
**I want** to package the Phase III app as Docker containers  
**So that** they can run consistently across environments

**Acceptance Criteria:**
- [ ] Frontend Dockerfile created and builds successfully
- [ ] Backend Dockerfile created and builds successfully
- [ ] Images pushed to Docker Hub or local registry
- [ ] Images tagged with version and latest
- [ ] Image sizes optimized (no unnecessary layers)

### User Story 2: Deploy to Minikube
**As** a developer  
**I want** to deploy the containerized app to a local Kubernetes cluster  
**So that** I can test cloud-native features locally

**Acceptance Criteria:**
- [ ] Minikube cluster starts without errors
- [ ] Helm chart installs successfully
- [ ] All pods reach "Running" state
- [ ] Services are accessible via port-forward
- [ ] Logs show no critical errors

### User Story 3: Use AI DevOps Tools
**As** a developer  
**I want** to use Gordon, kubectl-ai, and kagent for cluster management  
**So that** I can automate and understand Kubernetes operations

**Acceptance Criteria:**
- [ ] Gordon can build Docker images with AI assistance
- [ ] kubectl-ai successfully deploys Helm charts
- [ ] kagent analyzes cluster health
- [ ] kubectl-ai scales deployments on command
- [ ] All commands have documented usage

### User Story 4: Configure Health Checks & Auto-Scaling
**As** an operator  
**I want** Kubernetes to automatically restart failed pods  
**So that** the application remains available

**Acceptance Criteria:**
- [ ] Liveness probes configured for all pods
- [ ] Readiness probes configured for all pods
- [ ] Auto-restart happens within 30 seconds of failure
- [ ] HorizontalPodAutoscaler scales replicas (2-5)
- [ ] Scaling based on CPU usage > 70%

### User Story 5: Database Connectivity
**As** a developer  
**I want** PostgreSQL accessible from backend pods  
**So that** the app can persist data

**Acceptance Criteria:**
- [ ] PostgreSQL connection string works in pods
- [ ] Migrations run successfully in Kubernetes
- [ ] Data persists across pod restarts
- [ ] Database service discoverable via DNS

---

## Implementation Phases

### Phase IVa: Containerization (Days 1-3)
1. Create Dockerfile for frontend (Next.js)
2. Create Dockerfile for backend (FastAPI)
3. Build and test images locally
4. Push to Docker Hub (or use local registry)
5. Document image build process

### Phase IVb: Kubernetes Setup (Days 4-6)
1. Install Docker Desktop with Minikube support
2. Start Minikube cluster
3. Create namespace for app
4. Create ConfigMaps and Secrets
5. Test manual kubectl deployment of simple pod

### Phase IVc: Helm Charts (Days 7-9)
1. Create Helm chart structure
2. Create deployment templates for frontend/backend
3. Create service templates
4. Add resource limits and requests
5. Add health checks and probes
6. Test `helm install` and `helm upgrade`

### Phase IVd: AI DevOps Integration (Days 10-12)
1. Enable Gordon in Docker Desktop (Settings > Beta)
2. Test `docker ai` commands
3. Install kubectl-ai on system
4. Install kagent on system
5. Use tools to manage cluster operations

### Phase IVe: Testing & Validation (Days 13-14)
1. Run full deployment test
2. Simulate pod failure and verify restart
3. Test scaling up/down
4. Load test with multiple users
5. Document runbook for deployment

---

## Deliverables

### Code Artifacts
- [ ] `Dockerfile.frontend` - Optimized Next.js container
- [ ] `Dockerfile.backend` - Optimized FastAPI container
- [ ] `docker-compose.yml` - Local multi-container development
- [ ] `helm/Chart.yaml` - Helm chart metadata
- [ ] `helm/values.yaml` - Default configuration
- [ ] `helm/templates/` - All K8s manifests

### Documentation
- [ ] `specs/006-phase-4-kubernetes/DEPLOYMENT.md` - Step-by-step deployment guide
- [ ] `specs/006-phase-4-kubernetes/DEVOPS.md` - DevOps tool usage guide
- [ ] `specs/006-phase-4-kubernetes/TROUBLESHOOTING.md` - Common issues and fixes
- [ ] `helm/README.md` - Helm chart documentation

### Runbooks
- [ ] Deployment checklist
- [ ] Scaling procedures
- [ ] Monitoring & logging guide
- [ ] Rollback procedures

### Testing
- [ ] Integration tests for deployment
- [ ] Load test results
- [ ] Health check verification
- [ ] Failure recovery tests

---

## Success Metrics

| Metric | Target | Acceptance |
|--------|--------|-----------|
| **Deployment Time** | < 5 minutes | `helm install` to all pods ready |
| **Pod Startup Time** | < 30 seconds | Frontend and backend start |
| **Auto-Restart Time** | < 30 seconds | Pod restart to ready state |
| **CPU Usage** | < 500m per pod | Under typical load |
| **Memory Usage** | < 512Mi per pod | Under typical load |
| **Service Availability** | > 99.5% | No manual interventions needed |
| **Image Size** | < 500MB | Both frontend and backend |

---

## Prerequisites

- [ ] Phase III completely implemented and tested
- [ ] Docker Desktop installed (v4.53+ for Gordon)
- [ ] Git and GitHub account
- [ ] Docker Hub account (or local registry)
- [ ] Helm CLI installed
- [ ] kubectl CLI installed
- [ ] Minikube installed
- [ ] 8GB+ RAM available for Minikube
- [ ] 50GB+ free disk space

---

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Minikube resource limits | App crashes | Allocate 4GB RAM to Minikube |
| Image too large | Slow deployment | Use Alpine base images, multi-stage build |
| Database connection issues | Data loss | Use proper connection pooling |
| Pod restarts loop | Cascading failures | Implement readiness probes correctly |
| Helm syntax errors | Deployment fails | Validate with `helm lint` |

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Helm Docs](https://helm.sh/docs/)
- [Minikube Docs](https://minikube.sigs.k8s.io/)
- [kubectl-ai](https://github.com/sozercan/kubectl-ai)
- [kagent](https://github.com/bagel-ai/kagent)
- [Gordon (Docker AI)](https://www.docker.com/products/docker-desktop)
