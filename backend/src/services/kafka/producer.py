"""Kafka Producer Service for publishing events."""
import asyncio
import json
import logging
import os
from typing import Optional, Dict, Any
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from .events import (
    BaseEvent,
    TaskCreatedEvent,
    TaskUpdatedEvent,
    TaskCompletedEvent,
    TaskDeletedEvent,
    UserRegisteredEvent,
    NotificationSentEvent,
    TaskReminderEvent,
    AnalyticsEvent,
)

logger = logging.getLogger(__name__)


class KafkaProducerService:
    """Async Kafka producer with idempotent publishing and retry logic."""

    TOPICS = {
        "task_created": "task.created",
        "task_updated": "task.updated",
        "task_completed": "task.completed",
        "task_deleted": "task.deleted",
        "user_registered": "user.registered",
        "notification_sent": "notification.sent",
        "task_reminder": "task.reminder",
        "analytics": "analytics.events",
    }

    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        client_id: str = "todo-backend-producer",
    ):
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BROKERS", "localhost:9092"
        )
        self.client_id = client_id
        self._producer: Optional[AIOKafkaProducer] = None
        self._started = False

    async def start(self) -> None:
        """Start the Kafka producer."""
        if self._started:
            return

        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                # Idempotent producer settings
                enable_idempotence=True,
                acks="all",
                # Retry settings
                retries=5,
                retry_backoff_ms=100,
                # Serialization
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            await self._producer.start()
            self._started = True
            logger.info(f"Kafka producer started, connected to {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self._producer and self._started:
            await self._producer.stop()
            self._started = False
            logger.info("Kafka producer stopped")

    async def _publish(
        self,
        topic: str,
        event: BaseEvent,
        key: Optional[str] = None,
    ) -> bool:
        """
        Publish an event to a Kafka topic.

        Args:
            topic: Target Kafka topic
            event: Event to publish
            key: Optional partition key

        Returns:
            True if published successfully, False otherwise
        """
        if not self._started:
            await self.start()

        try:
            event_data = event.to_dict()
            result = await self._producer.send_and_wait(
                topic=topic,
                value=event_data,
                key=key,
            )
            logger.debug(
                f"Published event to {topic}: partition={result.partition}, "
                f"offset={result.offset}, event_id={event.event_id}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            return False

    # Convenience methods for each event type
    async def publish_task_created(self, event: TaskCreatedEvent) -> bool:
        """Publish a task created event."""
        return await self._publish(
            self.TOPICS["task_created"],
            event,
            key=event.task_id,
        )

    async def publish_task_updated(self, event: TaskUpdatedEvent) -> bool:
        """Publish a task updated event."""
        return await self._publish(
            self.TOPICS["task_updated"],
            event,
            key=event.task_id,
        )

    async def publish_task_completed(self, event: TaskCompletedEvent) -> bool:
        """Publish a task completed event."""
        return await self._publish(
            self.TOPICS["task_completed"],
            event,
            key=event.task_id,
        )

    async def publish_task_deleted(self, event: TaskDeletedEvent) -> bool:
        """Publish a task deleted event."""
        return await self._publish(
            self.TOPICS["task_deleted"],
            event,
            key=event.task_id,
        )

    async def publish_user_registered(self, event: UserRegisteredEvent) -> bool:
        """Publish a user registered event."""
        return await self._publish(
            self.TOPICS["user_registered"],
            event,
            key=event.user_id,
        )

    async def publish_notification_sent(self, event: NotificationSentEvent) -> bool:
        """Publish a notification sent event."""
        return await self._publish(
            self.TOPICS["notification_sent"],
            event,
            key=event.user_id,
        )

    async def publish_task_reminder(self, event: TaskReminderEvent) -> bool:
        """Publish a task reminder event."""
        return await self._publish(
            self.TOPICS["task_reminder"],
            event,
            key=event.task_id,
        )

    async def publish_analytics(self, event: AnalyticsEvent) -> bool:
        """Publish an analytics event."""
        return await self._publish(
            self.TOPICS["analytics"],
            event,
            key=event.session_id,
        )


# Singleton instance
_kafka_producer: Optional[KafkaProducerService] = None


async def get_kafka_producer() -> KafkaProducerService:
    """Get the singleton Kafka producer instance."""
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = KafkaProducerService()
        await _kafka_producer.start()
    return _kafka_producer


async def shutdown_kafka_producer() -> None:
    """Shutdown the Kafka producer."""
    global _kafka_producer
    if _kafka_producer:
        await _kafka_producer.stop()
        _kafka_producer = None
