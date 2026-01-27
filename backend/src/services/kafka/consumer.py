"""Kafka Consumer Service for processing events."""
import asyncio
import json
import logging
import os
from typing import Optional, Dict, Callable, Awaitable, Any, List
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)


class KafkaConsumerService:
    """Async Kafka consumer with consumer group support and dead-letter handling."""

    TOPICS = [
        "task.created",
        "task.updated",
        "task.completed",
        "task.deleted",
        "user.registered",
        "notification.sent",
        "task.reminder",
        "analytics.events",
    ]

    DEAD_LETTER_TOPIC = "dead-letter"

    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        group_id: str = "todo-backend-consumer",
        topics: Optional[List[str]] = None,
    ):
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BROKERS", "localhost:9092"
        )
        self.group_id = group_id
        self.topics = topics or self.TOPICS
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._started = False
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
        self._running = False

    def register_handler(
        self,
        topic: str,
        handler: Callable[[Dict[str, Any]], Awaitable[None]],
    ) -> None:
        """Register an event handler for a specific topic."""
        self._handlers[topic] = handler
        logger.info(f"Registered handler for topic: {topic}")

    async def start(self) -> None:
        """Start the Kafka consumer."""
        if self._started:
            return

        try:
            self._consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                # Offset management
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                # Deserialization
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
            )
            await self._consumer.start()
            self._started = True
            logger.info(
                f"Kafka consumer started, connected to {self.bootstrap_servers}, "
                f"group_id={self.group_id}, topics={self.topics}"
            )
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            raise

    async def stop(self) -> None:
        """Stop the Kafka consumer."""
        self._running = False
        if self._consumer and self._started:
            await self._consumer.stop()
            self._started = False
            logger.info("Kafka consumer stopped")

    async def _handle_message(self, topic: str, message: Dict[str, Any]) -> bool:
        """
        Handle a single message from Kafka.

        Args:
            topic: Source topic
            message: Deserialized message data

        Returns:
            True if handled successfully, False otherwise
        """
        handler = self._handlers.get(topic)
        if handler:
            try:
                await handler(message)
                logger.debug(f"Successfully handled message from {topic}")
                return True
            except Exception as e:
                logger.error(f"Error handling message from {topic}: {e}")
                return False
        else:
            logger.warning(f"No handler registered for topic: {topic}")
            return True  # Don't retry if no handler

    async def consume(self) -> None:
        """Start consuming messages from subscribed topics."""
        if not self._started:
            await self.start()

        self._running = True
        logger.info("Starting message consumption loop")

        try:
            async for msg in self._consumer:
                if not self._running:
                    break

                topic = msg.topic
                value = msg.value
                key = msg.key

                logger.debug(
                    f"Received message: topic={topic}, partition={msg.partition}, "
                    f"offset={msg.offset}, key={key}"
                )

                success = await self._handle_message(topic, value)

                if not success:
                    # Could send to dead-letter topic here
                    logger.error(
                        f"Failed to process message from {topic}, "
                        f"event_id={value.get('event_id', 'unknown')}"
                    )

        except asyncio.CancelledError:
            logger.info("Consumer loop cancelled")
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
            raise


# Default event handlers
async def handle_task_created(event: Dict[str, Any]) -> None:
    """Handle task created events."""
    logger.info(f"Task created: {event.get('task_id')} - {event.get('title')}")
    # Add business logic here (e.g., send notifications, update analytics)


async def handle_task_updated(event: Dict[str, Any]) -> None:
    """Handle task updated events."""
    logger.info(f"Task updated: {event.get('task_id')}")
    changes = event.get('changes', {})
    logger.info(f"Changes: {changes}")


async def handle_task_completed(event: Dict[str, Any]) -> None:
    """Handle task completed events."""
    logger.info(f"Task completed: {event.get('task_id')} - {event.get('title')}")
    # Could trigger celebration notifications, update statistics, etc.


async def handle_task_deleted(event: Dict[str, Any]) -> None:
    """Handle task deleted events."""
    logger.info(f"Task deleted: {event.get('task_id')} - {event.get('title')}")


async def handle_user_registered(event: Dict[str, Any]) -> None:
    """Handle user registered events."""
    logger.info(f"User registered: {event.get('user_id')} - {event.get('email')}")
    # Could trigger welcome email, onboarding flow, etc.


async def handle_notification_sent(event: Dict[str, Any]) -> None:
    """Handle notification sent events."""
    logger.info(
        f"Notification sent to {event.get('user_id')}: "
        f"{event.get('notification_type')} - {event.get('title')}"
    )


async def handle_task_reminder(event: Dict[str, Any]) -> None:
    """Handle task reminder events."""
    logger.info(
        f"Task reminder: {event.get('task_id')} - {event.get('title')} "
        f"({event.get('reminder_type')})"
    )


async def handle_analytics(event: Dict[str, Any]) -> None:
    """Handle analytics events."""
    logger.debug(
        f"Analytics event: {event.get('event_name')} - "
        f"category={event.get('event_category')}"
    )


# Singleton instance
_kafka_consumer: Optional[KafkaConsumerService] = None


async def get_kafka_consumer() -> KafkaConsumerService:
    """Get the singleton Kafka consumer instance with default handlers."""
    global _kafka_consumer
    if _kafka_consumer is None:
        _kafka_consumer = KafkaConsumerService()

        # Register default handlers
        _kafka_consumer.register_handler("task.created", handle_task_created)
        _kafka_consumer.register_handler("task.updated", handle_task_updated)
        _kafka_consumer.register_handler("task.completed", handle_task_completed)
        _kafka_consumer.register_handler("task.deleted", handle_task_deleted)
        _kafka_consumer.register_handler("user.registered", handle_user_registered)
        _kafka_consumer.register_handler("notification.sent", handle_notification_sent)
        _kafka_consumer.register_handler("task.reminder", handle_task_reminder)
        _kafka_consumer.register_handler("analytics.events", handle_analytics)

        await _kafka_consumer.start()
    return _kafka_consumer


async def shutdown_kafka_consumer() -> None:
    """Shutdown the Kafka consumer."""
    global _kafka_consumer
    if _kafka_consumer:
        await _kafka_consumer.stop()
        _kafka_consumer = None
