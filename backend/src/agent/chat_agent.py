"""OpenRouter-based chat agent for task management."""

import json
import os
from typing import Any, Dict, List

import httpx
from sqlalchemy.orm import Session

from ..services.task_service import TaskService
from ..models.task import TaskCreate, TaskUpdate


class ChatAgent:
    """Chat agent using OpenRouter API."""

    def __init__(self, session: Session, user_id: str, language: str = "en"):
        """Initialize chat agent.

        Args:
            session: Database session
            user_id: User ID for task operations
            language: User's preferred language (en or ur)
        """
        self.session = session
        self.user_id = user_id
        self.language = language
        self.api_key = os.getenv("OPENAI_API_KEY")  # OpenRouter API key
        self.base_url = os.getenv(
            "OPENAI_BASE_URL", "https://openrouter.ai/api/v1"
        )
        self.model = os.getenv("AI_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

        # Debug logging
        print(f"ChatAgent initialized:")
        print(f"  Language: {self.language}")
        print(f"  API Key: {self.api_key[:20] if self.api_key else 'MISSING'}...")
        print(f"  Base URL: {self.base_url}")
        print(f"  Model: {self.model}")

    def _get_system_prompt(self) -> str:
        """Get system prompt for the AI agent."""
        if self.language == "ur":
            return """You are a helpful task management assistant. You help users manage their todo tasks.

🔴🔴🔴 MANDATORY LANGUAGE RULE 🔴🔴🔴
RESPOND ONLY IN URDU (اردو)
استعمال کریں صرف اردو زبان
NO ENGLISH TEXT ALLOWED!
🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴

Example correct response:
User: "add task buy milk"
You: "میں نے آپ کا ٹاسک 'buy milk' شامل کر دیا ہے۔"

Example WRONG response (DO NOT DO THIS):
You: "I have added your task" ❌ WRONG!

Available actions:
- Create a task: When user wants to add/create a task
- List tasks: When user wants to see/view their tasks (all, completed, or incomplete)
- Complete a task: When user wants to mark a task as done
- Uncomplete a task: When user wants to mark a task as not done (unmark/incomplete)
- Delete a task: When user wants to remove a task
- Update a task: When user wants to modify a task title or description

IMPORTANT: When listing tasks, ALWAYS include task IDs in your response so users can reference them.

When the user requests an action, respond with a JSON object:

CREATE TASK:
{{"action": "create_task", "title": "task title", "description": "optional description"}}

LIST ALL TASKS:
{{"action": "list_tasks", "filter": "all"}}

LIST COMPLETED TASKS ONLY:
{{"action": "list_tasks", "filter": "completed"}}

LIST INCOMPLETE/PENDING TASKS:
{{"action": "list_tasks", "filter": "incomplete"}}

MARK TASK AS COMPLETE:
{{"action": "complete_task", "task_id": 123}}

MARK TASK AS INCOMPLETE (UNMARK):
{{"action": "uncomplete_task", "task_id": 123}}

DELETE TASK:
{{"action": "delete_task", "task_id": 123}}

UPDATE TASK:
{{"action": "update_task", "task_id": 123, "title": "new title", "description": "new description"}}

If you're just chatting or need clarification, respond normally without JSON.
Be friendly and helpful! Always mention task IDs when listing tasks.

REMEMBER: RESPOND IN URDU (اردو) ONLY! صرف اردو میں جواب دیں!"""
        else:
            return """You are a helpful task management assistant. You help users manage their todo tasks.

LANGUAGE: English
Respond in clear, natural English.

Available actions:
- Create a task: When user wants to add/create a task
- List tasks: When user wants to see/view their tasks (all, completed, or incomplete)
- Complete a task: When user wants to mark a task as done
- Uncomplete a task: When user wants to mark a task as not done (unmark/incomplete)
- Delete a task: When user wants to remove a task
- Update a task: When user wants to modify a task title or description

IMPORTANT: When listing tasks, ALWAYS include task IDs in your response so users can reference them.

When the user requests an action, respond with a JSON object:

CREATE TASK:
{{"action": "create_task", "title": "task title", "description": "optional description"}}

LIST ALL TASKS:
{{"action": "list_tasks", "filter": "all"}}

LIST COMPLETED TASKS ONLY:
{{"action": "list_tasks", "filter": "completed"}}

LIST INCOMPLETE/PENDING TASKS:
{{"action": "list_tasks", "filter": "incomplete"}}

MARK TASK AS COMPLETE:
{{"action": "complete_task", "task_id": 123}}

MARK TASK AS INCOMPLETE (UNMARK):
{{"action": "uncomplete_task", "task_id": 123}}

DELETE TASK:
{{"action": "delete_task", "task_id": 123}}

UPDATE TASK:
{{"action": "update_task", "task_id": 123, "title": "new title", "description": "new description"}}

If you're just chatting or need clarification, respond normally without JSON.
Be friendly and helpful! Always mention task IDs when listing tasks."""

    async def _translate_to_urdu(self, english_text: str) -> str:
        """Translate English response to Urdu as fallback.

        Args:
            english_text: English text to translate

        Returns:
            Urdu translation
        """
        translation_prompt = f"""Translate this English text to natural Urdu:

English: {english_text}

Urdu (only output the translation, nothing else):"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Todo App AI Assistant",
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": translation_prompt}
            ],
            "temperature": 0.3,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                translated = result["choices"][0]["message"]["content"].strip()
                print(f"Translated to Urdu: {translated}")
                return translated
        except Exception as e:
            print(f"Translation failed: {e}")
            return english_text

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message and execute appropriate action.

        Args:
            message: User's message

        Returns:
            Response with action result
        """
        # Call OpenRouter API to understand user intent
        response = await self._call_openrouter(message)

        # Try to parse JSON action from response
        try:
            action_data = self._extract_json(response)
            if action_data and "action" in action_data:
                result = await self._execute_action(action_data)

                # Translate response to Urdu if needed
                if self.language == "ur" and "content" in result:
                    # Check if response is in English (simple heuristic)
                    if any(c.isascii() and c.isalpha() for c in result["content"][:50]):
                        print(f"Response appears to be in English, translating...")
                        result["content"] = await self._translate_to_urdu(result["content"])

                return result
        except Exception as e:
            print(f"Action parsing error: {e}")
            pass

        # No action detected, translate chat response if Urdu
        if self.language == "ur":
            # Check if response contains significant English text
            english_chars = sum(1 for c in response[:100] if c.isascii() and c.isalpha())
            if english_chars > 20:  # If more than 20 English letters
                print(f"Chat response in English, translating...")
                response = await self._translate_to_urdu(response)

        return {"type": "message", "content": response}

    async def _call_openrouter(self, message: str) -> str:
        """Call OpenRouter API.

        Args:
            message: User message

        Returns:
            AI response text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Todo App AI Assistant",
        }

        # Add language reminder to user message for Urdu
        if self.language == "ur":
            enhanced_message = f"[RESPOND IN URDU ONLY] {message}"
        else:
            enhanced_message = message

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": enhanced_message},
            ],
        }

        print(f"Calling OpenRouter API:")
        print(f"  URL: {self.base_url}/chat/completions")
        print(f"  Model: {self.model}")
        print(f"  API Key present: {bool(self.api_key)}")
        print(f"  Headers: {list(headers.keys())}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=data
                )
                print(f"  Response status: {response.status_code}")
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                # Log the error response for debugging
                error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
                print(f"OpenRouter API Error: {e.response.status_code}")
                print(f"Error detail: {error_detail}")
                raise Exception(f"OpenRouter API error: {e.response.status_code}")

    def _extract_json(self, text: str) -> Dict[str, Any] | None:
        """Extract JSON object from text.

        Args:
            text: Text that may contain JSON

        Returns:
            Parsed JSON object or None
        """
        # Try to find JSON in the text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            json_str = text[start : end + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        return None

    async def _execute_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task action.

        Args:
            action_data: Action data with action type and parameters

        Returns:
            Action result
        """
        action = action_data.get("action")

        try:
            if action == "create_task":
                title = action_data.get("title", "")
                description = action_data.get("description", "")
                task_data = TaskCreate(
                    title=title,
                    description=description or None,
                    is_completed=False
                )
                task = TaskService.create_task(
                    self.session, task_data, self.user_id
                )
                return {
                    "type": "task_created",
                    "content": f"✓ Created task: {task.title}",
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "is_completed": task.is_completed,
                    },
                }

            elif action == "list_tasks":
                # Get all tasks from database
                all_tasks = TaskService.get_tasks_by_user(self.session, self.user_id)

                # Apply filter
                task_filter = action_data.get("filter", "all").lower()
                if task_filter == "completed":
                    tasks = [t for t in all_tasks if t.is_completed]
                    filter_label = "completed"
                elif task_filter == "incomplete":
                    tasks = [t for t in all_tasks if not t.is_completed]
                    filter_label = "incomplete/pending"
                else:
                    tasks = all_tasks
                    filter_label = "all"

                if not tasks:
                    return {
                        "type": "message",
                        "content": f"You have no {filter_label} tasks."
                    }

                task_list = "\n".join(
                    [
                        f"{i+1}. [{('✓' if t.is_completed else ' ')}] {t.title} (ID: {t.id})"
                        for i, t in enumerate(tasks)
                    ]
                )
                return {
                    "type": "task_list",
                    "content": f"Your {filter_label} tasks:\n{task_list}",
                    "tasks": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "description": t.description,
                            "is_completed": t.is_completed,
                        }
                        for t in tasks
                    ],
                }

            elif action == "complete_task":
                task_id = action_data.get("task_id")
                if not task_id:
                    return {"type": "error", "content": "Task ID is required."}

                task_data = TaskUpdate(is_completed=True)
                task = TaskService.update_task(
                    self.session, task_id, self.user_id, task_data
                )
                if not task:
                    return {"type": "error", "content": f"Task {task_id} not found."}

                return {
                    "type": "task_completed",
                    "content": f"✓ Completed task: {task.title}",
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "is_completed": task.is_completed,
                    },
                }

            elif action == "uncomplete_task":
                task_id = action_data.get("task_id")
                if not task_id:
                    return {"type": "error", "content": "Task ID is required."}

                task_data = TaskUpdate(is_completed=False)
                task = TaskService.update_task(
                    self.session, task_id, self.user_id, task_data
                )
                if not task:
                    return {"type": "error", "content": f"Task {task_id} not found."}

                return {
                    "type": "task_uncompleted",
                    "content": f"✓ Marked task as incomplete: {task.title}",
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "is_completed": task.is_completed,
                    },
                }

            elif action == "delete_task":
                task_id = action_data.get("task_id")
                if not task_id:
                    return {"type": "error", "content": "Task ID is required."}

                success = TaskService.delete_task(self.session, task_id, self.user_id)
                if not success:
                    return {"type": "error", "content": f"Task {task_id} not found."}

                return {
                    "type": "task_deleted",
                    "content": f"✓ Deleted task ID {task_id}",
                }

            elif action == "update_task":
                task_id = action_data.get("task_id")
                if not task_id:
                    return {"type": "error", "content": "Task ID is required."}

                title = action_data.get("title")
                description = action_data.get("description")
                task_data = TaskUpdate(title=title, description=description)
                task = TaskService.update_task(
                    self.session, task_id, self.user_id, task_data
                )
                if not task:
                    return {"type": "error", "content": f"Task {task_id} not found."}

                return {
                    "type": "task_updated",
                    "content": f"✓ Updated task: {task.title}",
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                    },
                }

            else:
                return {"type": "error", "content": f"Unknown action: {action}"}

        except ValueError as e:
            return {"type": "error", "content": str(e)}
        except Exception as e:
            return {"type": "error", "content": f"Error: {str(e)}"}


def create_chat_agent(session: Session, user_id: str, language: str = "en") -> ChatAgent:
    """Factory function to create a chat agent.

    Args:
        session: Database session
        user_id: User ID
        language: User's preferred language (en or ur)

    Returns:
        ChatAgent instance
    """
    return ChatAgent(session, user_id, language)
