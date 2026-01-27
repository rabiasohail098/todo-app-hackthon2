"""Integration tests for Dapr services."""
import asyncio
import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock

# Skip tests if Dapr is not available
pytestmark = pytest.mark.skipif(
    os.getenv("DAPR_HOST") is None,
    reason="Dapr not configured"
)


class TestDaprStateService:
    """Test Dapr state store functionality."""

    @pytest.fixture
    def mock_aiohttp(self):
        """Mock aiohttp session."""
        with patch("aiohttp.ClientSession") as mock:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"data": "test"})
            mock_response.text = AsyncMock(return_value="")

            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session.delete = AsyncMock(return_value=mock_response)

            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock.return_value = mock_session
            yield mock_session

    @pytest.mark.asyncio
    async def test_save_state(self, mock_aiohttp):
        """Test saving state to Dapr."""
        from src.services.dapr.state_service import DaprStateService

        service = DaprStateService(dapr_host="localhost", dapr_port=3500)

        result = await service.save_state("test-key", {"value": "test"})

        assert result is True

    @pytest.mark.asyncio
    async def test_get_state(self, mock_aiohttp):
        """Test getting state from Dapr."""
        from src.services.dapr.state_service import DaprStateService

        mock_aiohttp.get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"value": "test"}
        )

        service = DaprStateService(dapr_host="localhost", dapr_port=3500)

        result = await service.get_state("test-key")

        assert result is not None

    @pytest.mark.asyncio
    async def test_delete_state(self, mock_aiohttp):
        """Test deleting state from Dapr."""
        from src.services.dapr.state_service import DaprStateService

        mock_aiohttp.delete.return_value.__aenter__.return_value.status = 204

        service = DaprStateService(dapr_host="localhost", dapr_port=3500)

        result = await service.delete_state("test-key")

        assert result is True

    @pytest.mark.asyncio
    async def test_cache_task(self, mock_aiohttp):
        """Test caching a task."""
        from src.services.dapr.state_service import DaprStateService

        service = DaprStateService(dapr_host="localhost", dapr_port=3500)

        result = await service.cache_task(
            task_id=123,
            task_data={"title": "Test Task", "status": "pending"},
            ttl=3600
        )

        assert result is True


class TestDaprPubSubService:
    """Test Dapr pub/sub functionality."""

    @pytest.fixture
    def mock_aiohttp(self):
        """Mock aiohttp session."""
        with patch("aiohttp.ClientSession") as mock:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 204
            mock_response.text = AsyncMock(return_value="")

            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = AsyncMock(return_value=mock_response)

            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock.return_value = mock_session
            yield mock_session

    @pytest.mark.asyncio
    async def test_publish_message(self, mock_aiohttp):
        """Test publishing a message via Dapr."""
        from src.services.dapr.pubsub_service import DaprPubSubService

        service = DaprPubSubService(dapr_host="localhost", dapr_port=3500)

        result = await service.publish(
            topic="task.created",
            data={"task_id": "123", "title": "Test"}
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_publish_task_created(self, mock_aiohttp):
        """Test publishing task created event via Dapr."""
        from src.services.dapr.pubsub_service import DaprPubSubService

        service = DaprPubSubService(dapr_host="localhost", dapr_port=3500)

        result = await service.publish_task_created(
            user_id="user-123",
            task_id="task-456",
            title="Test Task"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_publish_task_completed(self, mock_aiohttp):
        """Test publishing task completed event via Dapr."""
        from src.services.dapr.pubsub_service import DaprPubSubService

        service = DaprPubSubService(dapr_host="localhost", dapr_port=3500)

        result = await service.publish_task_completed(
            user_id="user-123",
            task_id="task-456",
            title="Test Task"
        )

        assert result is True
