# Local Deployment Guide - Phase 5

This guide covers deploying the complete Todo App stack locally with all Phase 5 features including Kafka, Dapr, and observability.

## Prerequisites

- Docker Desktop 4.x+ (with Docker Compose v2)
- Git
- Make (optional, for convenience commands)
- 16GB+ RAM recommended
- 20GB+ free disk space

## Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd todo-app-hackthon

# 2. Copy environment template
cp .env.local.template .env

# 3. Edit .env with your values (especially API keys)
# Required: DATABASE_URL, JWT_SECRET, CORS_ORIGINS
# Optional: OPENAI_API_KEY for chat features

# 4. Start the complete stack
make dev-up

# Or without Make:
docker-compose -f docker-compose.phase5.yml up -d

# 5. Initialize data (Kafka topics, sample data)
./init-data.sh
# Or: make dev-init
```

## Service URLs

Once running, access services at:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js web application |
| Backend API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Kafka UI | http://localhost:8080 | Kafka cluster management |
| Grafana | http://localhost:3001 | Dashboards (admin/admin) |
| Prometheus | http://localhost:9090 | Metrics |
| Jaeger | http://localhost:16686 | Distributed tracing |
| Kibana | http://localhost:5601 | Log visualization |
| Elasticsearch | http://localhost:9200 | Search/logging |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
│  ┌─────────────────┐                                           │
│  │    Frontend     │ Next.js @ :3000                           │
│  └────────┬────────┘                                           │
└───────────┼─────────────────────────────────────────────────────┘
            │
┌───────────┼─────────────────────────────────────────────────────┐
│           ▼        API Layer                                    │
│  ┌─────────────────┐     ┌──────────────────┐                  │
│  │    Backend      │────▶│   Dapr Sidecar   │                  │
│  │   FastAPI       │     │   (State/PubSub) │                  │
│  └────────┬────────┘     └────────┬─────────┘                  │
│           │                       │                             │
└───────────┼───────────────────────┼─────────────────────────────┘
            │                       │
┌───────────┼───────────────────────┼─────────────────────────────┐
│           ▼                       ▼    Data Layer               │
│  ┌─────────────────┐     ┌──────────────────┐                  │
│  │   PostgreSQL    │     │      Redis       │                  │
│  │    Database     │     │   (State Store)  │                  │
│  └─────────────────┘     └──────────────────┘                  │
│                                                                 │
│  ┌─────────────────────────────────────────────┐               │
│  │              Kafka Cluster                   │               │
│  │  ┌────────┐ ┌────────┐ ┌────────┐           │               │
│  │  │Broker 1│ │Broker 2│ │Broker 3│           │               │
│  │  └────────┘ └────────┘ └────────┘           │               │
│  │  ┌─────────────────┐ ┌─────────────────┐    │               │
│  │  │ Schema Registry │ │    Zookeeper    │    │               │
│  │  └─────────────────┘ └─────────────────┘    │               │
│  └─────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
            │
┌───────────┼─────────────────────────────────────────────────────┐
│           ▼        Observability Layer                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   Prometheus    │ │     Grafana     │ │     Jaeger      │   │
│  │    (Metrics)    │ │  (Dashboards)   │ │   (Tracing)     │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
│  ┌─────────────────────────────────────┐                       │
│  │      Elasticsearch + Kibana         │                       │
│  │            (Logging)                │                       │
│  └─────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

## Kafka Topics

The following Kafka topics are created automatically:

| Topic | Partitions | Description |
|-------|------------|-------------|
| task.created | 3 | New task creation events |
| task.updated | 3 | Task modification events |
| task.completed | 3 | Task completion events |
| task.deleted | 3 | Task deletion events |
| user.registered | 3 | New user registration |
| notification.sent | 3 | Notification dispatch |
| task.reminder | 3 | Task reminder events |
| analytics.events | 6 | User behavior analytics |

## Common Commands

```bash
# Start services
make dev-up

# Stop services
make dev-down

# View logs
make dev-logs

# Restart services
make dev-restart

# Initialize data
make dev-init

# Clean up (including volumes)
make dev-clean

# Check status
make dev-status

# Rebuild images
make dev-build

# Scale backend
make scale-backend
```

## Troubleshooting

### Services not starting

1. Check Docker resources (increase memory if needed)
2. Verify ports are not in use:
   ```bash
   lsof -i :3000 -i :8000 -i :9092 -i :5432
   ```
3. Check logs: `docker-compose -f docker-compose.phase5.yml logs`

### Kafka connection issues

1. Wait 30-60 seconds after startup for Kafka to be ready
2. Check Kafka UI at http://localhost:8080
3. Verify brokers are healthy:
   ```bash
   docker exec kafka1 kafka-broker-api-versions --bootstrap-server localhost:9092
   ```

### Database connection issues

1. Check PostgreSQL is running:
   ```bash
   docker exec todo-postgres pg_isready
   ```
2. Verify DATABASE_URL in .env matches docker-compose settings

### Dapr not working

1. Ensure Dapr sidecar is running alongside backend
2. Check Dapr dashboard at http://localhost:8080 (if enabled)
3. Verify components in `dapr/components/` are correct

## Performance Tuning

### For development

Default settings are optimized for development with reasonable resource usage.

### For load testing

1. Increase Docker memory allocation to 8GB+
2. Scale services:
   ```bash
   docker-compose -f docker-compose.phase5.yml up -d --scale backend=3
   ```
3. Run load tests:
   ```bash
   cd tests/performance
   locust -f load_test.py --host=http://localhost:8000
   ```

## Grafana Dashboards

Pre-configured dashboards available:

1. **Backend API Metrics** - Request rates, latency, errors
2. **Kafka Metrics** - Broker health, consumer lag, throughput
3. **Business Metrics** - Task activity, completion rates

Access at http://localhost:3001 (admin/admin)

## Security Notes

- All default passwords should be changed in production
- JWT_SECRET must be at least 32 characters
- Kafka is configured without authentication for local dev
- Redis has no password for local dev

## Next Steps

- See `docs/CLOUD_DEPLOYMENT.md` for cloud deployment (Phase 5 Part C)
- See `docs/API_REFERENCE.md` for API documentation
- See `docs/ARCHITECTURE.md` for detailed architecture documentation
