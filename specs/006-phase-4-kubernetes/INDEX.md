# Phase 4: Kubernetes Deployment - Complete Index

Welcome to Phase 4 implementation. This folder contains everything needed to deploy the Todo App to Kubernetes using Minikube and Helm charts.

---

## 📌 Start Here

### First Time Setup (Choose One)

**Option A: Quick Start (30 minutes)**
→ Read: [quickstart.md](./quickstart.md)

**Option B: Full Deployment (2 hours)**
→ Read: [DEPLOYMENT.md](./DEPLOYMENT.md)

**Option C: Understand Architecture First**
→ Read: [spec.md](./spec.md)

---

## 📖 Documentation Guide

### For Everyone
| Document | Purpose | Time |
|----------|---------|------|
| [quickstart.md](./quickstart.md) | 30-min setup guide | 30 min |
| [spec.md](./spec.md) | Architecture & goals | 15 min |
| [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md) | Configuration guide | 10 min |

### For Developers
| Document | Purpose | Time |
|----------|---------|------|
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Step-by-step deployment | 60 min |
| [CHECKLIST.md](./CHECKLIST.md) | Verification steps | 30 min |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | Problem solving | Reference |

### For DevOps/Operations
| Document | Purpose | Time |
|----------|---------|------|
| [plan.md](./plan.md) | Project timeline & strategy | 20 min |
| [tasks.md](./tasks.md) | Detailed task breakdown | Reference |
| [research.md](./research.md) | Design decisions | 30 min |
| [DEVOPS.md](./DEVOPS.md) | AI tools integration | 20 min |
| [data-model.md](./data-model.md) | Configuration templates | Reference |

### For Architecture Review
| Document | Purpose | Time |
|----------|---------|------|
| [spec.md](./spec.md) | Complete specification | 20 min |
| [research.md](./research.md) | Design rationale | 30 min |
| [plan.md](./plan.md) | Implementation roadmap | 15 min |

---

## 🚀 Quick Commands

### Start Everything (Copy & Paste)

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=4096
minikube addons enable metrics-server

# 2. Build images
docker build -t todo-frontend:latest frontend/
docker build -t todo-backend:latest backend/

# 3. Load images
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# 4. Deploy
helm install todo-app helm/todo-app -n todo-app \
  -f helm/todo-app/values-dev.yaml

# 5. Access
kubectl port-forward service/frontend 3000:3000 -n todo-app &
# Open http://localhost:3000
```

### Common Tasks

```bash
# Check deployment status
kubectl get all -n todo-app

# View logs
kubectl logs <pod-name> -n todo-app -f

# Scale deployment
kubectl scale deployment frontend --replicas=3 -n todo-app

# Update values
helm upgrade todo-app helm/todo-app -n todo-app -f helm/todo-app/values-dev.yaml

# Rollback deployment
helm rollback todo-app -n todo-app

# Delete everything
helm uninstall todo-app -n todo-app
kubectl delete namespace todo-app
```

---

## 🎯 Learning Paths

### Path 1: I Just Want It Running (1 hour)
1. Read: [quickstart.md](./quickstart.md) (15 min)
2. Copy & paste commands from Quick Commands above (30 min)
3. Verify: [CHECKLIST.md](./CHECKLIST.md) → Deployment section (15 min)

### Path 2: I Need to Understand Everything (3 hours)
1. Read: [spec.md](./spec.md) - Understand what we're building
2. Read: [plan.md](./plan.md) - Understand the timeline
3. Read: [research.md](./research.md) - Understand design choices
4. Follow: [DEPLOYMENT.md](./DEPLOYMENT.md) - Step-by-step deployment
5. Complete: [CHECKLIST.md](./CHECKLIST.md) - Verify everything works

### Path 3: I'm Troubleshooting Something (Reference)
1. Check: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Find your issue
2. Follow: Diagnostic steps
3. Execute: Suggested commands
4. Verify: Test that fix worked

### Path 4: I'm Setting Up DevOps Tools (30 min)
1. Read: [DEVOPS.md](./DEVOPS.md)
2. Install: Gordon, kubectl-ai, kagent
3. Practice: Examples in the guide
4. Integrate: Into your CI/CD pipeline

---

## 📊 What You Get

### Infrastructure
- ✅ Docker images (frontend 150MB, backend 200MB)
- ✅ Kubernetes manifests (8 templates)
- ✅ Helm chart (production-ready)
- ✅ Auto-scaling configuration
- ✅ Health checks and probes
- ✅ Configuration management (ConfigMap + Secrets)

### Documentation
- ✅ 11 comprehensive guides
- ✅ 5,400+ lines of documentation
- ✅ Step-by-step procedures
- ✅ Troubleshooting flowcharts
- ✅ Pre/post deployment checklists
- ✅ Environment variable reference
- ✅ DevOps tools integration guide

### Automation
- ✅ Helm charts with dev/prod values
- ✅ Docker build scripts
- ✅ Minikube setup automation
- ✅ Deployment verification procedures

---

## 📋 File Structure

```
specs/006-phase-4-kubernetes/
├── spec.md                    # Full specification (400+ lines)
├── plan.md                    # 14-day timeline (300+ lines)
├── tasks.md                   # 71 tasks (800+ lines)
├── quickstart.md              # 30-min quick start (300+ lines)
├── research.md                # Design decisions (800+ lines)
├── data-model.md              # Config templates (500+ lines)
├── DEPLOYMENT.md              # Deployment procedure (400+ lines)
├── DEVOPS.md                  # DevOps tools (500+ lines)
├── TROUBLESHOOTING.md         # Troubleshooting (800+ lines)
├── CHECKLIST.md               # Pre/post checks (600+ lines)
├── ENVIRONMENT_VARIABLES.md   # Config guide (400+ lines)
└── INDEX.md                   # This file

helm/todo-app/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
├── README.md
└── templates/
    ├── namespace.yaml
    ├── configmap.yaml
    ├── secret.yaml
    ├── deployment-frontend.yaml
    ├── deployment-backend.yaml
    ├── service-frontend.yaml
    ├── service-backend.yaml
    └── hpa.yaml

kubernetes/
└── setup.sh
```

---

## 🔑 Key Concepts

### Minikube
Local Kubernetes cluster for development and testing. Runs on your machine.

### Docker
Container format for packaging applications. We have frontend and backend images.

### Helm
Package manager for Kubernetes. Makes it easy to deploy, upgrade, and rollback.

### ConfigMap
Kubernetes object for non-sensitive configuration (log levels, CORS origins, etc.)

### Secret
Kubernetes object for sensitive data (database URLs, API keys, credentials)

### HPA (Horizontal Pod Autoscaler)
Automatically scales pods up/down based on CPU usage

### Service
Kubernetes object that exposes pods to other pods or external traffic

### Namespace
Kubernetes object that isolates resources (like a folder)

---

## ⚡ Troubleshooting

### Issue: Pod won't start
→ See: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Section 1: Pending Pods

### Issue: ImagePullBackOff
→ See: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Section 2: ImagePullBackOff

### Issue: CrashLoopBackOff
→ See: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Section 3: CrashLoopBackOff

### Issue: Service not responding
→ See: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Section 4: Pods Running But Not Responding

### Issue: Database connection failed
→ See: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Section 9: Database Connection Issues

### Issue: Something else?
→ See: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Section 10: Debugging Workflow

---

## 💡 Tips & Tricks

### Enable metrics-server immediately
```bash
minikube addons enable metrics-server
```
Without this, `kubectl top` won't work.

### Use aliases for shorter commands
```bash
alias k=kubectl
alias h=helm
```

### Watch pod creation in real-time
```bash
watch kubectl get pods -n todo-app
```

### Stream logs from all pods
```bash
kubectl logs -f deployment/backend -n todo-app
```

### Execute commands in pods
```bash
kubectl exec -it <pod-name> -n todo-app -- /bin/sh
```

### Debug with temporary pod
```bash
kubectl run -it --rm debug --image=ubuntu --restart=Never -n todo-app -- bash
```

---

## 📞 Getting Help

1. **Read Documentation**: Start with relevant section in your issue area
2. **Check Logs**: `kubectl logs <pod> -n todo-app`
3. **Describe Resources**: `kubectl describe pod <pod> -n todo-app`
4. **Review Events**: `kubectl get events -n todo-app`
5. **Ask in TROUBLESHOOTING.md**: Most issues covered there

---

## 🎓 Learning Resources

- **Kubernetes Docs**: https://kubernetes.io/docs/
- **Helm Docs**: https://helm.sh/docs/
- **Docker Docs**: https://docs.docker.com/
- **Minikube Docs**: https://minikube.sigs.k8s.io/docs/
- **kubectl Cheatsheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/

---

## ✅ Checklist Before Starting

- [ ] Docker Desktop installed (with Minikube support)
- [ ] kubectl installed
- [ ] Helm 3 installed
- [ ] Git latest changes pulled
- [ ] Python 3.13+ (for backend)
- [ ] Node.js 18+ (for frontend)
- [ ] 4GB+ RAM available
- [ ] 4+ CPU cores available
- [ ] Internet connection (to pull images)

---

## 🚀 You're Ready!

Choose your path from "Learning Paths" above and start building. The quickest way to understand is to **just run it** using quickstart.md.

**Questions?** Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) first!

**Ready?** Start with [quickstart.md](./quickstart.md) now!

---

**Phase 4**: Kubernetes Deployment
**Created**: Q4 2025 Hackathon
**Status**: ✅ Complete & Ready to Use
**Next**: Deploy, monitor, and iterate!

