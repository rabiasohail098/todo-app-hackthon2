# Phase IV: Data Model & Configuration

Database schema, environment variables, and configuration for Phase IV deployment.

---

## Database Schema (No Changes from Phase III)

Phase IV does NOT add new database models. It uses the exact schema from Phase III.

### Existing Tables

#### tasks
```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  is_completed BOOLEAN DEFAULT FALSE,
  priority VARCHAR(20),
  due_date TIMESTAMP,
  category_id INTEGER,
  recurrence_pattern VARCHAR(50),
  next_recurrence_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

#### conversations
```sql
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### messages
```sql
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  conversation_id INTEGER NOT NULL,
  role VARCHAR(20), -- 'user' or 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

#### tags
```sql
CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  name VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  UNIQUE(user_id, name)
);
```

#### task_tags (Junction Table)
```sql
CREATE TABLE task_tags (
  task_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (task_id, tag_id)
);
```

#### categories
```sql
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  name VARCHAR(100) NOT NULL,
  color VARCHAR(7),
  icon VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  UNIQUE(user_id, name)
);
```

#### subtasks
```sql
CREATE TABLE subtasks (
  id SERIAL PRIMARY KEY,
  parent_task_id INTEGER NOT NULL,
  title VARCHAR(255) NOT NULL,
  is_completed BOOLEAN DEFAULT FALSE,
  "order" INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

#### attachments
```sql
CREATE TABLE attachments (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL,
  filename VARCHAR(255) NOT NULL,
  file_path VARCHAR(500),
  file_size INTEGER,
  mime_type VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

#### task_activity (Activity Log)
```sql
CREATE TABLE task_activity (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL,
  user_id TEXT NOT NULL,
  action VARCHAR(50), -- 'created', 'updated', 'completed', etc.
  field VARCHAR(100), -- which field changed
  old_value TEXT,
  new_value TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Environment Variables

### Frontend Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_API_KEY=your-key-here
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
NEXT_PUBLIC_LOG_LEVEL=debug
```

### Backend Environment Variables

```env
# .env
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/todo_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_LOG_LEVEL=debug

# OpenAI
OPENAI_API_KEY=your-key-here

# JWT/Auth
JWT_SECRET=your-secret-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Cloudinary (for attachments)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:30000

# APScheduler
SCHEDULER_ENABLED=true
SCHEDULER_JOBS_PATH=backend/src/jobs

# Logging
LOG_FORMAT=json
LOG_LEVEL=debug
```

---

## Kubernetes Configuration

### ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-app-config
  namespace: todo-app
data:
  API_HOST: backend-service
  API_PORT: "8000"
  LOG_LEVEL: debug
  SCHEDULER_ENABLED: "true"
  JWT_ALGORITHM: HS256
  JWT_EXPIRATION_HOURS: "24"
  CORS_ORIGINS: "http://frontend:3000,http://localhost:3000"
```

### Secret Example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-app-secrets
  namespace: todo-app
type: Opaque
stringData:
  DATABASE_URL: postgresql://postgres:password@postgres:5432/todo_db
  OPENAI_API_KEY: your-key-here
  JWT_SECRET: your-secret-here
  CLOUDINARY_CLOUD_NAME: your-cloud-name
  CLOUDINARY_API_KEY: your-api-key
  CLOUDINARY_API_SECRET: your-api-secret
```

---

## Docker Environment

### Frontend Dockerfile Environment

```dockerfile
FROM node:20-alpine

# Build arguments
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_LOG_LEVEL=info

ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_PUBLIC_LOG_LEVEL=${NEXT_PUBLIC_LOG_LEVEL}
ENV NODE_ENV=production

WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

COPY . .
RUN npm run build

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

CMD ["npm", "start"]
```

### Backend Dockerfile Environment

```dockerfile
FROM python:3.12-alpine

# Build arguments
ARG API_LOG_LEVEL=info

ENV API_LOG_LEVEL=${API_LOG_LEVEL}
ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache gcc musl-dev postgresql-dev

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import http.client; conn=http.client.HTTPConnection('localhost', 8000); conn.request('GET', '/health'); exit(0 if conn.getresponse().status == 200 else 1)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Helm Chart Values Structure

### values.yaml (Default)

```yaml
# Default values for todo-app
replicaCount: 2

image:
  pullPolicy: IfNotPresent
  pullSecrets: []

frontend:
  image:
    repository: todo-frontend
    tag: latest
  replicas: 2
  port: 3000
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

backend:
  image:
    repository: todo-backend
    tag: latest
  replicas: 2
  port: 8000
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

database:
  host: postgres
  port: 5432
  name: todo_db
  user: postgres
  # password stored in Secret

config:
  LOG_LEVEL: debug
  SCHEDULER_ENABLED: "true"
  JWT_ALGORITHM: HS256
  JWT_EXPIRATION_HOURS: "24"

namespace: todo-app

ingress:
  enabled: false
  className: "nginx"
  annotations: {}
  hosts:
    - host: localhost
      paths:
        - path: /
          pathType: Prefix
  tls: []

nodeSelector: {}
tolerations: []
affinity: {}
```

### values-dev.yaml (Development)

```yaml
# Development overrides
frontend:
  replicas: 1
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 200m
      memory: 256Mi
  autoscaling:
    enabled: false

backend:
  replicas: 1
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  autoscaling:
    enabled: false

config:
  LOG_LEVEL: debug
  SCHEDULER_ENABLED: "false"

ingress:
  enabled: false
```

### values-prod.yaml (Production)

```yaml
# Production overrides
frontend:
  replicas: 3
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 60

backend:
  replicas: 3
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 60

config:
  LOG_LEVEL: info
  SCHEDULER_ENABLED: "true"

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: todo.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: todo-tls
      hosts:
        - todo.example.com
```

---

## Docker Compose Configuration (Optional)

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: todo_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/todo_db
      API_HOST: 0.0.0.0
      API_PORT: 8000
      LOG_LEVEL: debug
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NEXT_PUBLIC_LOG_LEVEL: debug
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
```

---

## Network Policies (Optional)

### Allow Frontend to Backend

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-allow-frontend
  namespace: todo-app
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8000
```

### Allow Backend to Database

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-allow-database
  namespace: todo-app
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: default
      ports:
        - protocol: TCP
          port: 5432
```

---

## Scaling Configuration

### HPA Target Metrics

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
  namespace: todo-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend
  minReplicas: 2
  maxReplicas: 5
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

---

## Deployment Readiness

### Pre-Deployment Checklist

- [ ] Database migrations run successfully
- [ ] Environment variables configured
- [ ] Secrets created and accessible
- [ ] Docker images built and tested
- [ ] Helm chart syntax validated
- [ ] ConfigMaps and Secrets ready
- [ ] Network policies (if used) defined
- [ ] Health checks configured

### Post-Deployment Validation

- [ ] All pods in Running state
- [ ] Services accessible
- [ ] Health checks passing
- [ ] Logs showing no errors
- [ ] Database connections established
- [ ] API responding correctly
- [ ] Frontend loading successfully

---

## Configuration Management Best Practices

1. **Secrets**: Never commit to Git
2. **ConfigMaps**: Version control in Git
3. **Environment Files**: Use .gitignore for local .env
4. **Helm Values**: Separate dev/prod overrides
5. **Documentation**: Keep config docs updated
