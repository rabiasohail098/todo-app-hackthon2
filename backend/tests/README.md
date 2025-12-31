# Backend Tests - Phase 3 AI Chatbot

## Test Files

- `test_chat_agent.py` - Unit tests for ChatAgent class
- `test_chat_api.py` - Integration tests for Chat API endpoints

## Running Tests

### Install Test Dependencies

```bash
cd backend
pip install pytest pytest-asyncio pytest-cov
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
# Chat agent unit tests
pytest tests/test_chat_agent.py -v

# Chat API integration tests
pytest tests/test_chat_api.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

Open `htmlcov/index.html` to view coverage report.

### Run Specific Test

```bash
# Run single test
pytest tests/test_chat_agent.py::TestChatAgentInitialization::test_agent_initializes_with_english -v

# Run test class
pytest tests/test_chat_agent.py::TestSystemPrompt -v
```

## Test Categories

### Unit Tests (`test_chat_agent.py`)

**TestChatAgentInitialization**:
- Agent initializes with English
- Agent initializes with Urdu
- Defaults to English

**TestSystemPrompt**:
- English system prompt format
- Urdu system prompt format

**TestJSONExtraction**:
- Extract JSON from mixed text
- Extract pure JSON
- Handle missing JSON
- Handle invalid JSON

**TestActionExecution**:
- Create task action
- List tasks action
- Complete task action
- Delete task action
- Update task action
- Task not found error

**TestLanguageDetection**:
- Detect English in Urdu mode
- Detect Urdu text

**TestErrorHandling**:
- Missing task ID
- Unknown action

### Integration Tests (`test_chat_api.py`)

**TestChatEndpoint**:
- Send message successfully
- Send message in Urdu
- Unauthorized access
- Send to existing conversation
- Empty message validation
- Invalid language validation

**TestConversationEndpoints**:
- Get user conversations
- Get conversation messages
- Get non-existent conversation
- Delete conversation
- Invalid conversation ID

**TestStatelessBehavior**:
- New agent per request

**TestErrorHandling**:
- AI service error handling

## Test Coverage Goals

- **Unit Tests**: 80%+ coverage of `chat_agent.py`
- **Integration Tests**: 70%+ coverage of `routes/chat.py`

## Mocking Strategy

Tests use mocks to avoid:
- Real database operations
- Real OpenRouter API calls
- Real authentication checks

This ensures tests run quickly and don't require:
- Database connection
- API keys
- Network access

## CI/CD Integration

Add to GitHub Actions:

```yaml
- name: Run tests
  run: |
    cd backend
    pytest tests/ -v --cov=src
```

## Notes

- Tests are **safe** - they don't modify working code
- All tests use **mocks** - no real API calls
- Tests verify **logic only** - not actual AI responses
- **Fast execution** - ~1-2 seconds for all tests

---

**Version**: 1.0.0 | **Created**: 2025-12-31
