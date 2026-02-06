.PHONY: dev-up dev-down dev-logs dev-restart dev-init

# Start the complete system
dev-up:
	docker-compose -f docker-compose.phase5.yml up -d
	@echo "Waiting for services to start..."
	@sleep 30
	@echo "System started successfully!"
	@echo "Services available at:"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - Backend: http://localhost:8000"
	@echo "  - Kafka UI: http://localhost:8080"
	@echo "  - Grafana: http://localhost:3001"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Jaeger: http://localhost:16686"
	@echo "  - Kibana: http://localhost:5601"
	@echo "  - Elasticsearch: http://localhost:9200"

# Stop the complete system
dev-down:
	docker-compose -f docker-compose.phase5.yml down
	@echo "System stopped."

# Show logs from all services
dev-logs:
	docker-compose -f docker-compose.phase5.yml logs -f

# Restart the system
dev-restart:
	docker-compose -f docker-compose.phase5.yml restart
	@echo "System restarted."

# Initialize data and topics
dev-init:
	docker-compose -f docker-compose.phase5.yml exec kafka1 kafka-topics --create --topic task.created --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
	docker-compose -f docker-compose.phase5.yml exec kafka1 kafka-topics --create --topic task.updated --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
	docker-compose -f docker-compose.phase5.yml exec kafka1 kafka-topics --create --topic task.completed --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
	docker-compose -f docker-compose.phase5.yml exec kafka1 kafka-topics --create --topic task.deleted --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
	docker-compose -f docker-compose.phase5.yml exec kafka1 kafka-topics --create --topic user.registered --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
	docker-compose -f docker-compose.phase5.yml exec kafka1 kafka-topics --create --topic notification.sent --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
	@echo "Kafka topics created."

# Clean up everything including volumes
dev-clean:
	docker-compose -f docker-compose.phase5.yml down -v
	docker volume prune -f
	@echo "System cleaned up completely."

# Show status of all services
dev-status:
	docker-compose -f docker-compose.phase5.yml ps

# Rebuild images
dev-build:
	docker-compose -f docker-compose.phase5.yml build
	@echo "Images rebuilt."

# Scale specific services
scale-backend:
	docker-compose -f docker-compose.phase5.yml up -d --scale backend=2

scale-frontend:
	docker-compose -f docker-compose.phase5.yml up -d --scale frontend=2