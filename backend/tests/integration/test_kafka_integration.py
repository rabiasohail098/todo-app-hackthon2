"""Integration tests for Kafka producer and consumer."""
import asyncio
import pytest
import os
from unittest.mock import patch, AsyncMock

# Skip tests if Kafka is not available
pytestmark = pytest.mark.skipif(
    os.getenv("KAFKA_ENABLED", "false").lower() != "true",
    reason="Kafka not enabled"
)


class TestKafkaProducer:
    """Test Kafka producer functionality."""

    @pytest.fixture
    def mock_aiokafka(self):
        """Mock aiokafka producer."""
        with patch("aiokafka.AIOKafkaProducer") as mock:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock()
            mock_instance.stop = AsyncMock()
            mock_instance.send_and_wait = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_producer_start(self, mock_aiokafka):
        """Test producer starts successfully."""
        from src.services.kafka.producer import KafkaProducerService

        producer = KafkaProducerService(bootstrap_servers="localhost:9092")
        await producer.start()

        assert producer._started is True
        mock_aiokafka.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_producer_stop(self, mock_aiokafka):
        """Test producer stops successfully."""
        from src.services.kafka.producer import KafkaProducerService

        producer = KafkaProducerService(bootstrap_servers="localhost:9092")
        await producer.start()
        await producer.stop()

        assert producer._started is False
        mock_aiokafka.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_task_created(self, mock_aiokafka):
        """Test publishing a task created event."""
        from src.services.kafka.producer import KafkaProducerService
        from src.services.kafka.events import TaskCreatedEvent

        # Setup mock response
        mock_result = AsyncMock()
        mock_result.partition = 0
        mock_result.offset = 42
        mock_aiokafka.send_and_wait.return_value = mock_result

        producer = KafkaProducerService(bootstrap_servers="localhost:9092")
        await producer.start()

        event = TaskCreatedEvent(
            user_id="user-123",
            task_id="task-456",
            title="Test Task",
            description="Test description",
        )

        result = await producer.publish_task_created(event)

        assert result is True
        mock_aiokafka.send_and_wait.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_task_completed(self, mock_aiokafka):
        """Test publishing a task completed event."""
        from src.services.kafka.producer import KafkaProducerService
        from src.services.kafka.events import TaskCompletedEvent

        mock_result = AsyncMock()
        mock_result.partition = 0
        mock_result.offset = 43
        mock_aiokafka.send_and_wait.return_value = mock_result

        producer = KafkaProducerService(bootstrap_servers="localhost:9092")
        await producer.start()

        event = TaskCompletedEvent(
            user_id="user-123",
            task_id="task-456",
            title="Test Task",
        )

        result = await producer.publish_task_completed(event)

        assert result is True


class TestKafkaConsumer:
    """Test Kafka consumer functionality."""

    @pytest.fixture
    def mock_consumer(self):
        """Mock aiokafka consumer."""
        with patch("aiokafka.AIOKafkaConsumer") as mock:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock()
            mock_instance.stop = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_consumer_start(self, mock_consumer):
        """Test consumer starts successfully."""
        from src.services.kafka.consumer import KafkaConsumerService

        consumer = KafkaConsumerService(
            bootstrap_servers="localhost:9092",
            group_id="test-group",
        )
        await consumer.start()

        assert consumer._started is True
        mock_consumer.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_handler(self):
        """Test registering event handlers."""
        from src.services.kafka.consumer import KafkaConsumerService

        consumer = KafkaConsumerService()

        async def test_handler(event):
            pass

        consumer.register_handler("task.created", test_handler)

        assert "task.created" in consumer._handlers
        assert consumer._handlers["task.created"] == test_handler


class TestEventFlow:
    """Test end-to-end event flow."""

    @pytest.mark.asyncio
    async def test_event_serialization(self):
        """Test event models serialize correctly."""
        from src.services.kafka.events import (
            TaskCreatedEvent,
            TaskUpdatedEvent,
            TaskDeletedEvent,
        )

        # Test TaskCreatedEvent
        event = TaskCreatedEvent(
            user_id="user-123",
            task_id="task-456",
            title="Test Task",
        )

        data = event.to_dict()

        assert data["user_id"] == "user-123"
        assert data["task_id"] == "task-456"
        assert data["title"] == "Test Task"
        assert "event_id" in data
        assert "event_timestamp" in data

    @pytest.mark.asyncio
    async def test_event_update_changes(self):
        """Test task update event captures changes."""
        from src.services.kafka.events import TaskUpdatedEvent

        event = TaskUpdatedEvent(
            user_id="user-123",
            task_id="task-456",
            changes={"title": "changed", "priority": "changed"},
            previous_values={"title": "Old Title", "priority": "low"},
            new_values={"title": "New Title", "priority": "high"},
        )

        data = event.to_dict()

        assert data["changes"]["title"] == "changed"
        assert data["previous_values"]["title"] == "Old Title"
        assert data["new_values"]["title"] == "New Title"
