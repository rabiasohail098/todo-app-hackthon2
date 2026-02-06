"""Dapr State Store Service for distributed state management."""
import json
import logging
import os
from typing import Optional, Dict, Any, List
import aiohttp

logger = logging.getLogger(__name__)


class DaprStateService:
    """
    Dapr State Store Service using Redis backend.

    Provides distributed state management with TTL support.
    """

    def __init__(
        self,
        dapr_host: Optional[str] = None,
        dapr_port: Optional[int] = None,
        store_name: str = "statestore",
    ):
        self.dapr_host = dapr_host or os.getenv("DAPR_HOST", "localhost")
        self.dapr_port = dapr_port or int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.store_name = store_name
        self.base_url = f"http://{self.dapr_host}:{self.dapr_port}"

    async def save_state(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Save state to the Dapr state store.

        Args:
            key: State key
            value: Value to store (will be JSON serialized)
            ttl_seconds: Optional TTL in seconds
            metadata: Optional metadata

        Returns:
            True if saved successfully, False otherwise
        """
        url = f"{self.base_url}/v1.0/state/{self.store_name}"

        state_item = {
            "key": key,
            "value": value,
        }

        if ttl_seconds:
            state_item["metadata"] = {"ttlInSeconds": str(ttl_seconds)}
        elif metadata:
            state_item["metadata"] = metadata

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=[state_item],
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status in (200, 201, 204):
                        logger.debug(f"State saved: {key}")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"Failed to save state: {response.status} - {text}")
                        return False
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            return False

    async def get_state(self, key: str) -> Optional[Any]:
        """
        Get state from the Dapr state store.

        Args:
            key: State key

        Returns:
            Stored value if found, None otherwise
        """
        url = f"{self.base_url}/v1.0/state/{self.store_name}/{key}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"State retrieved: {key}")
                        return data
                    elif response.status == 204:
                        # No content - key doesn't exist
                        return None
                    else:
                        text = await response.text()
                        logger.error(f"Failed to get state: {response.status} - {text}")
                        return None
        except Exception as e:
            logger.error(f"Error getting state: {e}")
            return None

    async def delete_state(self, key: str) -> bool:
        """
        Delete state from the Dapr state store.

        Args:
            key: State key

        Returns:
            True if deleted successfully, False otherwise
        """
        url = f"{self.base_url}/v1.0/state/{self.store_name}/{key}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url) as response:
                    if response.status in (200, 204):
                        logger.debug(f"State deleted: {key}")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"Failed to delete state: {response.status} - {text}")
                        return False
        except Exception as e:
            logger.error(f"Error deleting state: {e}")
            return False

    async def bulk_get_state(self, keys: List[str]) -> Dict[str, Any]:
        """
        Bulk get state from the Dapr state store.

        Args:
            keys: List of state keys

        Returns:
            Dictionary of key-value pairs
        """
        url = f"{self.base_url}/v1.0/state/{self.store_name}/bulk"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"keys": keys},
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status == 200:
                        items = await response.json()
                        result = {}
                        for item in items:
                            if item.get("data"):
                                result[item["key"]] = item["data"]
                        return result
                    else:
                        text = await response.text()
                        logger.error(f"Failed to bulk get state: {response.status} - {text}")
                        return {}
        except Exception as e:
            logger.error(f"Error bulk getting state: {e}")
            return {}

    # Convenience methods for common use cases

    async def cache_task(self, task_id: int, task_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache a task for quick retrieval."""
        return await self.save_state(f"task:{task_id}", task_data, ttl_seconds=ttl)

    async def get_cached_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a cached task."""
        return await self.get_state(f"task:{task_id}")

    async def cache_user_session(self, user_id: str, session_data: Dict[str, Any], ttl: int = 86400) -> bool:
        """Cache user session data."""
        return await self.save_state(f"session:{user_id}", session_data, ttl_seconds=ttl)

    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data."""
        return await self.get_state(f"session:{user_id}")

    async def invalidate_user_session(self, user_id: str) -> bool:
        """Invalidate user session."""
        return await self.delete_state(f"session:{user_id}")


# Singleton instance
_dapr_state_service: Optional[DaprStateService] = None


def get_dapr_state_service() -> DaprStateService:
    """Get the singleton Dapr state service instance."""
    global _dapr_state_service
    if _dapr_state_service is None:
        _dapr_state_service = DaprStateService()
    return _dapr_state_service
