#!/bin/bash
# init-data.sh
# Script to initialize data for the Todo application with Kafka and PostgreSQL

set -e

echo "Starting data initialization..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec todo-postgres pg_isready > /dev/null 2>&1
do
    sleep 2
    echo "Waiting for PostgreSQL..."
done
echo "PostgreSQL is ready!"

# Create database schema if not exists
echo "Creating database schema..."
docker exec todo-postgres psql -U postgres -d todo_db -c "
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_events (
    id SERIAL PRIMARY KEY,
    task_id INTEGER,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_task_events_type ON task_events(event_type);
"

echo "Database schema created successfully!"

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
until docker exec kafka1 kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1
do
    sleep 5
    echo "Waiting for Kafka..."
done
echo "Kafka is ready!"

# Create Kafka topics
echo "Creating Kafka topics..."
docker exec kafka1 kafka-topics --create --topic task.created --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists
docker exec kafka1 kafka-topics --create --topic task.updated --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists
docker exec kafka1 kafka-topics --create --topic task.completed --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists
docker exec kafka1 kafka-topics --create --topic task.deleted --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists
docker exec kafka1 kafka-topics --create --topic user.registered --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists
docker exec kafka1 kafka-topics --create --topic notification.sent --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists

echo "Kafka topics created successfully!"

# Insert sample data
echo "Inserting sample data..."
docker exec todo-postgres psql -U postgres -d todo_db -c "
INSERT INTO users (email, name) VALUES ('admin@example.com', 'Admin User') ON CONFLICT (email) DO NOTHING;
INSERT INTO tasks (title, description, status, priority, due_date)
VALUES
    ('Setup Kafka Integration', 'Integrate Kafka for event streaming', 'completed', 'high', NOW() + INTERVAL '1 day'),
    ('Configure Dapr', 'Set up Dapr for microservices', 'in-progress', 'medium', NOW() + INTERVAL '2 days'),
    ('Implement Monitoring', 'Add Prometheus and Grafana', 'pending', 'low', NOW() + INTERVAL '3 days')
ON CONFLICT DO NOTHING;
"

echo "Sample data inserted!"

# Register schemas in Schema Registry
echo "Registering schemas in Schema Registry..."
sleep 10  # Wait for schema registry to be fully ready

# Create a temporary file for the task.created schema
cat > /tmp/task_created_schema.json << 'EOF'
{
  "schema": "{ \"type\": \"record\", \"name\": \"TaskCreated\", \"fields\": [ { \"name\": \"eventId\", \"type\": \"string\" }, { \"name\": \"eventTimestamp\", \"type\": \"long\" }, { \"name\": \"userId\", \"type\": \"string\" }, { \"name\": \"taskId\", \"type\": \"string\" }, { \"name\": \"title\", \"type\": \"string\" }, { \"name\": \"description\", \"type\": \"string\" }, { \"name\": \"priority\", \"type\": \"string\" }, { \"name\": \"dueDate\", \"type\": \"long\" }, { \"name\": \"categoryId\", \"type\": \"string\" }, { \"name\": \"tags\", \"type\": { \"type\": \"array\", \"items\": \"string\" } } ] }",
  "schemaType": "AVRO"
}
EOF

# Register the schema
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data @/tmp/task_created_schema.json \
  http://localhost:8081/subjects/task.created-value/versions || echo "Schema registry not available yet, continuing..."

rm -f /tmp/task_created_schema.json

echo "Initialization completed successfully!"
echo ""
echo "Services available at:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend: http://localhost:8000"
echo "  - Kafka UI: http://localhost:8080"
echo "  - Grafana: http://localhost:3001"
echo "  - Prometheus: http://localhost:9090"
echo "  - Jaeger: http://localhost:16686"
echo "  - Kibana: http://localhost:5601"