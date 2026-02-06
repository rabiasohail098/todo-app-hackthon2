# Dapr Integration for Phase V

## Dapr Architecture Overview

Dapr (Distributed Application Runtime) provides a set of APIs and capabilities for building distributed applications. In the Todo app, Dapr enables:

- **State Management**: Persist application state with consistency guarantees
- **Pub/Sub**: Decouple services through event-driven messaging
- **Service Invocation**: Call services without hardcoding addresses
- **Secrets**: Secure credential management
- **Jobs**: Schedule and execute background tasks

## Dapr Components Setup

### State Store Configuration (Redis)

```yaml
# backend/config/dapr/state-store.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis:6379
  - name: redisPassword
    value: "" # Or use secret store
  - name: actorStateStore
    value: "true"
  - name: ttlInSeconds
    value: "3600"
  auth:
    secretStore: kubernetes
```

### Pub/Sub Configuration (Kafka)

```yaml
# backend/config/dapr/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka1:29092,kafka2:29093,kafka3:29094"
  - name: consumerGroup
    value: "todo-app-dapr"
  - name: authRequired
    value: "false"
  - name: maxMessageBytes
    value: "1048576"
  - name: allowCreateTopics
    value: "true"
  - name: schemaFormat
    value: ""
```

### Secrets Configuration (Kubernetes)

```yaml
# backend/config/dapr/secrets.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secrets
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
```

### Service Invocation Configuration

```yaml
# backend/config/dapr/service-invocation.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: todo-app
spec:
  mtls:
    enabled: true
    allowInsecure: false
    workloadCertTTL: 24h
    clusterDomainAliases:
      - cluster.local
  secrets:
    scopes:
      - storeName: "secrets"
        allowedSecrets: ["*"]
  accessControl:
    defaultAction: "allow"
    trustDomain: "public"
    policies:
      - appId: backend
        allowedApiActions:
          - "invoke/any-method"
      - appId: notification-service
        allowedApiActions:
          - "invoke/send-notification"
```

## Backend Integration Implementation

### State Store Service

```python
# backend/src/services/dapr_state.py

import json
import logging
from typing import Any, Dict, Optional
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class DaprStateService:
    def __init__(self, dapr_port: int = 3500):
        self.dapr_port = dapr_port
        self.base_url = f"http://localhost:{dapr_port}/v1.0"
        self.state_store = "statestore"
    
    async def save_state(
        self,
        key: str,
        value: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None
    ):
        """Save state with optional TTL"""
        state_request = {
            "key": key,
            "value": value
        }
        
        if ttl_seconds:
            state_request["metadata"] = {
                "ttlInSeconds": str(ttl_seconds),
                **(metadata or {})
            }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/state/{self.state_store}"
            async with session.post(url, json=[state_request]) as resp:
                if resp.status != 204:
                    logger.error(f"Failed to save state: {resp.status}")
                    raise Exception("State save failed")
                logger.info(f"State saved for key: {key}")
    
    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve state by key"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/state/{self.state_store}/{key}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"State retrieved for key: {key}")
                    return data
                elif resp.status == 404:
                    logger.debug(f"State not found for key: {key}")
                    return None
                else:
                    logger.error(f"Failed to get state: {resp.status}")
                    raise Exception("State retrieval failed")
    
    async def delete_state(self, key: str):
        """Delete state"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/state/{self.state_store}/{key}"
            async with session.delete(url) as resp:
                if resp.status != 204:
                    logger.error(f"Failed to delete state: {resp.status}")
                    raise Exception("State deletion failed")
                logger.info(f"State deleted for key: {key}")
    
    async def save_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ):
        """Save user preferences with 30-day TTL"""
        key = f"user-preferences:{user_id}"
        await self.save_state(key, preferences, ttl_seconds=2592000)
    
    async def get_user_preferences(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve user preferences"""
        key = f"user-preferences:{user_id}"
        return await self.get_state(key)
    
    async def save_task_cache(
        self,
        user_id: str,
        tasks: list
    ):
        """Cache user's tasks for 1 hour"""
        key = f"tasks-cache:{user_id}"
        await self.save_state(
            key, 
            {"tasks": tasks, "cached_at": datetime.now().isoformat()},
            ttl_seconds=3600
        )
    
    async def get_task_cache(self, user_id: str) -> Optional[list]:
        """Get cached tasks"""
        key = f"tasks-cache:{user_id}"
        cache = await self.get_state(key)
        return cache.get("tasks") if cache else None
```

### Pub/Sub Service

```python
# backend/src/services/dapr_pubsub.py

import json
import logging
import aiohttp
from typing import Any, Dict, Callable
from fastapi import FastAPI

logger = logging.getLogger(__name__)

class DaprPubSubService:
    def __init__(self, dapr_port: int = 3500):
        self.dapr_port = dapr_port
        self.base_url = f"http://localhost:{dapr_port}/v1.0"
        self.pubsub_name = "pubsub"
        self.subscribers: Dict[str, list[Callable]] = {}
    
    async def publish_event(
        self,
        topic: str,
        data: Dict[str, Any],
        metadata: Dict[str, str] = None
    ):
        """Publish event to topic"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/publish/{self.pubsub_name}/{topic}"
            
            payload = {
                "data": data,
                **(metadata or {})
            }
            
            async with session.post(url, json=payload) as resp:
                if resp.status == 204:
                    logger.info(f"Event published to {topic}")
                else:
                    logger.error(f"Failed to publish: {resp.status}")
                    raise Exception("Publish failed")
    
    async def publish_task_created(
        self,
        user_id: str,
        task_id: str,
        task_data: Dict[str, Any]
    ):
        """Publish task creation event"""
        await self.publish_event(
            "task.created",
            {
                "userId": user_id,
                "taskId": task_id,
                **task_data
            }
        )
    
    async def publish_task_completed(
        self,
        task_id: str,
        user_id: str
    ):
        """Publish task completion event"""
        await self.publish_event(
            "task.completed",
            {
                "taskId": task_id,
                "userId": user_id,
                "completedAt": datetime.now().isoformat()
            }
        )
    
    async def publish_user_registered(
        self,
        user_id: str,
        email: str
    ):
        """Publish user registration event"""
        await self.publish_event(
            "user.registered",
            {
                "userId": user_id,
                "email": email,
                "registeredAt": datetime.now().isoformat()
            }
        )
    
    def setup_subscribers(self, app: FastAPI):
        """Setup subscription endpoints"""
        
        @app.post("/dapr/subscribe")
        async def dapr_subscribe():
            """Dapr subscription metadata"""
            return [
                {
                    "pubsubname": self.pubsub_name,
                    "topic": "task.created",
                    "route": "/subscribe/task-created",
                    "deadLetterTopic": "dlq-task-created"
                },
                {
                    "pubsubname": self.pubsub_name,
                    "topic": "task.completed",
                    "route": "/subscribe/task-completed",
                    "deadLetterTopic": "dlq-task-completed"
                },
                {
                    "pubsubname": self.pubsub_name,
                    "topic": "user.registered",
                    "route": "/subscribe/user-registered",
                    "deadLetterTopic": "dlq-user-registered"
                }
            ]
        
        @app.post("/subscribe/task-created")
        async def on_task_created(data: Dict[str, Any]):
            """Handle task creation"""
            try:
                logger.info(f"Task created: {data.get('taskId')}")
                # Process event: update cache, send notifications, etc.
                return {"status": "success"}
            except Exception as e:
                logger.error(f"Error processing task creation: {e}")
                return {"status": "error", "message": str(e)}, 500
        
        @app.post("/subscribe/task-completed")
        async def on_task_completed(data: Dict[str, Any]):
            """Handle task completion"""
            try:
                logger.info(f"Task completed: {data.get('taskId')}")
                # Process event: update stats, send congratulations, etc.
                return {"status": "success"}
            except Exception as e:
                logger.error(f"Error processing task completion: {e}")
                return {"status": "error", "message": str(e)}, 500
        
        @app.post("/subscribe/user-registered")
        async def on_user_registered(data: Dict[str, Any]):
            """Handle user registration"""
            try:
                logger.info(f"User registered: {data.get('email')}")
                # Process event: send welcome email, setup defaults, etc.
                return {"status": "success"}
            except Exception as e:
                logger.error(f"Error processing user registration: {e}")
                return {"status": "error", "message": str(e)}, 500
```

### Service Invocation

```python
# backend/src/services/dapr_service_invocation.py

import aiohttp
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class DaprServiceInvocation:
    def __init__(self, dapr_port: int = 3500):
        self.dapr_port = dapr_port
        self.base_url = f"http://localhost:{dapr_port}/v1.0"
    
    async def invoke_service(
        self,
        service_id: str,
        method_name: str,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Invoke another service via Dapr"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/invoke/{service_id}/method/{method_name}"
            
            try:
                async with session.post(url, json=data or {}) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        logger.info(f"Service invocation successful: {service_id}/{method_name}")
                        return result
                    else:
                        logger.error(f"Service invocation failed: {resp.status}")
                        raise Exception(f"Service invocation failed: {resp.status}")
            except Exception as e:
                logger.error(f"Service invocation error: {e}")
                raise
    
    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "in-app"
    ):
        """Send notification via notification service"""
        return await self.invoke_service(
            "notification-service",
            "send",
            {
                "userId": user_id,
                "title": title,
                "message": message,
                "type": notification_type
            }
        )
    
    async def get_user_recommendations(
        self,
        user_id: str
    ):
        """Get recommendations from AI service"""
        return await self.invoke_service(
            "ai-service",
            "get-recommendations",
            {"userId": user_id}
        )
```

### Jobs Service (Scheduled Tasks)

```python
# backend/src/services/dapr_jobs.py

import aiohttp
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DaprJobsService:
    def __init__(self, dapr_port: int = 3500):
        self.dapr_port = dapr_port
        self.base_url = f"http://localhost:{dapr_port}/v1.0"
        self.jobs_api = "jobapi"
    
    async def schedule_job(
        self,
        job_id: str,
        callback_url: str,
        schedule: str,  # Cron format
        metadata: Dict[str, Any] = None
    ):
        """Schedule a job using Dapr Jobs API"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/jobs/{self.jobs_api}/{job_id}"
            
            payload = {
                "schedule": schedule,
                "callback": callback_url,
                "metadata": metadata or {}
            }
            
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 204:
                        logger.info(f"Job scheduled: {job_id}")
                    else:
                        logger.error(f"Failed to schedule job: {resp.status}")
                        raise Exception("Job scheduling failed")
            except Exception as e:
                logger.error(f"Job scheduling error: {e}")
                raise
    
    async def schedule_task_reminder(
        self,
        task_id: str,
        due_date: datetime,
        callback_url: str
    ):
        """Schedule reminder for task due date"""
        # Send reminder 30 minutes before due date
        reminder_time = due_date - timedelta(minutes=30)
        
        job_id = f"reminder-{task_id}"
        
        # For one-time jobs, we would use timestamp directly
        # For recurring: "0 9 * * MON-FRI" (9am weekdays)
        
        await self.schedule_job(
            job_id=job_id,
            callback_url=f"{callback_url}/task-reminder",
            schedule=reminder_time.isoformat(),
            metadata={"taskId": task_id}
        )
    
    async def schedule_daily_digest(
        self,
        user_id: str,
        callback_url: str
    ):
        """Schedule daily digest at 9am"""
        job_id = f"digest-{user_id}"
        
        await self.schedule_job(
            job_id=job_id,
            callback_url=f"{callback_url}/daily-digest",
            schedule="0 9 * * *",  # 9am daily
            metadata={"userId": user_id}
        )
```

## Dapr Sidecar Configuration

### For Docker Compose

```yaml
app:
  image: todo-app:latest
  ports:
    - "8000:8000"
  depends_on:
    - dapr
  environment:
    DAPR_HOST: dapr
    DAPR_HTTP_PORT: 3500

dapr:
  image: daprio/daprd:latest
  command: ./daprd
    -app-id backend
    -app-port 8000
    -dapr-http-port 3500
    -dapr-grpc-port 50001
    -components-path ./config/dapr
    -log-level info
  ports:
    - "3500:3500"
    - "50001:50001"
  volumes:
    - ./config/dapr:/config/dapr
  depends_on:
    - redis
    - kafka1
```

### For Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: todo-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/config: "dapr-config"
    spec:
      containers:
      - name: app
        image: todo-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HOST
          value: "localhost"
        - name: DAPR_HTTP_PORT
          value: "3500"
```

## Testing Dapr Components

### Test State Store

```bash
# Save state
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '{
    "key": "test-key",
    "value": {"message": "hello"}
  }'

# Get state
curl http://localhost:3500/v1.0/state/statestore/test-key

# Delete state
curl -X DELETE http://localhost:3500/v1.0/state/statestore/test-key
```

### Test Pub/Sub

```bash
# Publish message
curl -X POST http://localhost:3500/v1.0/publish/pubsub/test-topic \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"message": "hello world"}
  }'
```

## Best Practices

1. **Always use appropriate state store** - Redis for cache, PostgreSQL for durable state
2. **Implement idempotent subscribers** - Handle duplicate events gracefully
3. **Use meaningful app-ids** - Make service discovery intuitive
4. **Configure proper mTLS** - Enable mutual TLS in production
5. **Monitor sidecar health** - Watch for sidecar crashes
6. **Use secrets for credentials** - Never hardcode sensitive data
7. **Implement circuit breakers** - Handle service failures gracefully
8. **Test locally first** - Validate Dapr integration before cloud deployment
