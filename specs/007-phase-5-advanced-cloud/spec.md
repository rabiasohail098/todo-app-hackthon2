# Phase V: Detailed Specifications

## Overview

This document provides detailed technical specifications for Phase V implementation.

## Part A: Event-Driven Architecture

### A1. Event Topics & Schemas

#### Topic: task.created
- **Partition**: 3
- **Replication**: 3
- **Retention**: 7 days
- **Compression**: Snappy

**Message Schema**:
```json
{
  "eventId": "uuid",
  "eventTimestamp": 1673000000000,
  "userId": "user-123",
  "taskId": "task-456",
  "title": "Complete project",
  "description": "Finish Phase V",
  "priority": "HIGH",
  "dueDate": 1673086400000,
  "categoryId": "category-789",
  "tags": ["work", "urgent"]
}
```

#### Topic: task.updated
- **Partition**: 3
- **Replication**: 3
- **Retention**: 7 days

**Message Schema**:
```json
{
  "eventId": "uuid",
  "eventTimestamp": 1673000000000,
  "userId": "user-123",
  "taskId": "task-456",
  "changes": {
    "title": "Complete project",
    "status": "in-progress"
  },
  "previousValues": {
    "title": "Start project",
    "status": "pending"
  }
}
```

#### Topic: task.completed
- **Partition**: 3
- **Replication**: 3
- **Retention**: 7 days

**Message Schema**:
```json
{
  "eventId": "uuid",
  "eventTimestamp": 1673000000000,
  "userId": "user-123",
  "taskId": "task-456",
  "completedAt": 1673086400000,
  "timeToComplete": 86400000
}
```

#### Topic: task.deleted
- **Partition**: 3
- **Replication**: 3
- **Retention**: 7 days

**Message Schema**:
```json
{
  "eventId": "uuid",
  "eventTimestamp": 1673000000000,
  "userId": "user-123",
  "taskId": "task-456",
  "reason": "user-deletion"
}
```

#### Topic: user.registered
- **Partition**: 3
- **Replication**: 3
- **Retention**: 30 days

**Message Schema**:
```json
{
  "eventId": "uuid",
  "eventTimestamp": 1673000000000,
  "userId": "user-123",
  "email": "user@example.com",
  "registeredAt": "2023-01-06T12:00:00Z"
}
```

#### Topic: notification.sent
- **Partition**: 3
- **Replication**: 3
- **Retention**: 7 days

**Message Schema**:
```json
{
  "eventId": "uuid",
  "eventTimestamp": 1673000000000,
  "notificationId": "notif-789",
  "userId": "user-123",
  "type": "task-reminder",
  "channel": "email",
  "subject": "Task reminder",
  "status": "sent"
}
```

### A2. Dapr Components

#### State Store Component
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-secret
      key: password
  - name: actorStateStore
    value: "true"
  - name: ttlInSeconds
    value: "86400"
```

#### Pub/Sub Component
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-0:9092,kafka-1:9092,kafka-2:9092"
  - name: consumerGroup
    value: "todo-app"
  - name: authRequired
    value: "false"
```

#### Secrets Component
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
  scopes:
  - backend
  - notification-service
```

#### Service Invocation
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
spec:
  mtls:
    enabled: true
    allowInsecure: false
    workloadCertTTL: 24h
  api:
    allowed:
    - name: invoke
      version: v1
    - name: publish
      version: v1
    - name: state
      version: v1
```

### A3. Event Processing Pipeline

**Producer Flow**:
1. User creates task via API
2. Backend saves to PostgreSQL
3. Backend publishes `task.created` event to Kafka
4. Event contains task metadata
5. Confirmation returned to client

**Consumer Flow**:
1. Event published to Kafka topic
2. Consumer group picks up message
3. Dapr pub/sub routes to subscribers
4. Subscribers process async
5. Offset committed on success
6. Failed messages sent to DLQ

**Event Correlation**:
- All events include `eventId` (UUID)
- Trace events across services using `eventId`
- Log `eventId` for debugging

## Part B: Local Deployment Architecture

### B1. Docker Compose Services

```
┌─────────────────────────────────────────┐
│         Docker Compose Network           │
├─────────────────────────────────────────┤
│  Frontend        Backend      Database   │
│  :3000      :8000         PostgreSQL     │
│                            :5432         │
│                                          │
│  Kafka                 State             │
│  Zookeeper  Schema     Redis             │
│  Brokers x3 Registry   :6379             │
│  :9092-94              Monitor           │
│                        Prometheus/       │
│  Observability         Grafana/Jaeger    │
│  ELK Stack                               │
└─────────────────────────────────────────┘
```

### B2. Service Dependencies

```
frontend → backend → database
         → notification-service

backend → kafka (events)
       → redis (state via Dapr)
       → postgresql (persistence)

kafka → schema-registry
     → zookeeper

monitoring → prometheus → grafana
          → elasticsearch/kibana
          → jaeger
```

### B3. Volume Mounts

```
-volumes:
  postgres_data:
  kafka_data:
  zookeeper_data:
  elasticsearch_data:
  prometheus_data:
```

### B4. Environment Configuration

```
# .env.local
POSTGRES_USER=todouser
POSTGRES_PASSWORD=securepassword
KAFKA_BROKERS=kafka1:29092,kafka2:29093,kafka3:29094
REDIS_URL=redis://redis:6379
DAPR_HOST=localhost
DAPR_HTTP_PORT=3500
SCHEMA_REGISTRY_URL=http://schema-registry:8081
```

## Part C: Cloud Deployment Architecture

### C1. AWS EKS Architecture

```
┌─────────────────────────────────────┐
│  AWS Account & VPC                  │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐  │
│  │  EKS Cluster                 │  │
│  │  ┌──────────────────────┐    │  │
│  │  │ Ingress (ALB)        │    │  │
│  │  └──────────────────────┘    │  │
│  │          ↓                    │  │
│  │  ┌──────────────────────┐    │  │
│  │  │ Service Mesh (Istio) │    │  │
│  │  └──────────────────────┘    │  │
│  │          ↓                    │  │
│  │  ┌──────────────────────┐    │  │
│  │  │ Workload Pods        │    │  │
│  │  │ - Backend (3 replicas)    │  │
│  │  │ - Notification (2 replicas)   │  │
│  │  │ - Analytics (1 replica)   │  │
│  │  └──────────────────────┘    │  │
│  │                              │  │
│  │  Auto Scaling:               │  │
│  │  - HPA: 70% CPU target       │  │
│  │  - VPA: Right-sizing         │  │
│  │  - CA: Cluster scaling       │  │
│  └──────────────────────────────┘  │
│                                     │
│  Managed Services:                 │
│  - RDS PostgreSQL (Multi-AZ)       │
│  - MSK Kafka Cluster               │
│  - ElastiCache Redis               │
│  - CloudWatch Logs/Metrics         │
│  - EBS for persistence             │
│                                     │
└─────────────────────────────────────┘
```

### C2. GCP GKE Architecture

```
┌─────────────────────────────────────┐
│  GCP Project                        │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐  │
│  │  GKE Cluster                 │  │
│  │  ┌──────────────────────┐    │  │
│  │  │ Cloud Load Balancer  │    │  │
│  │  └──────────────────────┘    │  │
│  │          ↓                    │  │
│  │  ┌──────────────────────┐    │  │
│  │  │ Workload Pods        │    │  │
│  │  └──────────────────────┘    │  │
│  │                              │  │
│  │  Node Pools:                 │  │
│  │  - Regular (compute)         │  │
│  │  - Memory-optimized          │  │
│  └──────────────────────────────┘  │
│                                     │
│  Managed Services:                 │
│  - Cloud SQL PostgreSQL            │
│  - Pub/Sub (Kafka alternative)     │
│  - Memorystore Redis               │
│  - Cloud Logging                   │
│  - Cloud Monitoring                │
│                                     │
└─────────────────────────────────────┘
```

### C3. Azure AKS Architecture

```
┌─────────────────────────────────────┐
│  Azure Subscription                 │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐  │
│  │  AKS Cluster                 │  │
│  │  ┌──────────────────────┐    │  │
│  │  │ Application Gateway  │    │  │
│  │  └──────────────────────┘    │  │
│  │          ↓                    │  │
│  │  ┌──────────────────────┐    │  │
│  │  │ Workload Pods        │    │  │
│  │  └──────────────────────┘    │  │
│  │                              │  │
│  │  Node Pools:                 │  │
│  │  - Default Linux Pool        │  │
│  │  - Windows Pool (optional)   │  │
│  └──────────────────────────────┘  │
│                                     │
│  Managed Services:                 │
│  - Azure Database PostgreSQL       │
│  - Event Hubs (Kafka alternative)  │
│  - Azure Cache Redis               │
│  - Monitor & Analytics             │
│                                     │
└─────────────────────────────────────┘
```

### C4. GitOps Workflow

```
┌─────────────────────────────────────┐
│  Developer Workflow                 │
├─────────────────────────────────────┤
│  1. Code changes → Git push         │
│  2. PR triggers CI/CD pipeline      │
│  3. Tests & security scans          │
│  4. Build container images          │
│  5. Push to registry                │
│  6. Update Helm values in repo      │
│  7. Merge to main branch            │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  GitOps Pipeline (ArgoCD)           │
├─────────────────────────────────────┤
│  1. Watches Git repository          │
│  2. Detects manifest changes        │
│  3. Compares desired vs actual      │
│  4. Syncs cluster state             │
│  5. Applies changes (rollout)       │
│  6. Monitors deployment health      │
│  7. Auto-rollback on failure        │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Kubernetes Cluster                 │
├─────────────────────────────────────┤
│  New version deployed               │
│  Services updated                   │
│  Traffic shifted gradually          │
│  Monitoring validated               │
└─────────────────────────────────────┘
```

### C5. Auto-Scaling Configuration

**HPA Settings**:
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
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**VPA Settings**:
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  updatePolicy:
    updateMode: "Auto"  # Auto or Recreate
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2
        memory: 2Gi
```

## Monitoring & Observability

### Metrics Collection

**Backend Metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge

tasks_created = Counter('tasks_created_total', 'Total tasks created')
task_duration = Histogram('task_completion_duration_seconds', 'Task completion time')
concurrent_users = Gauge('concurrent_users', 'Concurrent users')
```

**Kafka Metrics**:
- Messages/sec by topic
- Consumer lag by group
- Broker disk usage
- Replication lag

**Database Metrics**:
- Query latency (p50, p95, p99)
- Connection pool usage
- Transaction duration
- Slow query count

### Alerting Rules

```yaml
groups:
- name: todo-app
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
    for: 5m
    annotations:
      summary: "High error rate detected"
      
  - alert: KafkaConsumerLag
    expr: kafka_consumer_lag > 1000
    for: 10m
    annotations:
      summary: "Kafka consumer lag too high"
      
  - alert: DatabaseConnectionPoolExhausted
    expr: db_connection_pool_usage > 0.95
    for: 5m
    annotations:
      summary: "Database connection pool exhausted"
```

## Security Specifications

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-netpol
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
          app: nginx-ingress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
  - to:
    - podSelector:
        matchLabels:
          app: kafka
  - ports:
    - port: 53
      protocol: UDP  # DNS
    - port: 443
      protocol: TCP  # HTTPS for external APIs
```

### RBAC Configuration

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: backend-role
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["db-credentials", "api-keys"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: backend-rolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: backend-role
subjects:
- kind: ServiceAccount
  name: backend
  namespace: todo-app
```

## Performance Targets

| Metric | Target | P95 | P99 |
|--------|--------|-----|-----|
| API Response Time | < 200ms | < 300ms | < 500ms |
| Chat Latency | < 500ms | < 800ms | < 1s |
| Task Creation Rate | 100/sec | 150/sec | 200/sec |
| Concurrent Users | 1000 | 1500 | 2000 |
| Database Query | < 10ms | < 20ms | < 50ms |

## Success Criteria Checklist

- [ ] All 8 event topics created and tested
- [ ] Event schemas registered in Schema Registry
- [ ] Dapr components configured for all services
- [ ] Kafka consumer groups functioning
- [ ] State store persisting user preferences
- [ ] Pub/Sub event routing working
- [ ] Local Docker Compose deployment complete
- [ ] Terraform scripts provisioning cloud infrastructure
- [ ] ArgoCD syncing cluster state from Git
- [ ] HPA scaling based on CPU/memory
- [ ] Monitoring dashboard active
- [ ] Backup/restore procedures tested
- [ ] DR exercise completed successfully
