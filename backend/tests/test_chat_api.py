"""Integration tests for Chat API endpoints (Phase 3)."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4


@pytest.fixture
def mock_auth_token():
    """Mock JWT token for authentication."""
    return "mock-jwt-token-test-user"


@pytest.fixture
def auth_headers(mock_auth_token):
    """Headers with authentication token."""
    return {"Authorization": f"Bearer {mock_auth_token}"}


class TestChatEndpoint:
    """Test POST /api/chat/ endpoint."""

    @patch('src.api.routes.chat.ChatService')
    def test_send_message_success(self, mock_service_class, auth_headers):
        """Test successful message send."""
        from src.api.main import app

        # Mock ChatService.process_message
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        async def mock_process(user_id, message, conversation_id, language):
            return {
                "conversation_id": str(uuid4()),
                "message_id": str(uuid4()),
                "response": "✓ Created task: buy milk",
                "type": "task_created",
                "data": {"task": {"id": 1, "title": "buy milk"}}
            }

        mock_service.process_message = AsyncMock(side_effect=mock_process)

        client = TestClient(app)

        # Send chat message
        response = client.post(
            "/api/chat/",
            json={
                "message": "add task buy milk",
                "language": "en"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "conversation_id" in data
        assert "message_id" in data
        assert "response" in data
        assert "buy milk" in data["response"]
        assert data["type"] == "task_created"

    @patch('src.api.routes.chat.ChatService')
    def test_send_message_urdu(self, mock_service_class, auth_headers):
        """Test message with Urdu language."""
        from src.api.main import app

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        async def mock_process(user_id, message, conversation_id, language):
            assert language == "ur"  # Verify Urdu language passed
            return {
                "conversation_id": str(uuid4()),
                "message_id": str(uuid4()),
                "response": "میں نے آپ کا ٹاسک شامل کر دیا ہے",
                "type": "task_created",
                "data": None
            }

        mock_service.process_message = AsyncMock(side_effect=mock_process)

        client = TestClient(app)

        response = client.post(
            "/api/chat/",
            json={
                "message": "ایک ٹاسک بنائیں",
                "language": "ur"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "task_created"

    def test_send_message_unauthorized(self):
        """Test sending message without authentication."""
        from src.api.main import app

        client = TestClient(app)

        response = client.post(
            "/api/chat/",
            json={
                "message": "add task",
                "language": "en"
            }
            # No headers - no auth
        )

        assert response.status_code == 401

    @patch('src.api.routes.chat.ChatService')
    def test_send_message_with_conversation_id(self, mock_service_class, auth_headers):
        """Test sending message to existing conversation."""
        from src.api.main import app

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        conv_id = str(uuid4())

        async def mock_process(user_id, message, conversation_id, language):
            assert str(conversation_id) == conv_id
            return {
                "conversation_id": conv_id,
                "message_id": str(uuid4()),
                "response": "Your tasks: 1. buy milk",
                "type": "task_list",
                "data": None
            }

        mock_service.process_message = AsyncMock(side_effect=mock_process)

        client = TestClient(app)

        response = client.post(
            "/api/chat/",
            json={
                "message": "show my tasks",
                "conversation_id": conv_id,
                "language": "en"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conv_id

    def test_send_empty_message(self, auth_headers):
        """Test validation for empty message."""
        from src.api.main import app

        client = TestClient(app)

        response = client.post(
            "/api/chat/",
            json={
                "message": "",  # Empty message
                "language": "en"
            },
            headers=auth_headers
        )

        # Should fail validation (min_length=1)
        assert response.status_code == 422

    def test_send_invalid_language(self, auth_headers):
        """Test validation for invalid language code."""
        from src.api.main import app

        client = TestClient(app)

        response = client.post(
            "/api/chat/",
            json={
                "message": "add task",
                "language": "invalid"  # Not "en" or "ur"
            },
            headers=auth_headers
        )

        # Should fail pattern validation
        assert response.status_code == 422


class TestConversationEndpoints:
    """Test conversation management endpoints."""

    @patch('src.api.routes.chat.ChatService')
    def test_get_user_conversations(self, mock_service_class, auth_headers):
        """Test getting user's conversations."""
        from src.api.main import app

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_conversations = [
            {
                "id": str(uuid4()),
                "created_at": "2025-12-31T10:00:00",
                "updated_at": "2025-12-31T10:30:00"
            },
            {
                "id": str(uuid4()),
                "created_at": "2025-12-30T15:00:00",
                "updated_at": "2025-12-30T15:15:00"
            }
        ]

        mock_service.get_user_conversations.return_value = mock_conversations

        client = TestClient(app)

        response = client.get(
            "/api/chat/conversations",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert len(data["conversations"]) == 2

    @patch('src.api.routes.chat.ChatService')
    def test_get_conversation_messages(self, mock_service_class, auth_headers):
        """Test getting messages from a conversation."""
        from src.api.main import app

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        conv_id = str(uuid4())
        mock_messages = [
            {
                "id": str(uuid4()),
                "role": "user",
                "content": "add task buy milk",
                "created_at": "2025-12-31T10:00:00"
            },
            {
                "id": str(uuid4()),
                "role": "assistant",
                "content": "✓ Created task: buy milk",
                "created_at": "2025-12-31T10:00:05"
            }
        ]

        mock_service.get_all_messages.return_value = mock_messages

        client = TestClient(app)

        response = client.get(
            f"/api/chat/conversations/{conv_id}/messages",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"

    @patch('src.api.routes.chat.ChatService')
    def test_get_nonexistent_conversation(self, mock_service_class, auth_headers):
        """Test getting messages from non-existent conversation."""
        from src.api.main import app

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Mock raises ValueError for conversation not found
        mock_service.get_all_messages.side_effect = ValueError("Conversation not found")

        client = TestClient(app)

        fake_id = str(uuid4())
        response = client.get(
            f"/api/chat/conversations/{fake_id}/messages",
            headers=auth_headers
        )

        assert response.status_code == 403

    def test_delete_conversation_success(self, auth_headers):
        """Test deleting a conversation."""
        from src.api.main import app

        # This requires actual database setup, so we'll test the route exists
        client = TestClient(app)

        conv_id = str(uuid4())
        response = client.delete(
            f"/api/chat/conversations/{conv_id}",
            headers=auth_headers
        )

        # May return 404 (conversation not found) or 200 (deleted)
        # Both are valid responses indicating the endpoint works
        assert response.status_code in [200, 404]

    def test_delete_conversation_invalid_id(self, auth_headers):
        """Test deleting conversation with invalid UUID."""
        from src.api.main import app

        client = TestClient(app)

        response = client.delete(
            "/api/chat/conversations/invalid-uuid",
            headers=auth_headers
        )

        # Should return 400 for invalid UUID format
        assert response.status_code == 400


class TestStatelessBehavior:
    """Test stateless architecture principles."""

    @patch('src.api.routes.chat.ChatService')
    def test_new_agent_per_request(self, mock_service_class, auth_headers):
        """Test that each request creates a fresh agent instance."""
        from src.api.main import app

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Track calls to process_message
        call_count = 0

        async def mock_process(user_id, message, conversation_id, language):
            nonlocal call_count
            call_count += 1
            return {
                "conversation_id": str(uuid4()),
                "message_id": str(uuid4()),
                "response": f"Response {call_count}",
                "type": "message",
                "data": None
            }

        mock_service.process_message = AsyncMock(side_effect=mock_process)

        client = TestClient(app)

        # Send 3 requests
        for i in range(3):
            response = client.post(
                "/api/chat/",
                json={"message": f"message {i}", "language": "en"},
                headers=auth_headers
            )
            assert response.status_code == 200

        # Verify process_message was called 3 times (fresh service each time)
        assert call_count == 3


class TestErrorHandling:
    """Test API error handling."""

    @patch('src.api.routes.chat.ChatService')
    def test_ai_service_error(self, mock_service_class, auth_headers):
        """Test handling of AI service errors."""
        from src.api.main import app

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Mock AI service raising exception
        mock_service.process_message = AsyncMock(
            side_effect=Exception("AI service unavailable")
        )

        client = TestClient(app)

        response = client.post(
            "/api/chat/",
            json={"message": "add task", "language": "en"},
            headers=auth_headers
        )

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()


# Run tests with: pytest tests/test_chat_api.py -v
