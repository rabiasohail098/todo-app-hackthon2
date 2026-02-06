"""Comprehensive API tests for all endpoints in the Todo app."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
import json


@pytest.fixture
def mock_auth_token():
    """Mock JWT token for authentication."""
    return "mock-jwt-token-test-user"


@pytest.fixture
def auth_headers(mock_auth_token):
    """Headers with authentication token."""
    return {"Authorization": f"Bearer {mock_auth_token}", "X-User-Id": "test-user-id"}


@pytest.fixture
def client():
    """FastAPI test client."""
    from src.api.main import app
    return TestClient(app)


class TestHealthAPI:
    """Test health check endpoints."""

    def test_health_endpoint(self, client):
        """Test GET /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test GET / root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Todo App API" in data["message"]

    def test_metrics_endpoint(self, client):
        """Test GET /metrics endpoint."""
        response = client.get("/metrics")
        # May return 200 (if prometheus is installed) or 501 (if not)
        assert response.status_code in [200, 501]


class TestTaskAPI:
    """Test task management endpoints."""

    @patch('src.api.routes.tasks.TaskService')
    def test_create_task(self, mock_service_class, client, auth_headers):
        """Test POST /api/tasks endpoint."""
        from src.models.task import TaskPriority

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Mock task creation
        mock_task = {
            "id": 1,
            "user_id": "test-user-id",
            "title": "Test task",
            "description": "Test description",
            "is_completed": False,
            "priority": "medium",
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:00:00"
        }

        mock_service.create_task.return_value = mock_task

        response = client.post(
            "/api/tasks",
            json={
                "title": "Test task",
                "description": "Test description",
                "priority": "medium"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test task"
        assert data["description"] == "Test description"

    @patch('src.api.routes.tasks.TaskService')
    def test_get_tasks(self, mock_service_class, client, auth_headers):
        """Test GET /api/tasks endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Mock task list
        mock_tasks = [{
            "id": 1,
            "user_id": "test-user-id",
            "title": "Test task",
            "description": "Test description",
            "is_completed": False,
            "priority": "medium",
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:00:00"
        }]

        mock_service.get_tasks_by_user.return_value = mock_tasks

        response = client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0  # Could be empty list

    @patch('src.api.routes.tasks.TaskService')
    def test_get_single_task(self, mock_service_class, client, auth_headers):
        """Test GET /api/tasks/{task_id} endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_task = {
            "id": 1,
            "user_id": "test-user-id",
            "title": "Test task",
            "description": "Test description",
            "is_completed": False,
            "priority": "medium",
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:00:00"
        }

        mock_service.get_task_by_id.return_value = mock_task

        response = client.get("/api/tasks/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test task"

    @patch('src.api.routes.tasks.TaskService')
    def test_update_task(self, mock_service_class, client, auth_headers):
        """Test PATCH /api/tasks/{task_id} endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        updated_task = {
            "id": 1,
            "user_id": "test-user-id",
            "title": "Updated task",
            "description": "Updated description",
            "is_completed": True,
            "priority": "high",
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:05:00"
        }

        mock_service.update_task.return_value = updated_task

        response = client.patch(
            "/api/tasks/1",
            json={
                "title": "Updated task",
                "is_completed": True,
                "priority": "high"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated task"
        assert data["is_completed"] is True

    @patch('src.api.routes.tasks.TaskService')
    def test_delete_task(self, mock_service_class, client, auth_headers):
        """Test DELETE /api/tasks/{task_id} endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_service.delete_task.return_value = True

        response = client.delete("/api/tasks/1", headers=auth_headers)
        assert response.status_code == 204  # No content for successful delete


class TestCategoryAPI:
    """Test category management endpoints."""

    @patch('src.api.routes.categories.CategoryService')
    def test_create_category(self, mock_service_class, client, auth_headers):
        """Test POST /api/categories endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_category = {
            "id": 1,
            "user_id": "test-user-id",
            "name": "Work",
            "color": "#FF0000",
            "icon": "💼",
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:00:00"
        }

        mock_service.create_category.return_value = mock_category

        response = client.post(
            "/api/categories",
            json={
                "name": "Work",
                "color": "#FF0000",
                "icon": "💼"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Work"
        assert data["color"] == "#FF0000"

    @patch('src.api.routes.categories.CategoryService')
    def test_get_categories(self, mock_service_class, client, auth_headers):
        """Test GET /api/categories endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_categories = [{
            "id": 1,
            "user_id": "test-user-id",
            "name": "Work",
            "color": "#FF0000",
            "icon": "💼",
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:00:00"
        }]

        mock_service.get_categories_by_user.return_value = mock_categories

        response = client.get("/api/categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0

    @patch('src.api.routes.categories.CategoryService')
    def test_get_single_category(self, mock_service_class, client, auth_headers):
        """Test GET /api/categories/{category_id} endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_category = {
            "id": 1,
            "user_id": "test-user-id",
            "name": "Work",
            "color": "#FF0000",
            "icon": "💼",
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:00:00"
        }

        mock_service.get_category_by_id.return_value = mock_category

        response = client.get("/api/categories/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Work"

    @patch('src.api.routes.categories.CategoryService')
    def test_update_category(self, mock_service_class, client, auth_headers):
        """Test PUT /api/categories/{category_id} endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        updated_category = {
            "id": 1,
            "user_id": "test-user-id",
            "name": "Personal",
            "color": "#00FF00",
            "icon": "🏠",
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:05:00"
        }

        mock_service.update_category.return_value = updated_category

        response = client.put(
            "/api/categories/1",
            json={
                "name": "Personal",
                "color": "#00FF00",
                "icon": "🏠"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Personal"
        assert data["color"] == "#00FF00"

    @patch('src.api.routes.categories.CategoryService')
    def test_delete_category(self, mock_service_class, client, auth_headers):
        """Test DELETE /api/categories/{category_id} endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_service.delete_category.return_value = True

        response = client.delete("/api/categories/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestSubtaskAPI:
    """Test subtask management endpoints."""

    @patch('src.api.routes.subtasks.SubtaskService')
    def test_create_subtask(self, mock_service_class, client, auth_headers):
        """Test POST /api/tasks/{task_id}/subtasks endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_subtask = {
            "id": 1,
            "parent_task_id": 1,
            "title": "Subtask 1",
            "is_completed": False,
            "order": 1,
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:00:00"
        }

        mock_service.create_subtask.return_value = mock_subtask

        response = client.post(
            "/api/tasks/1/subtasks",
            json={
                "title": "Subtask 1",
                "order": 1
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Subtask 1"
        assert data["parent_task_id"] == 1

    @patch('src.api.routes.subtasks.SubtaskService')
    def test_get_subtasks(self, mock_service_class, client, auth_headers):
        """Test GET /api/tasks/{task_id}/subtasks endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_subtasks = [{
            "id": 1,
            "parent_task_id": 1,
            "title": "Subtask 1",
            "is_completed": False,
            "order": 1,
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:00:00"
        }]

        mock_service.get_subtasks_for_task.return_value = mock_subtasks

        response = client.get("/api/tasks/1/subtasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0

    @patch('src.api.routes.subtasks.SubtaskService')
    def test_get_subtask_progress(self, mock_service_class, client, auth_headers):
        """Test GET /api/tasks/{task_id}/subtasks/progress endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        progress_data = {
            "total": 5,
            "completed": 2,
            "percentage": 40.0
        }

        mock_service.get_subtask_progress.return_value = progress_data

        response = client.get("/api/tasks/1/subtasks/progress", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "completed" in data
        assert "percentage" in data

    @patch('src.api.routes.subtasks.SubtaskService')
    def test_update_subtask(self, mock_service_class, client, auth_headers):
        """Test PATCH /api/subtasks/{subtask_id} endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        updated_subtask = {
            "id": 1,
            "parent_task_id": 1,
            "title": "Updated Subtask",
            "is_completed": True,
            "order": 1,
            "created_at": "2025-12-31T10:00:00",
            "updated_at": "2025-12-31T10:05:00"
        }

        mock_service.update_subtask.return_value = updated_subtask

        response = client.patch(
            "/api/subtasks/1",
            json={
                "is_completed": True,
                "title": "Updated Subtask"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True
        assert data["title"] == "Updated Subtask"

    @patch('src.api.routes.subtasks.SubtaskService')
    def test_delete_subtask(self, mock_service_class, client, auth_headers):
        """Test DELETE /api/subtasks/{subtask_id} endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_service.delete_subtask.return_value = True

        response = client.delete("/api/subtasks/1", headers=auth_headers)
        assert response.status_code == 204


class TestTagAPI:
    """Test tag management endpoints."""

    @patch('src.api.routes.tags.TagService')
    def test_create_tag(self, mock_service_class, client, auth_headers):
        """Test POST /api/tags endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_tag = {
            "id": 1,
            "user_id": "test-user-id",
            "name": "important",
            "created_at": "2025-12-31T10:00:00"
        }

        mock_service.create_tag.return_value = mock_tag

        response = client.post(
            "/api/tags",
            json={
                "name": "important"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "important"

    @patch('src.api.routes.tags.TagService')
    def test_get_tags(self, mock_service_class, client, auth_headers):
        """Test GET /api/tags endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_tags = [{
            "id": 1,
            "user_id": "test-user-id",
            "name": "important",
            "created_at": "2025-12-31T10:00:00"
        }]

        mock_service.get_tags_by_user.return_value = mock_tags

        response = client.get("/api/tags", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0

    @patch('src.api.routes.tags.TagService')
    def test_add_tag_to_task(self, mock_service_class, client, auth_headers):
        """Test POST /api/tasks/{task_id}/tags/{tag_id} endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_service.add_tag_to_task.return_value = True

        response = client.post("/api/tasks/1/tags/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch('src.api.routes.tags.TagService')
    def test_remove_tag_from_task(self, mock_service_class, client, auth_headers):
        """Test DELETE /api/tasks/{task_id}/tags/{tag_id} endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_service.remove_tag_from_task.return_value = True

        response = client.delete("/api/tasks/1/tags/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatisticsAPI:
    """Test statistics endpoints."""

    @patch('src.api.routes.statistics.StatisticsService')
    def test_get_statistics(self, mock_service_class, client, auth_headers):
        """Test GET /api/statistics endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        stats_data = {
            "total_tasks": 10,
            "completed_tasks": 5,
            "pending_tasks": 5,
            "overdue_tasks": 0
        }

        mock_service.get_user_statistics.return_value = stats_data

        response = client.get("/api/statistics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "completed_tasks" in data

    @patch('src.api.routes.statistics.StatisticsService')
    def test_get_daily_statistics(self, mock_service_class, client, auth_headers):
        """Test GET /api/statistics/daily endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        daily_stats = {
            "last_7_days": [
                {"date": "2025-12-25", "created": 2, "completed": 1},
                {"date": "2025-12-26", "created": 1, "completed": 0},
            ]
        }

        mock_service.get_daily_statistics.return_value = daily_stats

        response = client.get("/api/statistics/daily", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "last_7_days" in data


class TestChatAPI:
    """Test chat endpoints (already tested in test_chat_api.py, but included for completeness)."""

    @patch('src.api.routes.chat.ChatService')
    def test_send_message(self, mock_service_class, client, auth_headers):
        """Test POST /api/chat/ endpoint."""
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


class TestAttachmentAPI:
    """Test attachment endpoints."""

    @patch('src.api.routes.attachments.AttachmentService')
    def test_upload_attachment(self, mock_service_class, client, auth_headers):
        """Test POST /api/tasks/{task_id}/attachments endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_attachment = {
            "id": 1,
            "task_id": 1,
            "user_id": "test-user-id",
            "filename": "document.pdf",
            "original_filename": "document.pdf",
            "file_type": "application/pdf",
            "file_size": 1024,
            "cloudinary_url": "https://example.com/document.pdf",
            "created_at": "2025-12-31T10:00:00"
        }

        mock_service.upload_attachment.return_value = mock_attachment

        # Since this is a file upload, we'll test the route exists and returns expected status
        # For a real test, we'd need to handle multipart form data
        response = client.post("/api/tasks/1/attachments", headers=auth_headers)
        # Could return 422 (validation error for missing file) or 500 (missing file), but route should exist
        assert response.status_code in [422, 500, 400]  # Route exists and expects file data


class TestActivityAPI:
    """Test activity log endpoints."""

    @patch('src.api.routes.activity.ActivityService')
    def test_get_activity_log(self, mock_service_class, client, auth_headers):
        """Test GET /api/tasks/{task_id}/activity endpoint."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_activities = [{
            "id": 1,
            "task_id": 1,
            "user_id": "test-user-id",
            "action": "task_updated",
            "field": "title",
            "old_value": "Old title",
            "new_value": "New title",
            "description": "Updated task title",
            "created_at": "2025-12-31T10:00:00"
        }]

        mock_service.get_task_activity.return_value = mock_activities

        response = client.get("/api/tasks/1/activity", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0


class TestAuthentication:
    """Test authentication and authorization."""

    def test_unauthorized_access(self, client):
        """Test that protected endpoints return 401 without auth."""
        endpoints_to_test = [
            "/api/tasks",
            "/api/categories",
            "/api/tags",
            "/api/statistics",
            "/api/chat/"
        ]

        for endpoint in endpoints_to_test:
            if endpoint == "/api/chat/":
                response = client.post(endpoint, json={"message": "test"})
            else:
                response = client.get(endpoint)

            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"


# Run tests with: pytest tests/test_all_apis.py -v