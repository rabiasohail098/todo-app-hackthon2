"""Dapr Pub/Sub Service for event-driven messaging."""
import json
import logging
import os
from typing import Optional, Dict, Any, Callable, Awaitable
import aiohttp

logger = logging.getLogger(__name__)


class DaprPubSubService:
    """
    Dapr Pub/Sub Service using Kafka backend.

    Provides distributed pub/sub messaging with topic routing.
    """

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
        dapr_host: Optional[str] = None,
        dapr_port: Optional[int] = None,
        pubsub_name: str = "pubsub",
    ):
        self.dapr_host = dapr_host or os.getenv("DAPR_HOST", "localhost")
        self.dapr_port = dapr_port or int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.pubsub_name = pubsub_name
        self.base_url = f"http://{self.dapr_host}:{self.dapr_port}"

    async def publish(
        self,
        topic: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Publish a message to a Dapr pub/sub topic.

        Args:
            topic: Topic name
            data: Message data (will be JSON serialized)
            metadata: Optional metadata

        Returns:
            True if published successfully, False otherwise
        """
        url = f"{self.base_url}/v1.0/publish/{self.pubsub_name}/{topic}"

        headers = {"Content-Type": "application/json"}
        if metadata:
            for key, value in metadata.items():
                headers[f"metadata.{key}"] = value

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=data,
                    headers=headers,
                ) as response:
                    if response.status in (200, 201, 204):
                        logger.debug(f"Message published to {topic}")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"Failed to publish: {response.status} - {text}")
                        return False
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            return False

    # Convenience methods for each event type

    async def publish_task_created(
        self,
        user_id: str,
        task_id: str,
        title: str,
        **kwargs,
    ) -> bool:
        """Publish a task created event via Dapr."""
        event = {
            "user_id": user_id,
            "task_id": task_id,
            "title": title,
            **kwargs,
        }
        return await self.publish(self.TOPICS["task_created"], event)

    async def publish_task_updated(
        self,
        user_id: str,
        task_id: str,
        changes: Dict[str, Any],
    ) -> bool:
        """Publish a task updated event via Dapr."""
        event = {
            "user_id": user_id,
            "task_id": task_id,
            "changes": changes,
        }
        return await self.publish(self.TOPICS["task_updated"], event)

    async def publish_task_completed(
        self,
        user_id: str,
        task_id: str,
        title: str,
    ) -> bool:
        """Publish a task completed event via Dapr."""
        event = {
            "user_id": user_id,
            "task_id": task_id,
            "title": title,
        }
        return await self.publish(self.TOPICS["task_completed"], event)

    async def publish_task_deleted(
        self,
        user_id: str,
        task_id: str,
        title: str,
    ) -> bool:
        """Publish a task deleted event via Dapr."""
        event = {
            "user_id": user_id,
            "task_id": task_id,
            "title": title,
        }
        return await self.publish(self.TOPICS["task_deleted"], event)

    async def publish_user_registered(
        self,
        user_id: str,
        email: str,
        name: Optional[str] = None,
    ) -> bool:
        """Publish a user registered event via Dapr."""
        event = {
            "user_id": user_id,
            "email": email,
            "name": name,
        }
        return await self.publish(self.TOPICS["user_registered"], event)

    async def publish_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        body: str,
    ) -> bool:
        """Publish a notification event via Dapr."""
        event = {
            "user_id": user_id,
            "notification_type": notification_type,
            "title": title,
            "body": body,
        }
        return await self.publish(self.TOPICS["notification_sent"], event)


# Singleton instance
_dapr_pubsub_service: Optional[DaprPubSubService] = None


def get_dapr_pubsub_service() -> DaprPubSubService:
    """Get the singleton Dapr pub/sub service instance."""
    global _dapr_pubsub_service
    if _dapr_pubsub_service is None:
        _dapr_pubsub_service = DaprPubSubService()
    return _dapr_pubsub_service
