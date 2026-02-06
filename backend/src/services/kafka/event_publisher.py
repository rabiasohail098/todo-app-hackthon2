"""Event publisher service for integrating Kafka events with API endpoints."""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from .producer import get_kafka_producer, KafkaProducerService
from .events import (
    TaskCreatedEvent,
    TaskUpdatedEvent,
    TaskCompletedEvent,
    TaskDeletedEvent,
    UserRegisteredEvent,
    NotificationSentEvent,
    Priority,
)

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    High-level event publisher for integrating with API endpoints.

    Publishes events asynchronously without blocking API responses.
    """

    def __init__(self):
        self._producer: Optional[KafkaProducerService] = None

    async def _get_producer(self) -> KafkaProducerService:
        """Get or initialize the Kafka producer."""
        if self._producer is None:
            self._producer = await get_kafka_producer()
        return self._producer

    async def publish_task_created(
        self,
        user_id: str,
        task_id: int,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Publish a task created event.

        Called after a task is successfully created in the database.
        """
        try:
            producer = await self._get_producer()

            # Map priority string to enum
            priority_enum = Priority.MEDIUM
            if priority == "high" or priority == "critical":
                priority_enum = Priority.HIGH
            elif priority == "low":
                priority_enum = Priority.LOW

            event = TaskCreatedEvent(
                user_id=user_id,
                task_id=str(task_id),
                title=title,
                description=description,
                priority=priority_enum,
                due_date=int(due_date.timestamp() * 1000) if due_date else None,
                tags=tags or [],
            )

            await producer.publish_task_created(event)
            logger.info(f"Published task.created event for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to publish task.created event: {e}")
            # Don't raise - event publishing should not break API

    async def publish_task_updated(
        self,
        user_id: str,
        task_id: int,
        changes: Dict[str, Any],
        previous_values: Dict[str, Any],
        new_values: Dict[str, Any],
    ) -> None:
        """
        Publish a task updated event.

        Called after a task is successfully updated in the database.
        """
        try:
            producer = await self._get_producer()

            # Convert all values to strings for the event
            str_changes = {k: str(v) for k, v in changes.items()}
            str_prev = {k: str(v) if v is not None else None for k, v in previous_values.items()}
            str_new = {k: str(v) if v is not None else None for k, v in new_values.items()}

            event = TaskUpdatedEvent(
                user_id=user_id,
                task_id=str(task_id),
                changes=str_changes,
                previous_values=str_prev,
                new_values=str_new,
            )

            await producer.publish_task_updated(event)
            logger.info(f"Published task.updated event for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to publish task.updated event: {e}")

    async def publish_task_completed(
        self,
        user_id: str,
        task_id: int,
        title: str,
        created_at: Optional[datetime] = None,
    ) -> None:
        """
        Publish a task completed event.

        Called when a task's is_completed field changes to True.
        """
        try:
            producer = await self._get_producer()

            # Calculate duration if we have created_at
            duration = None
            if created_at:
                duration = int((datetime.utcnow() - created_at).total_seconds() * 1000)

            event = TaskCompletedEvent(
                user_id=user_id,
                task_id=str(task_id),
                title=title,
                duration=duration,
            )

            await producer.publish_task_completed(event)
            logger.info(f"Published task.completed event for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to publish task.completed event: {e}")

    async def publish_task_deleted(
        self,
        user_id: str,
        task_id: int,
        title: str,
        reason: Optional[str] = None,
    ) -> None:
        """
        Publish a task deleted event.

        Called after a task is successfully deleted from the database.
        """
        try:
            producer = await self._get_producer()

            event = TaskDeletedEvent(
                user_id=user_id,
                task_id=str(task_id),
                title=title,
                reason=reason,
            )

            await producer.publish_task_deleted(event)
            logger.info(f"Published task.deleted event for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to publish task.deleted event: {e}")

    async def publish_user_registered(
        self,
        user_id: str,
        email: str,
        name: Optional[str] = None,
        source: str = "web",
    ) -> None:
        """
        Publish a user registered event.

        Called after a new user successfully registers.
        """
        try:
            producer = await self._get_producer()

            event = UserRegisteredEvent(
                user_id=user_id,
                email=email,
                name=name,
                registration_source=source,
            )

            await producer.publish_user_registered(event)
            logger.info(f"Published user.registered event for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to publish user.registered event: {e}")


# Background task helper for non-blocking event publishing
def publish_event_background(coro):
    """
    Schedule an event publishing coroutine to run in the background.

    This ensures API responses are not blocked by Kafka publishing.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(coro)
        else:
            loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create one
        asyncio.run(coro)


# Singleton instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get the singleton EventPublisher instance."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
