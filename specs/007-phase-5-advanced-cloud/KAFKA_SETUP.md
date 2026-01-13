# Kafka Setup for Phase V

## Kafka Architecture in Todo App

### Overview

Kafka serves as the event streaming backbone for the distributed Todo application. It enables:
- Decoupled service communication
- Event sourcing and audit trails
- Real-time notifications
- Analytics and reporting
- Message replay for debugging

## Kafka Topics Design

### Primary Topics

| Topic | Partition | Replication | Retention | Key Format | Purpose |
|-------|-----------|-------------|-----------|-----------|---------|
| task.created | 3 | 3 | 7d | userId | Task creation events |
| task.updated | 3 | 3 | 7d | taskId | Task modification events |
| task.completed | 3 | 3 | 7d | taskId | Task completion tracking |
| task.deleted | 3 | 3 | 7d | taskId | Task deletion events |
| user.registered | 3 | 3 | 30d | userId | User signup tracking |
| user.authenticated | 1 | 3 | 1d | userId | Login activity |
| notification.sent | 3 | 3 | 7d | notificationId | Email/SMS delivery |
| reminder.triggered | 3 | 3 | 7d | reminderId | Due date reminders |

### Event Schema (Avro)

#### task.created Event
```avro
{
  "type": "record",
  "name": "TaskCreatedEvent",
  "namespace": "com.todoapp.events",
  "fields": [
    {
      "name": "eventId",
      "type": "string",
      "doc": "Unique event identifier (UUID)"
    },
    {
      "name": "eventTimestamp",
      "type": "long",
      "doc": "Event creation timestamp (milliseconds)"
    },
    {
      "name": "userId",
      "type": "string",
      "doc": "User ID who created the task"
    },
    {
      "name": "taskId",
      "type": "string",
      "doc": "New task ID"
    },
    {
      "name": "title",
      "type": "string",
      "doc": "Task title"
    },
    {
      "name": "description",
      "type": ["null", "string"],
      "default": null,
      "doc": "Task description"
    },
    {
      "name": "priority",
      "type": {
        "type": "enum",
        "name": "Priority",
        "symbols": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
      },
      "default": "MEDIUM"
    },
    {
      "name": "dueDate",
      "type": ["null", "long"],
      "default": null,
      "doc": "Due date timestamp (milliseconds)"
    },
    {
      "name": "categoryId",
      "type": ["null", "string"],
      "default": null
    },
    {
      "name": "tags",
      "type": {
        "type": "array",
        "items": "string"
      },
      "default": []
    }
  ]
}
```

#### task.completed Event
```avro
{
  "type": "record",
  "name": "TaskCompletedEvent",
  "namespace": "com.todoapp.events",
  "fields": [
    {
      "name": "eventId",
      "type": "string"
    },
    {
      "name": "eventTimestamp",
      "type": "long"
    },
    {
      "name": "userId",
      "type": "string"
    },
    {
      "name": "taskId",
      "type": "string"
    },
    {
      "name": "completedAt",
      "type": "long",
      "doc": "Completion timestamp"
    },
    {
      "name": "timeToComplete",
      "type": ["null", "long"],
      "default": null,
      "doc": "Time from creation to completion (ms)"
    }
  ]
}
```

## Local Kafka Setup (Docker)

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - todo-network
    healthcheck:
      test: [ "CMD", "echo", "ruok", "|", "nc", "localhost", "2181" ]
      interval: 10s
      timeout: 5s
      retries: 5

  kafka1:
    image: confluentinc/cp-kafka:7.5.0
    container_name: kafka1
    ports:
      - "9092:9092"
      - "19092:19092"
    depends_on:
      zookeeper:
        condition: service_healthy
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka1:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_DELETE_TOPIC_ENABLE: "true"
      KAFKA_LOG_RETENTION_HOURS: 24
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
    networks:
      - todo-network
    healthcheck:
      test: kafka-broker-api-versions --bootstrap-server kafka1:9092
      interval: 10s
      timeout: 5s
      retries: 5

  kafka2:
    image: confluentinc/cp-kafka:7.5.0
    container_name: kafka2
    ports:
      - "9093:9093"
    depends_on:
      zookeeper:
        condition: service_healthy
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka2:29093,PLAINTEXT_HOST://localhost:9093
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 2
    networks:
      - todo-network
    healthcheck:
      test: kafka-broker-api-versions --bootstrap-server kafka2:9093
      interval: 10s
      timeout: 5s
      retries: 5

  kafka3:
    image: confluentinc/cp-kafka:7.5.0
    container_name: kafka3
    ports:
      - "9094:9094"
    depends_on:
      zookeeper:
        condition: service_healthy
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka3:29094,PLAINTEXT_HOST://localhost:9094
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
    networks:
      - todo-network
    healthcheck:
      test: kafka-broker-api-versions --bootstrap-server kafka3:9094
      interval: 10s
      timeout: 5s
      retries: 5

  schema-registry:
    image: confluentinc/cp-schema-registry:7.5.0
    container_name: schema-registry
    ports:
      - "8081:8081"
    depends_on:
      kafka1:
        condition: service_healthy
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka1:29092,kafka2:29093,kafka3:29094
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
    networks:
      - todo-network
    healthcheck:
      test: curl --fail http://localhost:8081/subjects
      interval: 10s
      timeout: 5s
      retries: 5

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8080:8080"
    depends_on:
      - kafka1
      - kafka2
      - kafka3
      - schema-registry
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka1:29092,kafka2:29093,kafka3:29094
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
      KAFKA_CLUSTERS_0_SCHEMAREGISTRY: http://schema-registry:8081
    networks:
      - todo-network

networks:
  todo-network:
    driver: bridge
```

### Topic Creation Script

```bash
#!/bin/bash
# create-topics.sh

BOOTSTRAP_SERVERS="localhost:9092"

# Function to create topic
create_topic() {
  local topic=$1
  local partitions=$2
  local replication=$3
  
  docker exec kafka1 kafka-topics \
    --bootstrap-server $BOOTSTRAP_SERVERS \
    --create \
    --if-not-exists \
    --topic $topic \
    --partitions $partitions \
    --replication-factor $replication \
    --config retention.ms=604800000 \
    --config compression.type=snappy
}

# Create topics
create_topic "task.created" 3 3
create_topic "task.updated" 3 3
create_topic "task.completed" 3 3
create_topic "task.deleted" 3 3
create_topic "user.registered" 3 3
create_topic "user.authenticated" 1 3
create_topic "notification.sent" 3 3
create_topic "reminder.triggered" 3 3

# Verify topics
echo "Topics created:"
docker exec kafka1 kafka-topics \
  --bootstrap-server $BOOTSTRAP_SERVERS \
  --list
```

## Kafka Producer Implementation

### FastAPI Producer Service

```python
# backend/src/services/kafka_producer.py

import json
import logging
from typing import Any, Dict
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONDeserializer, JSONSerializer
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class KafkaProducerService:
    def __init__(
        self, 
        bootstrap_servers: str = "localhost:9092",
        schema_registry_url: str = "http://localhost:8081"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'todo-app-producer',
            'acks': 'all',  # Wait for all replicas
            'retries': 3,
            'max.in.flight.requests.per.connection': 5
        })
        
        self.schema_registry = SchemaRegistryClient({
            'url': schema_registry_url
        })
    
    async def publish_task_created(
        self, 
        user_id: str, 
        task_id: str, 
        title: str,
        description: str = None,
        priority: str = "MEDIUM",
        due_date: int = None,
        category_id: str = None,
        tags: list = None
    ):
        """Publish task.created event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventTimestamp': int(datetime.now().timestamp() * 1000),
            'userId': user_id,
            'taskId': task_id,
            'title': title,
            'description': description,
            'priority': priority,
            'dueDate': due_date,
            'categoryId': category_id,
            'tags': tags or []
        }
        
        await self._publish(
            topic='task.created',
            key=user_id,
            value=event
        )
    
    async def publish_task_completed(
        self,
        user_id: str,
        task_id: str,
        completed_at: int = None,
        time_to_complete: int = None
    ):
        """Publish task.completed event"""
        event = {
            'eventId': str(uuid.uuid4()),
            'eventTimestamp': int(datetime.now().timestamp() * 1000),
            'userId': user_id,
            'taskId': task_id,
            'completedAt': completed_at or int(datetime.now().timestamp() * 1000),
            'timeToComplete': time_to_complete
        }
        
        await self._publish(
            topic='task.completed',
            key=task_id,
            value=event
        )
    
    async def _publish(self, topic: str, key: str, value: Dict[str, Any]):
        """Internal method to publish event"""
        try:
            self.producer.produce(
                topic=topic,
                key=key.encode('utf-8'),
                value=json.dumps(value).encode('utf-8'),
                callback=self._delivery_report
            )
            self.producer.flush()
            logger.info(f"Event published to {topic}: {value['eventId']}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    @staticmethod
    def _delivery_report(err, msg):
        """Callback for producer delivery reports"""
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")
    
    def close(self):
        """Close producer connection"""
        self.producer.flush()
```

## Kafka Consumer Implementation

### Event Consumer Service

```python
# backend/src/services/kafka_consumer.py

import json
import asyncio
import logging
from typing import Callable, Dict, Any
from confluent_kafka import Consumer, KafkaError

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "todo-app-consumers"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = None
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, topic: str, handler: Callable):
        """Register event handler for topic"""
        self.handlers[topic] = handler
        logger.info(f"Handler registered for {topic}")
    
    async def start(self, topics: list):
        """Start consumer for given topics"""
        self.consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'session.timeout.ms': 6000,
            'client.id': f'{self.group_id}-consumer'
        })
        
        self.consumer.subscribe(topics)
        logger.info(f"Subscribed to topics: {topics}")
        
        # Start consuming in background
        asyncio.create_task(self._consume_loop())
    
    async def _consume_loop(self):
        """Main consumer loop"""
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        break
                
                await self._process_message(msg)
        except Exception as e:
            logger.error(f"Consumer loop error: {e}")
        finally:
            self.consumer.close()
    
    async def _process_message(self, msg):
        """Process incoming message"""
        try:
            topic = msg.topic()
            value = json.loads(msg.value().decode('utf-8'))
            
            if topic in self.handlers:
                handler = self.handlers[topic]
                await handler(value)
                logger.info(f"Processed {topic}: {value['eventId']}")
            else:
                logger.warning(f"No handler for topic: {topic}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
```

## Kafka Commands Reference

### Topic Management
```bash
# List topics
docker exec kafka1 kafka-topics --bootstrap-server localhost:9092 --list

# Describe topic
docker exec kafka1 kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic task.created

# Create topic
docker exec kafka1 kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic test-topic \
  --partitions 3 \
  --replication-factor 3

# Delete topic
docker exec kafka1 kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic test-topic
```

### Consumer Groups
```bash
# List consumer groups
docker exec kafka1 kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --list

# Describe consumer group
docker exec kafka1 kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group todo-app-consumers

# Reset offset
docker exec kafka1 kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group todo-app-consumers \
  --reset-offsets \
  --to-earliest \
  --execute \
  --all-topics
```

### Message Production/Consumption
```bash
# Produce message
docker exec -it kafka1 kafka-console-producer \
  --broker-list localhost:9092 \
  --topic task.created \
  --property "key.separator=:" \
  --property "parse.key=true"

# Consume messages
docker exec kafka1 kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic task.created \
  --from-beginning \
  --property print.key=true \
  --property print.partition=true
```

## Monitoring & Troubleshooting

### Kafka UI
- URL: http://localhost:8080
- Monitor topics, partitions, consumer groups
- View messages in real-time
- Monitor broker metrics

### Common Issues

**Issue**: Consumer lag increasing
- Check if consumer is running
- Monitor network connectivity
- Check for processing bottlenecks

**Issue**: Messages not being produced
- Verify broker connectivity
- Check topic exists
- Review producer logs

**Issue**: Partition imbalance
- Trigger rebalancing
- Check broker disk space
- Monitor broker performance

## Best Practices

1. **Idempotency**: Design consumers to handle duplicate messages
2. **Ordering**: Use same partition key for related events
3. **Retention**: Set appropriate retention based on use case
4. **Monitoring**: Track consumer lag continuously
5. **Schemas**: Enforce Avro/Protobuf schemas in production
6. **Error Handling**: Implement dead-letter topics for failed messages
7. **Performance**: Tune batch size and compression
