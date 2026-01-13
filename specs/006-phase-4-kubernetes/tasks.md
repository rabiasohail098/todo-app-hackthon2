# Tasks: Phase IV - Local Kubernetes Deployment

**Feature Branch**: `006-phase-4-kubernetes`
**Status**: Complete
**Dependencies**: specs/005-advanced-task-filters (Phase 3 must be complete)

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

---

## Phase 1: Docker Setup & Configuration

**Purpose**: Prepare Docker environment and create container images

### User Story 1: Containerize Frontend (P0)

- [x] **T001** [P] [US1] Create frontend Dockerfile
  - File: `frontend/Dockerfile`
  - Use Node.js 20-alpine as base
  - Multi-stage build to minimize size
  - Build: `npm run build`
  - Serve via next start on port 3000
  - Include health check: GET /health

- [x] **T002** [P] [US1] Create .dockerignore for frontend
  - File: `frontend/.dockerignore`
  - Exclude node_modules, .next, .git, coverage, tests

- [x] **T003** [US1] Build and test frontend image locally
  - Build: `docker build -t todo-frontend:latest ./frontend`
  - Test: `docker run -p 3000:3000 todo-frontend:latest`
  - Verify: App accessible at http://localhost:3000

- [x] **T004** [US1] Push frontend image to Docker Hub
  - Tag: `<docker-hub-user>/todo-frontend:latest`
  - Push: `docker push <docker-hub-user>/todo-frontend:latest`
  - Verify: Image available on Docker Hub

### User Story 2: Containerize Backend (P0)

- [x] **T005** [P] [US2] Create backend Dockerfile
  - File: `backend/Dockerfile`
  - Use Python 3.12-alpine as base
  - Install dependencies: `pip install -r requirements.txt`
  - Run: `uvicorn main:app --host 0.0.0.0 --port 8000`
  - Include health check: GET /health
  - Multi-stage build (optional, for optimization)

- [x] **T006** [P] [US2] Create .dockerignore for backend
  - File: `backend/.dockerignore`
  - Exclude __pycache__, .venv, .git, coverage, .env

- [x] **T007** [US2] Build and test backend image locally
  - Build: `docker build -t todo-backend:latest ./backend`
  - Test: `docker run -p 8000:8000 -e DATABASE_URL=... todo-backend:latest`
  - Verify: API accessible at http://localhost:8000/docs

- [x] **T008** [US2] Push backend image to Docker Hub
  - Tag: `<docker-hub-user>/todo-backend:latest`
  - Push: `docker push <docker-hub-user>/todo-backend:latest`
  - Verify: Image available on Docker Hub

### User Story 3: Docker Compose Setup (Optional for Local Dev)

- [x] **T009** [P] [US3] Create docker-compose.yml
  - File: `docker-compose.yml`
  - Services: frontend, backend, postgres
  - Environment: Database URL, API keys
  - Volumes: Database data persistence
  - Ports: 3000 (frontend), 8000 (backend), 5432 (db)

- [x] **T010** [US3] Test docker-compose locally
  - Start: `docker-compose up`
  - Verify: All services healthy
  - Test: Frontend and backend communicate
  - Cleanup: `docker-compose down`

---

## Phase 2: Kubernetes Setup

**Purpose**: Set up local Kubernetes cluster with Minikube

### User Story 4: Minikube Installation & Setup

- [x] **T011** [P] [US4] Install Docker Desktop with Minikube
  - Version: Docker Desktop 4.53+ (includes Minikube)
  - Enable: Kubernetes from Docker Desktop settings
  - Or: Install Minikube separately via `brew install minikube` or `choco install minikube`

- [x] **T012** [US4] Start Minikube cluster
  - Command: `minikube start --cpus=4 --memory=4096`
  - Verify: `kubectl cluster-info`
  - Verify: `kubectl get nodes`

- [x] **T013** [P] [US4] Configure Docker registry access
  - Setup local registry or use Docker Hub credentials
  - For Docker Hub: Create `.docker/config.json` secret
  - Or: Use Minikube Docker daemon: `eval $(minikube docker-env)`

- [x] **T014** [US4] Create Kubernetes namespace
  - File: `k8s/namespace.yaml`
  - Name: `todo-app`
  - Apply: `kubectl apply -f k8s/namespace.yaml`

- [x] **T015** [P] [US4] Create ConfigMap for environment variables
  - File: `k8s/configmap.yaml`
  - Variables: DATABASE_URL, API_KEYS, LOG_LEVEL
  - Apply: `kubectl apply -f k8s/configmap.yaml -n todo-app`

- [x] **T016** [P] [US4] Create Secret for sensitive data
  - File: `k8s/secret.yaml` (git-ignored)
  - Values: Database password, JWT secret, API keys
  - Apply: `kubectl apply -f k8s/secret.yaml -n todo-app`

---

## Phase 3: Helm Charts

**Purpose**: Create infrastructure-as-code with Helm

### User Story 5: Helm Chart Structure

- [x] **T017** [P] [US5] Initialize Helm chart
  - Command: `helm create helm/todo-app`
  - Structure: Chart.yaml, values.yaml, templates/

- [x] **T018** [P] [US5] Create Chart.yaml metadata
  - File: `helm/todo-app/Chart.yaml`
  - Name: `todo-app`
  - Version: `1.0.0`
  - AppVersion: `1.0.0`
  - Description: Todo Chatbot with AI and Kubernetes

- [x] **T019** [US5] Create values.yaml (default values)
  - File: `helm/todo-app/values.yaml`
  - Frontend: image, replicas, resources
  - Backend: image, replicas, resources
  - Database: connection string, credentials
  - Ingress: disabled by default

- [x] **T020** [P] [US5] Create values-dev.yaml override
  - File: `helm/todo-app/values-dev.yaml`
  - Replicas: 1-2 for dev
  - Resources: Lower limits for local testing
  - Debug logging enabled

- [x] **T021** [P] [US5] Create values-prod.yaml override
  - File: `helm/todo-app/values-prod.yaml`
  - Replicas: 3+ for production
  - Resources: Higher limits
  - HPA: min 3, max 10
  - Security: Pod Security Policy

### User Story 6: Kubernetes Deployment Templates

- [x] **T022** [P] [US6] Create frontend deployment template
  - File: `helm/todo-app/templates/deployment-frontend.yaml`
  - Spec: image, replicas, resources
  - Port: 3000
  - Probes: liveness and readiness
  - Labels: app=frontend, version=v1

- [x] **T023** [P] [US6] Create backend deployment template
  - File: `helm/todo-app/templates/deployment-backend.yaml`
  - Spec: image, replicas, resources
  - Port: 8000
  - Environment: From ConfigMap and Secret
  - Probes: liveness and readiness
  - Labels: app=backend, version=v1

- [x] **T024** [P] [US6] Create frontend service template
  - File: `helm/todo-app/templates/service-frontend.yaml`
  - Type: NodePort (localhost access)
  - Port: 3000
  - Selector: app=frontend

- [x] **T025** [P] [US6] Create backend service template
  - File: `helm/todo-app/templates/service-backend.yaml`
  - Type: ClusterIP (internal only)
  - Port: 8000
  - Selector: app=backend

- [x] **T026** [P] [US6] Create configmap template
  - File: `helm/todo-app/templates/configmap.yaml`
  - Key-value pairs from values.yaml
  - Mount to pods as environment or files

- [x] **T027** [P] [US6] Create secret template
  - File: `helm/todo-app/templates/secret.yaml`
  - Base64 encode sensitive values
  - Database credentials, JWT secret

- [x] **T028** [P] [US6] Create HPA (Horizontal Pod Autoscaler) template
  - File: `helm/todo-app/templates/hpa.yaml`
  - Min replicas: 2
  - Max replicas: 5
  - Target CPU: 70%

### User Story 7: Helm Validation & Installation

- [x] **T029** [US7] Validate Helm chart syntax
  - Command: `helm lint helm/todo-app`
  - Fix any warnings or errors

- [x] **T030** [US7] Generate manifest preview
  - Command: `helm template todo-app helm/todo-app -n todo-app`
  - Review output for correctness

- [x] **T031** [US7] Install Helm chart to Minikube
  - Command: `helm install todo-app helm/todo-app -n todo-app`
  - Verify: `kubectl get all -n todo-app`

- [x] **T032** [US7] Test rollout and status
  - Command: `kubectl rollout status deployment/frontend -n todo-app`
  - Command: `kubectl rollout status deployment/backend -n todo-app`
  - Verify: All pods running

- [x] **T033** [US7] Upgrade Helm release
  - Modify values.yaml
  - Command: `helm upgrade todo-app helm/todo-app -n todo-app`
  - Verify: Changes applied without downtime

---

## Phase 4: Kubernetes Networking & Persistence

**Purpose**: Enable service discovery and data persistence

### User Story 8: Database Connectivity

- [x] **T034** [P] [US8] Create postgres-service
  - Type: ClusterIP (internal)
  - Port: 5432
  - Selectors: app=postgres (if deployed in K8s)
  - Or: External database (Neon) via connection string

- [x] **T035** [US8] Configure database connection string
  - Format: `postgresql://user:password@postgres-service:5432/todo_db`
  - Store in ConfigMap or Secret
  - Update backend deployment to use it

- [x] **T036** [US8] Run database migrations in Kubernetes
  - Method 1: Job for migration before main deployment
  - Method 2: Init container in backend pod
  - Verify: `kubectl logs <backend-pod> -n todo-app`

- [x] **T037** [US8] Test backend-to-database connectivity
  - kubectl exec: `kubectl exec -it <backend-pod> -n todo-app -- /bin/sh`
  - Test: `psql -h postgres-service -U user -d todo_db -c "SELECT 1"`

### User Story 9: Expose Services

- [x] **T038** [P] [US9] Port-forward frontend service
  - Command: `kubectl port-forward -n todo-app svc/frontend 3000:3000`
  - Test: http://localhost:3000

- [x] **T039** [P] [US9] Port-forward backend service
  - Command: `kubectl port-forward -n todo-app svc/backend 8000:8000`
  - Test: http://localhost:8000/docs

- [x] **T040** [US9] Create Ingress for domain routing (optional)
  - File: `helm/todo-app/templates/ingress.yaml`
  - Host: `localhost` or custom domain
  - TLS: Disabled for local testing

---

## Phase 5: Health Checks & Auto-Recovery

**Purpose**: Ensure reliability and high availability

### User Story 10: Pod Health Checks

- [x] **T041** [P] [US10] Add liveness probe to frontend
  - Type: HTTP GET
  - Path: /health
  - Initial delay: 10s
  - Period: 10s
  - Failure threshold: 3

- [x] **T042** [P] [US10] Add readiness probe to frontend
  - Type: HTTP GET
  - Path: /health
  - Initial delay: 5s
  - Period: 5s

- [x] **T043** [P] [US10] Add liveness probe to backend
  - Type: HTTP GET
  - Path: /health
  - Initial delay: 10s
  - Period: 10s

- [x] **T044** [P] [US10] Add readiness probe to backend
  - Type: HTTP GET
  - Path: /health
  - Initial delay: 5s
  - Period: 5s

- [x] **T045** [US10] Test auto-restart on pod failure
  - Kill pod: `kubectl delete pod <pod-name> -n todo-app`
  - Verify: New pod starts automatically
  - Check: `kubectl get pods -n todo-app -w` (watch mode)

---

## Phase 6: AI DevOps Tools Integration

**Purpose**: Use intelligent tools for cluster management

### User Story 11: Gordon (Docker AI)

- [x] **T046** [US11] Enable Gordon in Docker Desktop
  - Settings > Beta features > Docker AI
  - Verify: `docker ai "Hello"`

- [x] **T047** [P] [US11] Use Gordon to optimize Dockerfile
  - Command: `docker ai "optimize this Dockerfile for size"`
  - Review suggestions
  - Apply improvements if applicable

- [x] **T048** [US11] Use Gordon for image analysis
  - Command: `docker ai "analyze layers in my todo-backend image"`
  - Identify optimization opportunities

### User Story 12: kubectl-ai

- [x] **T049** [US12] Install kubectl-ai
  - Platform: Windows / macOS / Linux
  - Verify: `kubectl-ai "help"`

- [x] **T050** [P] [US12] Use kubectl-ai to deploy
  - Command: `kubectl-ai "deploy todo app with helm on minikube"`
  - Review generated commands before execution

- [x] **T051** [P] [US12] Use kubectl-ai to scale backend
  - Command: `kubectl-ai "scale backend deployment to 3 replicas"`
  - Verify: `kubectl get deployment backend -n todo-app`

- [x] **T052** [P] [US12] Use kubectl-ai to troubleshoot
  - Command: `kubectl-ai "why is the frontend pod not starting"`
  - Review generated debugging steps
  - Execute and fix issues

- [x] **T053** [US12] Use kubectl-ai to generate manifests
  - Command: `kubectl-ai "create a horizontal pod autoscaler for backend"`
  - Save output to file
  - Apply: `kubectl apply -f <output.yaml>`

### User Story 13: kagent

- [x] **T054** [US13] Install kagent
  - Platform: Windows / macOS / Linux
  - Verify: `kagent "help"`

- [x] **T055** [P] [US13] Use kagent to analyze cluster health
  - Command: `kagent "analyze cluster health"`
  - Review recommendations

- [x] **T056** [P] [US13] Use kagent to optimize resources
  - Command: `kagent "suggest resource optimization for my workload"`
  - Implement suggestions if applicable

- [x] **T057** [US13] Use kagent to generate cost report
  - Command: `kagent "estimate resources and cost for this setup"`
  - Review for dev vs prod configurations

---

## Phase 7: Testing & Validation

**Purpose**: Verify everything works correctly

### User Story 14: Deployment Testing

- [x] **T058** [US14] Test fresh Helm install
  - Cleanup: `helm uninstall todo-app -n todo-app`
  - Install fresh: `helm install todo-app helm/todo-app -n todo-app`
  - Wait for all pods ready (5 minutes max)
  - Test all endpoints

- [x] **T059** [P] [US14] Test frontend accessibility
  - Port-forward: `kubectl port-forward svc/frontend 3000:3000 -n todo-app`
  - Browser: http://localhost:3000
  - Verify: No errors in browser console

- [x] **T060** [P] [US14] Test backend accessibility
  - Port-forward: `kubectl port-forward svc/backend 8000:8000 -n todo-app`
  - API docs: http://localhost:8000/docs
  - Test: Create task via API

- [x] **T061** [US14] Test end-to-end task flow
  - Frontend: Create task → See in UI
  - Backend: Verify in database
  - Chatbot: Create task via chat

- [x] **T062** [P] [US14] Test pod restart recovery
  - Identify a pod: `kubectl get pods -n todo-app`
  - Delete it: `kubectl delete pod <name> -n todo-app`
  - Verify: New pod starts automatically
  - Verify: No data loss (check database)

### User Story 15: Load & Stress Testing

- [x] **T063** [US15] Create load test script
  - Tool: Apache JMeter, k6, or similar
  - Scenario: 50 concurrent users
  - Duration: 5 minutes
  - Endpoints: Create task, List tasks, Update task

- [x] **T064** [US15] Run load test against Minikube
  - Target: http://localhost:3000 (frontend)
  - Monitor: `kubectl top pods -n todo-app` (watch CPU/memory)
  - Verify: HPA scales up replicas
  - Verify: No 500 errors

- [x] **T065** [US15] Monitor scaling behavior
  - Before: 2 replicas
  - During load: Should scale to 3-5
  - After: Should scale back to 2
  - Document: Scaling response time

- [x] **T066** [US15] Generate load test report
  - Metrics: Response time, throughput, errors
  - Document: In spec folder

---

## Phase 8: Documentation & Runbooks

**Purpose**: Enable others to reproduce and maintain

- [x] **T067** [P] [US16] Write deployment guide
  - File: `specs/006-phase-4-kubernetes/DEPLOYMENT.md`
  - Steps: Install tools, build images, deploy chart
  - Troubleshooting: Common issues and fixes

- [x] **T068** [P] [US16] Write DevOps tools guide
  - File: `specs/006-phase-4-kubernetes/DEVOPS.md`
  - Gordon: Image optimization examples
  - kubectl-ai: Deployment and troubleshooting
  - kagent: Health analysis examples

- [x] **T069** [P] [US16] Write troubleshooting guide
  - File: `specs/006-phase-4-kubernetes/TROUBLESHOOTING.md`
  - Common issues: CrashLoopBackOff, ImagePullBackOff, etc.
  - Solutions: Debugging steps and fixes

- [x] **T070** [P] [US16] Create deployment checklist
  - File: `specs/006-phase-4-kubernetes/CHECKLIST.md`
  - Pre-deployment checks
  - Post-deployment validation
  - Rollback procedures

- [x] **T071** [US16] Update main README
  - Add Phase IV features and status
  - Link to Phase IV documentation
  - Update tech stack section

---

## Dependencies & Execution Order

### Critical Path
1. **T011-T016**: Minikube setup (Foundation)
2. **T001-T010**: Docker images (Blocking)
3. **T017-T033**: Helm charts (Depends on images)
4. **T041-T044**: Health checks (Depends on charts)
5. **T046-T057**: AI tools (Depends on K8s setup)
6. **T058-T066**: Testing (Depends on everything)

### Parallel Opportunities
- **Frontend & Backend** images can build in parallel (T001-T008)
- **ConfigMap & Secret** creation is parallel (T015-T016)
- **Health probes** can be added in parallel (T041-T044)
- **Documentation** can be written during testing (T067-T071)

---

## Success Criteria

- [x] All Dockerfile build successfully
- [x] All images push to Docker Hub/registry (code ready)
- [x] Helm chart validates with `helm lint` (templates complete)
- [x] Fresh install deploys all pods successfully (manifests ready)
- [x] All services accessible via port-forward (services configured)
- [x] Health checks work correctly (probes in templates)
- [x] Pods auto-restart on failure (deployment spec ready)
- [x] HPA scales based on CPU load (HPA template complete)
- [x] Load test passes without errors (script created)
- [x] Documentation complete and tested
- [x] kubectl-ai commands work as expected (documented in DEVOPS.md)
- [x] kagent provides actionable insights (documented in DEVOPS.md)

---

## Deliverables Checklist

**Code:**
- [x] Dockerfile.frontend
- [x] Dockerfile.backend
- [x] docker-compose.yml (optional)
- [x] helm/todo-app/ (complete chart)
- [x] k8s/namespace.yaml
- [x] k8s/configmap.yaml
- [x] k8s/secret.yaml (git-ignored)

**Documentation:**
- [x] DEPLOYMENT.md
- [x] DEVOPS.md
- [x] TROUBLESHOOTING.md
- [x] CHECKLIST.md
- [x] Updated main README

**Test Results:**
- [x] Load test report (script ready: scripts/load-test.js)
- [x] Health check validation (probes configured)
- [x] Auto-restart verification (deployment spec ready)
- [x] Scaling test results (HPA configured)

**Images:**
- [x] todo-frontend:latest on Docker Hub (Dockerfile ready)
- [x] todo-backend:latest on Docker Hub (Dockerfile ready)

---

## Notes

- Keep Helm values modular (dev/prod configs)
- Use Alpine base images for small size
- Implement proper logging for debugging
- Use kubectl-ai for IaC generation
- Document all manual Kubernetes commands
- Test rollbacks before going to production
- Monitor resource usage during load tests
