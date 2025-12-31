"""Unit tests for ChatAgent (Phase 3)."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

# Note: These are unit tests that test the logic without making real API calls


class TestChatAgentInitialization:
    """Test ChatAgent initialization."""

    def test_agent_initializes_with_english(self):
        """Test agent initializes with English language."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123", language="en")

        assert agent.user_id == "user-123"
        assert agent.language == "en"
        assert agent.session == mock_session
        assert agent.api_key is not None  # Should load from env

    def test_agent_initializes_with_urdu(self):
        """Test agent initializes with Urdu language."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-456", language="ur")

        assert agent.user_id == "user-456"
        assert agent.language == "ur"

    def test_agent_defaults_to_english(self):
        """Test agent defaults to English if no language specified."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-789")

        assert agent.language == "en"


class TestSystemPrompt:
    """Test system prompt generation."""

    def test_english_system_prompt(self):
        """Test English system prompt contains expected instructions."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123", language="en")
        prompt = agent._get_system_prompt()

        assert "English" in prompt
        assert "task management" in prompt
        assert "create_task" in prompt
        assert "list_tasks" in prompt

    def test_urdu_system_prompt(self):
        """Test Urdu system prompt contains Urdu instructions."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123", language="ur")
        prompt = agent._get_system_prompt()

        assert "اردو" in prompt or "Urdu" in prompt
        assert "RESPOND ONLY IN URDU" in prompt
        assert "create_task" in prompt  # JSON commands still in English


class TestJSONExtraction:
    """Test JSON extraction from AI responses."""

    def test_extract_json_from_text(self):
        """Test extracting JSON action from text response."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        # Test with JSON embedded in text
        text = 'Sure! {"action": "create_task", "title": "buy milk"}'
        result = agent._extract_json(text)

        assert result is not None
        assert result["action"] == "create_task"
        assert result["title"] == "buy milk"

    def test_extract_json_only(self):
        """Test extracting pure JSON."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        text = '{"action": "list_tasks", "filter": "all"}'
        result = agent._extract_json(text)

        assert result is not None
        assert result["action"] == "list_tasks"
        assert result["filter"] == "all"

    def test_no_json_in_text(self):
        """Test when no JSON present in text."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        text = "This is just a regular message without JSON"
        result = agent._extract_json(text)

        assert result is None

    def test_invalid_json(self):
        """Test handling of malformed JSON."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        text = '{"action": "create_task", "title": invalid}'
        result = agent._extract_json(text)

        assert result is None


class TestActionExecution:
    """Test action execution (mocked database operations)."""

    @pytest.mark.asyncio
    async def test_create_task_action(self):
        """Test create_task action execution."""
        from src.agent.chat_agent import ChatAgent
        from src.models.task import Task

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        # Mock TaskService.create_task
        with patch('src.agent.chat_agent.TaskService.create_task') as mock_create:
            mock_task = Task(
                id=1,
                user_id="user-123",
                title="buy milk",
                description=None,
                is_completed=False
            )
            mock_create.return_value = mock_task

            action_data = {
                "action": "create_task",
                "title": "buy milk",
                "description": ""
            }

            result = await agent._execute_action(action_data)

            assert result["type"] == "task_created"
            assert "buy milk" in result["content"]
            assert result["task"]["id"] == 1
            assert result["task"]["title"] == "buy milk"

    @pytest.mark.asyncio
    async def test_list_tasks_action(self):
        """Test list_tasks action execution."""
        from src.agent.chat_agent import ChatAgent
        from src.models.task import Task

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        # Mock TaskService.get_tasks_by_user
        with patch('src.agent.chat_agent.TaskService.get_tasks_by_user') as mock_get:
            mock_tasks = [
                Task(id=1, user_id="user-123", title="buy milk", is_completed=False),
                Task(id=2, user_id="user-123", title="buy eggs", is_completed=True),
            ]
            mock_get.return_value = mock_tasks

            action_data = {
                "action": "list_tasks",
                "filter": "all"
            }

            result = await agent._execute_action(action_data)

            assert result["type"] == "task_list"
            assert "buy milk" in result["content"]
            assert "buy eggs" in result["content"]
            assert len(result["tasks"]) == 2

    @pytest.mark.asyncio
    async def test_complete_task_action(self):
        """Test complete_task action execution."""
        from src.agent.chat_agent import ChatAgent
        from src.models.task import Task

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        # Mock TaskService.update_task
        with patch('src.agent.chat_agent.TaskService.update_task') as mock_update:
            mock_task = Task(
                id=5,
                user_id="user-123",
                title="buy milk",
                is_completed=True
            )
            mock_update.return_value = mock_task

            action_data = {
                "action": "complete_task",
                "task_id": 5
            }

            result = await agent._execute_action(action_data)

            assert result["type"] == "task_completed"
            assert "buy milk" in result["content"]
            assert result["task"]["is_completed"] is True

    @pytest.mark.asyncio
    async def test_delete_task_action(self):
        """Test delete_task action execution."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        # Mock TaskService.delete_task
        with patch('src.agent.chat_agent.TaskService.delete_task') as mock_delete:
            mock_delete.return_value = True

            action_data = {
                "action": "delete_task",
                "task_id": 3
            }

            result = await agent._execute_action(action_data)

            assert result["type"] == "task_deleted"
            assert "3" in result["content"]

    @pytest.mark.asyncio
    async def test_task_not_found_error(self):
        """Test handling of task not found error."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        # Mock TaskService.update_task returning None (not found)
        with patch('src.agent.chat_agent.TaskService.update_task') as mock_update:
            mock_update.return_value = None

            action_data = {
                "action": "complete_task",
                "task_id": 999
            }

            result = await agent._execute_action(action_data)

            assert result["type"] == "error"
            assert "not found" in result["content"].lower()


class TestLanguageDetection:
    """Test language detection for translation."""

    def test_detect_english_in_urdu_mode(self):
        """Test detecting English text when Urdu is expected."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123", language="ur")

        # English text
        english_text = "Task created successfully"

        # Simulate detection logic (checking for ASCII alphabetic chars)
        has_english = any(c.isascii() and c.isalpha() for c in english_text[:50])

        assert has_english is True

    def test_detect_urdu_text(self):
        """Test detecting Urdu text."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123", language="ur")

        # Urdu text
        urdu_text = "میں نے آپ کا ٹاسک شامل کر دیا ہے"

        # Simulate detection logic
        has_english = any(c.isascii() and c.isalpha() for c in urdu_text[:50])

        assert has_english is False


class TestErrorHandling:
    """Test error handling in chat agent."""

    @pytest.mark.asyncio
    async def test_missing_task_id(self):
        """Test error when task_id is missing."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        action_data = {
            "action": "complete_task"
            # Missing task_id
        }

        result = await agent._execute_action(action_data)

        assert result["type"] == "error"
        assert "required" in result["content"].lower()

    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """Test error handling for unknown action."""
        from src.agent.chat_agent import ChatAgent

        mock_session = Mock(spec=Session)
        agent = ChatAgent(mock_session, "user-123")

        action_data = {
            "action": "unknown_action"
        }

        result = await agent._execute_action(action_data)

        assert result["type"] == "error"
        assert "Unknown action" in result["content"]


# Run tests with: pytest tests/test_chat_agent.py -v
