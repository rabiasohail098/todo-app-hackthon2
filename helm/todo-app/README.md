# Todo App Helm Chart

A production-ready Helm chart for deploying the Todo Chatbot application to Kubernetes.

## Prerequisites

- Kubernetes 1.20+
- Helm 3.0+
- Docker images for frontend and backend available in a registry

## Installation

### Add the Helm repository (if published)

```bash
helm repo add todo https://charts.example.com
helm repo update
```

### Install from local chart

```bash
# Create namespace
kubectl create namespace todo-app

# Install chart
helm install todo-app . -n todo-app -f values.yaml

# Or with development values
helm install todo-app . -n todo-app -f values-dev.yaml
```

## Configuration

### Common Configuration

Edit `values.yaml` to customize:

- **Replicas**: Number of pods for frontend/backend
- **Resources**: CPU/memory requests and limits
- **Image Tags**: Docker image versions
- **Environment Variables**: App configuration
- **Database**: Connection settings
- **Scaling**: HPA min/max replicas and CPU thresholds

### Development Setup

Use `values-dev.yaml` for development:

```bash
helm install todo-app . -n todo-app -f values-dev.yaml
```

Features:
- Single replica for each service
- Lower resource limits
- Debug logging enabled

### Production Setup

Use `values-prod.yaml` for production:

```bash
helm install todo-app . -n todo-app -f values-prod.yaml
```

Features:
- 3+ replicas per service
- Higher resource limits
- Production logging
- Auto-scaling enabled

## Upgrading

```bash
helm upgrade todo-app . -n todo-app -f values.yaml
```

## Uninstalling

```bash
helm uninstall todo-app -n todo-app
```

## Troubleshooting

### Check chart syntax
```bash
helm lint .
```

### Preview manifests
```bash
helm template todo-app . -n todo-app
```

### Check installation status
```bash
helm status todo-app -n todo-app
helm history todo-app -n todo-app
```

### View pod logs
```bash
kubectl logs deployment/frontend -n todo-app
kubectl logs deployment/backend -n todo-app
```

### Rollback
```bash
helm rollback todo-app <revision> -n todo-app
```

## Chart Structure

```
todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default values
├── values-dev.yaml         # Development overrides
├── values-prod.yaml        # Production overrides
├── templates/
│   ├── namespace.yaml      # Kubernetes namespace
│   ├── configmap.yaml      # Configuration
│   ├── secret.yaml         # Secrets
│   ├── deployment-frontend.yaml
│   ├── deployment-backend.yaml
│   ├── service-frontend.yaml
│   ├── service-backend.yaml
│   ├── hpa.yaml            # Auto-scaling
│   └── ingress.yaml        # (optional)
└── README.md               # This file
```

## Values Reference

See `values.yaml` for all configurable options with descriptions.

Key sections:
- `frontend`: Frontend service configuration
- `backend`: Backend service configuration
- `database`: Database connection settings
- `config`: Application configuration (ConfigMap)
- `ingress`: Ingress settings (if enabled)

## Environment Variables

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://backend-service:8000)
- `NEXT_PUBLIC_LOG_LEVEL`: Logging level

### Backend
- `API_HOST`: Bind address (default: 0.0.0.0)
- `API_PORT`: Port (default: 8000)
- `LOG_LEVEL`: Logging level
- `DATABASE_URL`: PostgreSQL connection string (from Secret)
- `OPENAI_API_KEY`: OpenAI API key (from Secret)
- `JWT_SECRET`: JWT signing secret (from Secret)

## Secrets Management

Secrets are defined in `templates/secret.yaml` and should be customized:

```bash
# Create secret before installation
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL=postgresql://... \
  --from-literal=OPENAI_API_KEY=sk-... \
  --from-literal=JWT_SECRET=... \
  -n todo-app
```

For production, use:
- Sealed Secrets
- External Secrets Operator
- AWS Secrets Manager
- HashiCorp Vault

## Scaling

### Manual Scaling

```bash
kubectl scale deployment frontend --replicas=5 -n todo-app
```

### Auto-Scaling (HPA)

Configured in `hpa.yaml`. Default behavior:
- Min replicas: 2
- Max replicas: 5
- Scale up when CPU > 70%
- Scale down when CPU < 70%

## Health Checks

Both deployments include:
- **Liveness Probe**: Restarts pod if unhealthy
- **Readiness Probe**: Removes pod from service if not ready

Adjust timing in `values.yaml` if needed.

## Support

For issues or questions, refer to:
- Main project: https://github.com/panaversity/todo-app-hackathon
- Helm docs: https://helm.sh/docs/
