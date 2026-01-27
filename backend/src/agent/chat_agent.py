"""OpenRouter-based chat agent for task management."""

import json
import os
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from ..services.task_service import TaskService
from ..services.category_service import CategoryService
from ..models.task import TaskCreate, TaskUpdate

if TYPE_CHECKING:
    from ..models.conversation import Conversation


# Conversation states for guided task creation
class ConversationState:
    """Track multi-step conversation state for task creation."""

    IDLE = "idle"
    AWAITING_TITLE = "awaiting_title"
    AWAITING_DESCRIPTION = "awaiting_description"
    AWAITING_CATEGORY = "awaiting_category"
    AWAITING_PRIORITY = "awaiting_priority"
    AWAITING_DUE_DATE = "awaiting_due_date"
    AWAITING_RECURRENCE = "awaiting_recurrence"
    AWAITING_TAGS = "awaiting_tags"
    AWAITING_CONFIRMATION = "awaiting_confirmation"


class ChatAgent:
    """Chat agent using OpenRouter API."""

    def __init__(self, session: Session, user_id: str, language: str = "en", conversation: "Conversation" = None):
        """Initialize chat agent.

        Args:
            session: Database session
            user_id: User ID for task operations
            language: User's preferred language (en or ur)
            conversation: Conversation object for state persistence
        """
        self.session = session
        self.user_id = user_id
        self.language = language
        self.conversation = conversation  # Store conversation for state persistence
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
        print(f"  Conversation State: {self._get_state()}")

    def _get_state(self) -> str:
        """Get current conversation state from database."""
        if self.conversation and self.conversation.guided_state:
            return self.conversation.guided_state
        return ConversationState.IDLE

    def _set_state(self, state: str):
        """Set conversation state in database."""
        if self.conversation:
            self.conversation.guided_state = state
            print(f"State set to: {state}")

    def _get_pending_task(self) -> Dict[str, Any]:
        """Get pending task data from database."""
        if self.conversation:
            return self.conversation.get_pending_task()
        return {}

    def _update_pending_task(self, **kwargs):
        """Update pending task with new field values in database."""
        if self.conversation:
            pending = self.conversation.get_pending_task()
            pending.update(kwargs)
            self.conversation.set_pending_task(pending)
            print(f"Pending task updated: {pending}")

    def _clear_pending_task(self):
        """Clear pending task and reset state in database."""
        if self.conversation:
            self.conversation.guided_state = ConversationState.IDLE
            self.conversation.set_pending_task({})
            print("Pending task cleared")

    def _get_available_categories(self) -> List[Dict[str, Any]]:
        """Get available categories for task creation."""
        try:
            category_service = CategoryService(self.session)
            categories = category_service.get_categories_by_user(self.user_id)
            return [{"id": c.id, "name": c.name, "icon": c.icon} for c in categories]
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []

    def _format_category_options(self) -> str:
        """Format category options for display."""
        categories = self._get_available_categories()
        # Store categories in pending task for later reference
        self._update_pending_task(_available_categories=categories)

        if not categories:
            if self.language == "ur":
                return "کوئی کیٹیگری دستیاب نہیں۔ آپ ایک نئی کیٹیگری کا نام لکھ سکتے ہیں یا 'skip' کہیں۔"
            return "No categories available. You can type a new category name or say 'skip'."

        options = []
        for i, cat in enumerate(categories, 1):
            options.append(f"{i}. {cat.get('icon', '📁')} {cat['name']}")

        if self.language == "ur":
            return "کیٹیگری منتخب کریں:\n" + "\n".join(options) + "\n\n(نمبر لکھیں، نام لکھیں، نئی کیٹیگری کا نام لکھیں، یا 'skip' کہیں)"
        return "Select a category:\n" + "\n".join(options) + "\n\n(Enter number, name, type a new category, or say 'skip')"

    def _format_priority_options(self) -> str:
        """Format priority options for display."""
        if self.language == "ur":
            return """ترجیح منتخب کریں:
1. 🔴 Critical (فوری)
2. 🟠 High (اہم)
3. 🟡 Medium (درمیانہ) - پہلے سے منتخب
4. 🟢 Low (کم)

(نمبر یا نام لکھیں، یا 'skip' کہیں)"""
        return """Select priority:
1. 🔴 Critical
2. 🟠 High
3. 🟡 Medium (default)
4. 🟢 Low

(Enter number, name, or say 'skip')"""

    def _format_recurrence_options(self) -> str:
        """Format recurrence options for display."""
        if self.language == "ur":
            return """دہرائی کا پیٹرن منتخب کریں:
1. 📅 Daily (روزانہ)
2. 📆 Weekly (ہفتہ وار)
3. 🗓️ Monthly (ماہانہ)

(نمبر یا نام لکھیں، یا 'skip' کہیں - یہ ایک بار کا کام ہوگا)"""
        return """Select recurrence pattern:
1. 📅 Daily
2. 📆 Weekly
3. 🗓️ Monthly

(Enter number, name, or say 'skip' for one-time task)"""

    def _parse_user_response(self, message: str, field: str) -> Dict[str, Any]:
        """Parse user response for a specific field."""
        msg_lower = message.lower().strip()

        # Check for skip
        if msg_lower in ["skip", "چھوڑیں", "نہیں", "no", "none", "-"]:
            return {"skip": True}

        if field == "priority":
            priority_map = {
                "1": "critical", "critical": "critical", "فوری": "critical",
                "2": "high", "high": "high", "اہم": "high",
                "3": "medium", "medium": "medium", "درمیانہ": "medium",
                "4": "low", "low": "low", "کم": "low"
            }
            return {"value": priority_map.get(msg_lower, "medium")}

        elif field == "recurrence":
            recurrence_map = {
                "1": "daily", "daily": "daily", "روزانہ": "daily",
                "2": "weekly", "weekly": "weekly", "ہفتہ وار": "weekly",
                "3": "monthly", "monthly": "monthly", "ماہانہ": "monthly"
            }
            return {"value": recurrence_map.get(msg_lower)}

        elif field == "category":
            pending = self._get_pending_task()
            categories = pending.get("_available_categories", [])
            # Try to match by number
            if msg_lower.isdigit():
                idx = int(msg_lower) - 1
                if 0 <= idx < len(categories):
                    return {"value": categories[idx]["id"], "name": categories[idx]["name"]}
            # Try to match by name
            for cat in categories:
                if cat["name"].lower() == msg_lower:
                    return {"value": cat["id"], "name": cat["name"]}
            # New category name
            return {"new_category": message.strip()}

        elif field == "due_date":
            # Parse date input
            from ..utils.date_parser import parse_natural_date
            from datetime import timedelta

            # Quick options
            if msg_lower in ["tomorrow", "کل"]:
                tomorrow = datetime.now() + timedelta(days=1)
                return {"value": tomorrow}
            elif msg_lower in ["next week", "اگلا ہفتہ", "اگلے ہفتے"]:
                next_week = datetime.now() + timedelta(days=7)
                return {"value": next_week}

            # Try parsing as date
            try:
                parsed = parse_natural_date(message)
                if parsed:
                    return {"value": parsed}
                # Try ISO format
                parsed = datetime.fromisoformat(message.replace('Z', '+00:00'))
                return {"value": parsed}
            except:
                pass

            return {"value": None, "error": True}

        elif field == "tags":
            # Parse hashtags or comma-separated tags
            tags = []
            if "#" in message:
                # Extract hashtags
                import re
                tags = re.findall(r'#(\w+)', message)
            else:
                # Comma or space separated
                tags = [t.strip() for t in message.replace(",", " ").split() if t.strip()]
            return {"value": tags}

        return {"value": message.strip()}

    def _get_system_prompt(self) -> str:
        """Get system prompt for the AI agent."""
        if self.language == "ur":
            return """You are a helpful task management assistant. You help users manage their todo tasks.

🔴🔴🔴 MANDATORY LANGUAGE RULE 🔴🔴🔴
RESPOND ONLY IN URDU (اردو)
استعمال کریں صرف اردو زبان
NO ENGLISH TEXT ALLOWED!
🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴

Available actions:
- Create a task (GUIDED): When user wants to add/create a task - START GUIDED FLOW
- List tasks: When user wants to see/view their tasks
- Search tasks: When user wants to find/search for specific tasks
- Add subtask: When user wants to add a subtask/checklist item
- Complete/Uncomplete tasks and subtasks
- Delete a task or subtask
- Update a task

IMPORTANT: When listing tasks, ALWAYS include task IDs in your response.

🚀 GUIDED TASK CREATION MODE:
When user wants to create/add a task, ALWAYS start the guided flow:
- User says: "add task", "ٹاسک شامل کریں", "نیا ٹاسک", etc.
- Response: {{"action": "start_guided_task"}}

This will trigger a step-by-step wizard asking about:
1. Task title (ٹاسک کا عنوان) - required
2. Description (تفصیل) - optional
3. Category (کیٹیگری) - optional
4. Priority (ترجیح) - optional
5. Due date (آخری تاریخ) - optional
6. Recurrence (دہرائی) - optional
7. Tags (ٹیگز) - optional

Examples triggering guided flow:
- "add task" → {{"action": "start_guided_task"}}
- "ٹاسک شامل کریں" → {{"action": "start_guided_task"}}
- "نیا کام" → {{"action": "start_guided_task"}}
- "add task buy milk" → {{"action": "start_guided_task", "initial_title": "buy milk"}}

LIST ALL TASKS:
{{"action": "list_tasks", "filter": "all"}}

LIST COMPLETED TASKS ONLY:
{{"action": "list_tasks", "filter": "completed"}}

LIST INCOMPLETE/PENDING TASKS:
{{"action": "list_tasks", "filter": "incomplete"}}

SEARCH TASKS:
{{"action": "search_tasks", "query": "search keywords"}}

MARK TASK AS COMPLETE:
{{"action": "complete_task", "task_id": 123}}

MARK TASK AS INCOMPLETE (UNMARK):
{{"action": "uncomplete_task", "task_id": 123}}

DELETE TASK:
{{"action": "delete_task", "task_id": 123}}

UPDATE TASK:
{{"action": "update_task", "task_id": 123, "title": "new title", "description": "new description"}}

ADD SUBTASK TO TASK:
{{"action": "add_subtask", "task_id": 123, "subtask_title": "subtask description"}}

COMPLETE SUBTASK:
{{"action": "complete_subtask", "subtask_id": 456}}

DELETE SUBTASK:
{{"action": "delete_subtask", "subtask_id": 456}}

If you're just chatting or need clarification, respond normally without JSON.
Be friendly and helpful! Always mention task IDs when listing tasks.

REMEMBER: RESPOND IN URDU (اردو) ONLY! صرف اردو میں جواب دیں!"""
        else:
            return """You are a helpful task management assistant. You help users manage their todo tasks.

LANGUAGE: English
Respond in clear, natural English.

Available actions:
- Create a task (GUIDED): When user wants to add/create a task - START GUIDED FLOW to collect all details
- List tasks: When user wants to see/view their tasks (all, completed, or incomplete)
- Search tasks: When user wants to find/search for specific tasks by keyword
- Add subtask: When user wants to add a subtask/checklist item to a task
- Complete subtask: When user wants to mark a subtask as done
- Delete subtask: When user wants to remove a subtask
- Complete a task: When user wants to mark a task as done
- Uncomplete a task: When user wants to mark a task as not done (unmark/incomplete)
- Delete a task: When user wants to remove a task
- Update a task: When user wants to modify a task title or description

IMPORTANT: When listing tasks, ALWAYS include task IDs in your response so users can reference them.

🚀 GUIDED TASK CREATION MODE (NEW!):
When user wants to create/add a task, ALWAYS start the guided flow:
- User says: "add task", "create task", "new task", "add a task", etc.
- Response: {{"action": "start_guided_task"}}

This will trigger a step-by-step wizard asking about:
1. Task title (required)
2. Description (optional)
3. Category (optional)
4. Priority (optional)
5. Due date (optional)
6. Recurrence (optional)
7. Tags (optional)

Examples triggering guided flow:
- "add task" → {{"action": "start_guided_task"}}
- "create a new task" → {{"action": "start_guided_task"}}
- "I want to add a task" → {{"action": "start_guided_task"}}
- "new task please" → {{"action": "start_guided_task"}}
- "add task buy milk" → {{"action": "start_guided_task", "initial_title": "buy milk"}}

LIST ALL TASKS:
{{"action": "list_tasks", "filter": "all"}}

LIST COMPLETED TASKS ONLY:
{{"action": "list_tasks", "filter": "completed"}}

LIST INCOMPLETE/PENDING TASKS:
{{"action": "list_tasks", "filter": "incomplete"}}

SEARCH TASKS:
{{"action": "search_tasks", "query": "search keywords"}}

Examples:
- "Find all tasks about shopping" → {{"action": "search_tasks", "query": "shopping"}}
- "Search for work tasks" → {{"action": "search_tasks", "query": "work"}}
- "Show me tasks with meeting" → {{"action": "search_tasks", "query": "meeting"}}

MARK TASK AS COMPLETE:
{{"action": "complete_task", "task_id": 123}}

MARK TASK AS INCOMPLETE (UNMARK):
{{"action": "uncomplete_task", "task_id": 123}}

DELETE TASK:
{{"action": "delete_task", "task_id": 123}}

UPDATE TASK:
{{"action": "update_task", "task_id": 123, "title": "new title", "description": "new description"}}

ADD SUBTASK TO TASK:
{{"action": "add_subtask", "task_id": 123, "subtask_title": "subtask description"}}

Examples:
- "Add checklist item 'review slides' to task 5" → {{"action": "add_subtask", "task_id": 5, "subtask_title": "review slides"}}
- "Break down task 10 with step 'gather materials'" → {{"action": "add_subtask", "task_id": 10, "subtask_title": "gather materials"}}

COMPLETE SUBTASK:
{{"action": "complete_subtask", "subtask_id": 456}}

DELETE SUBTASK:
{{"action": "delete_subtask", "subtask_id": 456}}

If you're just chatting or need clarification, respond normally without JSON.
Be friendly and helpful! Always mention task IDs when listing tasks."""

    async def _generate_description(self, title: str) -> str:
        """Generate a task description based on the title using AI.

        Args:
            title: Task title

        Returns:
            Generated description
        """
        if self.language == "ur":
            prompt = f"یہ ٹاسک کے عنوان کے لیے ایک مختصر تفصیل لکھیں (صرف 1-2 جملے، صرف اردو میں):\n\nعنوان: {title}\n\nتفصیل:"
        else:
            prompt = f"Write a brief description for this task title (1-2 sentences only, no extra text):\n\nTitle: {title}\n\nDescription:"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Todo App AI Assistant",
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 100,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                description = result["choices"][0]["message"]["content"].strip()
                # Clean up any prefixes like "Description:" that AI might add
                description = description.replace("Description:", "").replace("تفصیل:", "").strip()
                print(f"Generated description: {description}")
                return description
        except Exception as e:
            print(f"Description generation failed: {e}")
            # Fallback to a simple description
            if self.language == "ur":
                return f"'{title}' کا کام مکمل کریں"
            return f"Complete the task: {title}"

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

    def _detect_direct_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect common intents directly without calling AI.

        This provides reliable first-attempt behavior for common commands.

        Args:
            message: User's message

        Returns:
            Action dict if intent detected, None otherwise
        """
        import re
        msg_lower = message.lower().strip()

        # ===================
        # TASK CREATION
        # ===================
        # Patterns: "add task X", "create task X", "new task X", "task add X"
        add_task_patterns = [
            r'^(?:add|create|new|make)\s+(?:a\s+)?task\s*[:\-]?\s*["\']?(.+?)["\']?$',
            r'^task\s+(?:add|create|new)\s*[:\-]?\s*["\']?(.+?)["\']?$',
            r'^(?:ٹاسک|کام)\s+(?:شامل|بنائیں|نیا)\s*[:\-]?\s*["\']?(.+?)["\']?$',
            r'^(?:شامل|بنائیں)\s+(?:ٹاسک|کام)\s*[:\-]?\s*["\']?(.+?)["\']?$',
        ]

        for pattern in add_task_patterns:
            match = re.match(pattern, msg_lower, re.IGNORECASE)
            if match:
                title = match.group(1).strip().strip('"\'')
                if title:
                    return {"action": "start_guided_task", "initial_title": title}

        # Simple patterns without title
        simple_add_patterns = [
            r'^(?:add|create|new|make)\s+(?:a\s+)?task\s*$',
            r'^(?:ٹاسک|کام)\s+(?:شامل|بنائیں)\s*$',
            r'^(?:نیا|نئی)\s+(?:ٹاسک|کام)\s*$',
        ]

        for pattern in simple_add_patterns:
            if re.match(pattern, msg_lower, re.IGNORECASE):
                return {"action": "start_guided_task"}

        # ===================
        # LIST TASKS
        # ===================
        list_patterns = [
            # English patterns - handle "show me all my tasks", "show all tasks", "list my tasks", etc.
            (r'^(?:show|list|view|display|get)\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?(?:the\s+)?tasks?\s*$', "all"),
            (r'^(?:show|list|view)\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?(?:incomplete|pending|active|remaining)\s+tasks?\s*$', "incomplete"),
            (r'^(?:show|list|view)\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?(?:completed?|done|finished)\s+tasks?\s*$', "completed"),
            # More flexible patterns
            (r'^(?:what\s+are\s+)?(?:my\s+)?(?:all\s+)?tasks?\s*\??$', "all"),
            (r'^tasks?\s*$', "all"),
            (r'^my\s+tasks?\s*$', "all"),
            (r'^all\s+(?:my\s+)?tasks?\s*$', "all"),
            # Urdu patterns
            (r'^(?:میرے\s+)?(?:تمام|سارے|سب)\s+(?:ٹاسک|کام)\s*(?:دکھائیں|دکھاؤ)?\s*$', "all"),
            (r'^(?:نامکمل|باقی)\s+(?:ٹاسک|کام)\s*(?:دکھائیں|دکھاؤ)?\s*$', "incomplete"),
            (r'^(?:مکمل|ختم)\s+(?:ٹاسک|کام)\s*(?:دکھائیں|دکھاؤ)?\s*$', "completed"),
        ]

        for pattern, filter_type in list_patterns:
            if re.match(pattern, msg_lower, re.IGNORECASE):
                return {"action": "list_tasks", "filter": filter_type}

        # ===================
        # COMPLETE TASK
        # ===================
        complete_patterns = [
            r'^(?:complete|finish|done|mark\s+(?:as\s+)?(?:done|complete))\s+task\s*#?(\d+)\s*$',
            r'^task\s*#?(\d+)\s+(?:complete|done|finished?)\s*$',
            r'^(?:ٹاسک|کام)\s*#?(\d+)\s+(?:مکمل|ختم)\s*(?:کریں|کرو)?\s*$',
        ]

        for pattern in complete_patterns:
            match = re.match(pattern, msg_lower, re.IGNORECASE)
            if match:
                task_id = int(match.group(1))
                return {"action": "complete_task", "task_id": task_id}

        # ===================
        # DELETE TASK
        # ===================
        delete_patterns = [
            r'^(?:delete|remove|cancel)\s+task\s*#?(\d+)\s*$',
            r'^task\s*#?(\d+)\s+(?:delete|remove)\s*$',
            r'^(?:ٹاسک|کام)\s*#?(\d+)\s+(?:حذف|ڈیلیٹ)\s*(?:کریں|کرو)?\s*$',
        ]

        for pattern in delete_patterns:
            match = re.match(pattern, msg_lower, re.IGNORECASE)
            if match:
                task_id = int(match.group(1))
                return {"action": "delete_task", "task_id": task_id}

        # No direct intent detected
        return None

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message and execute appropriate action.

        Args:
            message: User's message

        Returns:
            Response with action result
        """
        current_state = self._get_state()
        print(f"Processing message with state: {current_state}")

        # Check if user wants to cancel the current flow
        msg_lower = message.lower().strip()
        if msg_lower in ["cancel", "منسوخ", "رکو", "stop", "exit", "quit"]:
            if current_state != ConversationState.IDLE:
                self._clear_pending_task()
                if self.language == "ur":
                    return {"type": "message", "content": "ٹاسک بنانا منسوخ کر دیا گیا۔ آپ کی کیا مدد کر سکتا ہوں؟"}
                return {"type": "message", "content": "Task creation cancelled. How can I help you?"}

        # Handle guided task creation flow
        if current_state != ConversationState.IDLE:
            return await self._handle_guided_flow(message)

        # ============================================
        # DIRECT INTENT DETECTION (before calling AI)
        # This ensures reliable first-attempt behavior
        # ============================================
        direct_action = self._detect_direct_intent(message)
        if direct_action:
            print(f"Direct intent detected: {direct_action}")
            return await self._execute_action(direct_action)

        # Call OpenRouter API to understand user intent
        response = await self._call_openrouter(message)
        print(f"AI Response: {response[:200]}...")

        # Try to parse JSON action from response
        try:
            action_data = self._extract_json(response)
            if action_data and "action" in action_data:
                print(f"Detected action: {action_data.get('action')}")
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
            import traceback
            traceback.print_exc()

        # No action detected - clean JSON from response before showing to user
        # Remove any JSON objects from the text
        clean_response = self._clean_json_from_response(response)

        # Translate chat response if Urdu
        if self.language == "ur":
            # Check if response contains significant English text
            english_chars = sum(1 for c in clean_response[:100] if c.isascii() and c.isalpha())
            if english_chars > 20:  # If more than 20 English letters
                print(f"Chat response in English, translating...")
                clean_response = await self._translate_to_urdu(clean_response)

        return {"type": "message", "content": clean_response}

    def _clean_json_from_response(self, text: str) -> str:
        """Remove JSON objects from response text to make it user-friendly.

        Args:
            text: Response text that may contain JSON

        Returns:
            Cleaned text without JSON
        """
        import re

        # Remove JSON objects (including nested ones)
        # Pattern matches { followed by content until matching }
        cleaned = re.sub(r'\{[^{}]*\}', '', text)

        # Remove double braces like {{action: ...}}
        cleaned = re.sub(r'\{\{[^{}]*\}\}', '', cleaned)

        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()

        # If cleaned is empty, provide a helpful message
        if not cleaned:
            if self.language == "ur":
                return "میں آپ کی مدد کرنے کے لیے تیار ہوں۔ براہ کرم بتائیں آپ کیا کرنا چاہتے ہیں؟"
            return "I'm ready to help you. What would you like to do?"

        return cleaned

    async def _handle_guided_flow(self, message: str) -> Dict[str, Any]:
        """Handle guided task creation flow based on current state.

        Args:
            message: User's response

        Returns:
            Next step question or final task creation result
        """
        current_state = self._get_state()
        pending_task = self._get_pending_task()

        if current_state == ConversationState.AWAITING_TITLE:
            # User provided title
            title = message.strip()
            if not title:
                if self.language == "ur":
                    return {"type": "guided_step", "content": "براہ کرم ٹاسک کا عنوان درج کریں (یہ ضروری ہے):"}
                return {"type": "guided_step", "content": "Please enter the task title (this is required):"}

            self._update_pending_task(title=title)
            self._set_state(ConversationState.AWAITING_DESCRIPTION)

            if self.language == "ur":
                return {
                    "type": "guided_step",
                    "step": "description",
                    "content": f"✓ عنوان: {title}\n\nاب، تفصیل درج کریں (اختیاری):\n(یا 'skip' کہیں)"
                }
            return {
                "type": "guided_step",
                "step": "description",
                "content": f"✓ Title: {title}\n\nNow, enter a description (optional):\n(or say 'skip')"
            }

        elif current_state == ConversationState.AWAITING_DESCRIPTION:
            # User provided description or skipped
            parsed = self._parse_user_response(message, "description")
            msg_lower = message.lower().strip()

            # Check if user wants AI to generate description
            generate_keywords = ["write", "generate", "create", "suggest", "you write", "tum likho", "آپ لکھیں", "خود لکھو"]
            should_generate = any(kw in msg_lower for kw in generate_keywords)

            if should_generate:
                # Generate description using AI
                pending = self._get_pending_task()
                title = pending.get("title", "")
                generated_desc = await self._generate_description(title)
                self._update_pending_task(description=generated_desc)
            elif not parsed.get("skip"):
                self._update_pending_task(description=parsed.get("value", ""))

            self._set_state(ConversationState.AWAITING_CATEGORY)
            category_options = self._format_category_options()

            pending = self._get_pending_task()
            summary = f"✓ Title: {pending.get('title', '')}"
            if pending.get('description'):
                summary += f"\n✓ Description: {pending.get('description')}"

            if self.language == "ur":
                summary = f"✓ عنوان: {pending.get('title', '')}"
                if pending.get('description'):
                    summary += f"\n✓ تفصیل: {pending.get('description')}"
                return {
                    "type": "guided_step",
                    "step": "category",
                    "content": f"{summary}\n\n📁 {category_options}"
                }
            return {
                "type": "guided_step",
                "step": "category",
                "content": f"{summary}\n\n📁 {category_options}"
            }

        elif current_state == ConversationState.AWAITING_CATEGORY:
            # User selected category or skipped
            parsed = self._parse_user_response(message, "category")
            if not parsed.get("skip"):
                if parsed.get("new_category"):
                    # Create new category
                    self._update_pending_task(new_category_name=parsed.get("new_category"))
                elif parsed.get("value"):
                    self._update_pending_task(category_id=parsed.get("value"), category_name=parsed.get("name"))

            self._set_state(ConversationState.AWAITING_PRIORITY)
            priority_options = self._format_priority_options()

            pending = self._get_pending_task()
            if self.language == "ur":
                return {
                    "type": "guided_step",
                    "step": "priority",
                    "content": f"✓ کیٹیگری منتخب ہوگئی\n\n{priority_options}"
                }
            return {
                "type": "guided_step",
                "step": "priority",
                "content": f"✓ Category selected\n\n{priority_options}"
            }

        elif current_state == ConversationState.AWAITING_PRIORITY:
            # User selected priority or skipped
            parsed = self._parse_user_response(message, "priority")
            priority = parsed.get("value", "medium") if not parsed.get("skip") else "medium"
            self._update_pending_task(priority=priority)

            self._set_state(ConversationState.AWAITING_DUE_DATE)

            if self.language == "ur":
                priority_labels = {"critical": "🔴 فوری", "high": "🟠 اہم", "medium": "🟡 درمیانہ", "low": "🟢 کم"}
                return {
                    "type": "guided_step",
                    "step": "due_date",
                    "content": f"✓ ترجیح: {priority_labels.get(priority, priority)}\n\n📅 آخری تاریخ درج کریں:\n- 'tomorrow' یا 'کل'\n- 'next week' یا 'اگلا ہفتہ'\n- یا تاریخ (YYYY-MM-DD)\n- یا 'skip' کہیں"
                }
            priority_labels = {"critical": "🔴 Critical", "high": "🟠 High", "medium": "🟡 Medium", "low": "🟢 Low"}
            return {
                "type": "guided_step",
                "step": "due_date",
                "content": f"✓ Priority: {priority_labels.get(priority, priority)}\n\n📅 Enter due date:\n- 'tomorrow'\n- 'next week'\n- or date (YYYY-MM-DD)\n- or say 'skip'"
            }

        elif current_state == ConversationState.AWAITING_DUE_DATE:
            # User provided due date or skipped
            parsed = self._parse_user_response(message, "due_date")
            if not parsed.get("skip") and parsed.get("value"):
                # Convert datetime to ISO string for JSON serialization
                due_date_value = parsed.get("value")
                if isinstance(due_date_value, datetime):
                    due_date_str = due_date_value.isoformat()
                else:
                    due_date_str = str(due_date_value)
                self._update_pending_task(due_date=due_date_str)

            self._set_state(ConversationState.AWAITING_RECURRENCE)
            recurrence_options = self._format_recurrence_options()

            if self.language == "ur":
                return {
                    "type": "guided_step",
                    "step": "recurrence",
                    "content": f"✓ تاریخ محفوظ ہوگئی\n\n🔄 {recurrence_options}"
                }
            return {
                "type": "guided_step",
                "step": "recurrence",
                "content": f"✓ Due date saved\n\n🔄 {recurrence_options}"
            }

        elif current_state == ConversationState.AWAITING_RECURRENCE:
            # User selected recurrence or skipped
            parsed = self._parse_user_response(message, "recurrence")
            if not parsed.get("skip") and parsed.get("value"):
                self._update_pending_task(recurrence_pattern=parsed.get("value"))

            self._set_state(ConversationState.AWAITING_TAGS)

            if self.language == "ur":
                return {
                    "type": "guided_step",
                    "step": "tags",
                    "content": "✓ دہرائی محفوظ ہوگئی\n\n🏷️ ٹیگز درج کریں:\n- ہیش ٹیگ استعمال کریں: #urgent #work\n- یا الفاظ: urgent, work, important\n- یا 'skip' کہیں"
                }
            return {
                "type": "guided_step",
                "step": "tags",
                "content": "✓ Recurrence saved\n\n🏷️ Enter tags:\n- Use hashtags: #urgent #work\n- or words: urgent, work, important\n- or say 'skip'"
            }

        elif current_state == ConversationState.AWAITING_TAGS:
            # User provided tags or skipped
            parsed = self._parse_user_response(message, "tags")
            if not parsed.get("skip") and parsed.get("value"):
                self._update_pending_task(tags=parsed.get("value"))

            # Now create the task!
            return await self._finalize_guided_task()

        # Unknown state, reset
        self._clear_pending_task()
        if self.language == "ur":
            return {"type": "message", "content": "کچھ غلط ہوگیا۔ براہ کرم دوبارہ کوشش کریں۔"}
        return {"type": "message", "content": "Something went wrong. Please try again."}

    async def _finalize_guided_task(self) -> Dict[str, Any]:
        """Create the task with all collected data from guided flow.

        Returns:
            Task creation result
        """
        from ..models.enums import TaskPriority, RecurrencePattern

        pending_task = self._get_pending_task()
        print(f"Finalizing guided task: {pending_task}")

        try:
            # Handle new category creation if needed
            category_id = pending_task.get("category_id")
            if pending_task.get("new_category_name"):
                category_service = CategoryService(self.session)
                category = category_service.create_or_get_category(
                    user_id=self.user_id,
                    category_name=pending_task["new_category_name"].strip().title(),
                    color="#8B5CF6",
                    icon="📁"
                )
                category_id = category.id

            # Convert priority string to enum
            priority_str = pending_task.get("priority", "medium")
            priority_map = {
                "critical": TaskPriority.CRITICAL,
                "high": TaskPriority.HIGH,
                "medium": TaskPriority.MEDIUM,
                "low": TaskPriority.LOW
            }
            priority = priority_map.get(priority_str, TaskPriority.MEDIUM)

            # Convert recurrence pattern string to enum
            recurrence_str = pending_task.get("recurrence_pattern")
            recurrence_pattern = None
            if recurrence_str:
                recurrence_map = {
                    "daily": RecurrencePattern.DAILY,
                    "weekly": RecurrencePattern.WEEKLY,
                    "monthly": RecurrencePattern.MONTHLY
                }
                recurrence_pattern = recurrence_map.get(recurrence_str)

            # Parse due_date from ISO string back to datetime
            due_date = None
            due_date_str = pending_task.get("due_date")
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str)
                except (ValueError, TypeError):
                    pass

            # Create task
            task_data = TaskCreate(
                title=pending_task.get("title", ""),
                description=pending_task.get("description") or None,
                is_completed=False,
                category_id=category_id,
                priority=priority,
                due_date=due_date,
                recurrence_pattern=recurrence_pattern,
                recurrence_interval=1,
            )

            task = TaskService.create_task(self.session, task_data, self.user_id)

            # Handle tags with error handling
            tag_names = pending_task.get("tags", [])
            if tag_names:
                try:
                    from ..services.tag_service import TagService
                    from ..models.tag import TagCreate

                    for tag_name in tag_names:
                        if tag_name and tag_name.strip():
                            try:
                                tag_data = TagCreate(name=tag_name.strip())
                                tag = TagService.create_tag(self.session, tag_data, self.user_id)
                                TagService.add_tag_to_task(self.session, task.id, tag.id)
                            except Exception as tag_error:
                                print(f"Warning: Failed to add tag '{tag_name}': {tag_error}")
                                # Continue with other tags even if one fails
                except Exception as tags_error:
                    print(f"Warning: Error handling tags: {tags_error}")
                    # Don't fail the whole task creation because of tags

            # Clear state
            self._clear_pending_task()

            # Build success message
            # Get priority as string for display
            priority_value = str(task.priority) if task.priority else "medium"

            if self.language == "ur":
                content = f"✅ ٹاسک کامیابی سے بنایا گیا!\n\n"
                content += f"📝 عنوان: {task.title}\n"
                if task.description:
                    content += f"📄 تفصیل: {task.description}\n"
                if pending_task.get("category_name") or pending_task.get("new_category_name"):
                    cat_name = pending_task.get("category_name") or pending_task.get("new_category_name")
                    content += f"📁 کیٹیگری: {cat_name}\n"
                priority_labels = {"critical": "🔴 فوری", "high": "🟠 اہم", "medium": "🟡 درمیانہ", "low": "🟢 کم"}
                content += f"⚡ ترجیح: {priority_labels.get(priority_value, priority_value)}\n"
                if task.due_date:
                    content += f"📅 آخری تاریخ: {task.due_date.strftime('%Y-%m-%d')}\n"
                if pending_task.get("recurrence_pattern"):
                    recur_labels = {"daily": "روزانہ", "weekly": "ہفتہ وار", "monthly": "ماہانہ"}
                    content += f"🔄 دہرائی: {recur_labels.get(pending_task['recurrence_pattern'], pending_task['recurrence_pattern'])}\n"
                if tag_names:
                    content += f"🏷️ ٹیگز: {', '.join(['#' + t for t in tag_names])}\n"
                content += f"\n(Task ID: {task.id})"
            else:
                content = f"✅ Task created successfully!\n\n"
                content += f"📝 Title: {task.title}\n"
                if task.description:
                    content += f"📄 Description: {task.description}\n"
                if pending_task.get("category_name") or pending_task.get("new_category_name"):
                    cat_name = pending_task.get("category_name") or pending_task.get("new_category_name")
                    content += f"📁 Category: {cat_name}\n"
                priority_labels = {"critical": "🔴 Critical", "high": "🟠 High", "medium": "🟡 Medium", "low": "🟢 Low"}
                content += f"⚡ Priority: {priority_labels.get(priority_value, priority_value)}\n"
                if task.due_date:
                    content += f"📅 Due: {task.due_date.strftime('%Y-%m-%d')}\n"
                if pending_task.get("recurrence_pattern"):
                    content += f"🔄 Recurrence: {pending_task['recurrence_pattern'].title()}\n"
                if tag_names:
                    content += f"🏷️ Tags: {', '.join(['#' + t for t in tag_names])}\n"
                content += f"\n(Task ID: {task.id})"

            return {
                "type": "task_created",
                "content": content,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "is_completed": task.is_completed,
                    "category_id": task.category_id,
                    "priority": str(task.priority) if task.priority else "medium",
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                },
            }

        except Exception as e:
            print(f"Error creating task: {e}")
            self._clear_pending_task()
            if self.language == "ur":
                return {"type": "error", "content": f"ٹاسک بنانے میں خرابی: {str(e)}"}
            return {"type": "error", "content": f"Error creating task: {str(e)}"}

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
            # Handle guided task creation flow
            if action == "start_guided_task":
                # Start the guided task creation wizard
                initial_title = action_data.get("initial_title", "").strip()

                if initial_title:
                    # User provided initial title, save it and ask for description
                    self._update_pending_task(title=initial_title)
                    self._set_state(ConversationState.AWAITING_DESCRIPTION)

                    if self.language == "ur":
                        return {
                            "type": "guided_step",
                            "step": "description",
                            "content": f"🚀 ٹاسک بنانا شروع!\n\n✓ عنوان: {initial_title}\n\nاب، تفصیل درج کریں (اختیاری):\n(یا 'skip' کہیں)"
                        }
                    return {
                        "type": "guided_step",
                        "step": "description",
                        "content": f"🚀 Starting task creation!\n\n✓ Title: {initial_title}\n\nNow, enter a description (optional):\n(or say 'skip')"
                    }
                else:
                    # No initial title, ask for title first
                    self._set_state(ConversationState.AWAITING_TITLE)

                    if self.language == "ur":
                        return {
                            "type": "guided_step",
                            "step": "title",
                            "content": "🚀 نیا ٹاسک بنانا شروع!\n\nبراہ کرم ٹاسک کا عنوان درج کریں:\n(مثال: \"دودھ خریدنا\", \"میٹنگ کی تیاری\")"
                        }
                    return {
                        "type": "guided_step",
                        "step": "title",
                        "content": "🚀 Starting new task creation!\n\nPlease enter the task title:\n(Example: \"Buy groceries\", \"Prepare for meeting\")"
                    }

            elif action == "create_task":
                title = action_data.get("title", "")
                description = action_data.get("description", "")
                category_name = action_data.get("category")
                priority = action_data.get("priority", "medium")  # Phase 4: US2
                due_date_str = action_data.get("due_date")  # Phase 4: US3
                recurrence_pattern = action_data.get("recurrence_pattern")  # Phase 4: US8

                # Validate priority
                valid_priorities = ["critical", "high", "medium", "low"]
                if priority not in valid_priorities:
                    priority = "medium"

                # Validate recurrence pattern
                valid_recurrence = ["daily", "weekly", "monthly"]
                if recurrence_pattern and recurrence_pattern not in valid_recurrence:
                    recurrence_pattern = None

                # Phase 4: US3 - Parse due date if provided
                due_date = None
                if due_date_str:
                    from ..utils.date_parser import parse_natural_date
                    from datetime import datetime

                    # Try to parse as ISO format first, then natural language
                    try:
                        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    except:
                        due_date = parse_natural_date(due_date_str)

                # Phase 4: Auto-create or get category if mentioned
                category_id = None
                if category_name:
                    category_service = CategoryService(self.session)
                    category = category_service.create_or_get_category(
                        user_id=self.user_id,
                        category_name=category_name.strip().title(),  # Capitalize first letter
                        color="#8B5CF6",  # Default purple color
                        icon="📁"  # Default folder icon
                    )
                    category_id = category.id

                task_data = TaskCreate(
                    title=title,
                    description=description or None,
                    is_completed=False,
                    category_id=category_id,  # Phase 4: US1
                    priority=priority,  # Phase 4: US2
                    due_date=due_date,  # Phase 4: US3
                    recurrence_pattern=recurrence_pattern,  # Phase 4: US8
                    recurrence_interval=1,  # Default interval
                )
                task = TaskService.create_task(
                    self.session, task_data, self.user_id
                )

                # Phase 4: US7 - Handle hashtags/tags
                tag_names = action_data.get("tags", [])
                if tag_names:
                    from ..services.tag_service import TagService
                    from ..models.tag import TagCreate

                    for tag_name in tag_names:
                        if tag_name and tag_name.strip():
                            # Create or get the tag
                            tag_data = TagCreate(name=tag_name.strip())
                            tag = TagService.create_tag(self.session, tag_data, self.user_id)
                            # Associate tag with task
                            TagService.add_tag_to_task(self.session, task.id, tag.id)

                # Build response content
                response_content = f"✓ Created task: {task.title}"
                if category_name:
                    response_content += f" (Category: {category_name.title()})"
                if priority != "medium":
                    priority_labels = {
                        "critical": "🔴 Critical",
                        "high": "🟠 High",
                        "low": "🟢 Low"
                    }
                    response_content += f" [Priority: {priority_labels.get(priority, priority.title())}]"
                if due_date:
                    from ..utils.date_parser import format_relative_date
                    response_content += f" 📅 Due: {format_relative_date(due_date)}"
                if tag_names:
                    response_content += f" 🏷️ Tags: {', '.join(['#' + t for t in tag_names])}"

                return {
                    "type": "task_created",
                    "content": response_content,
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "is_completed": task.is_completed,
                        "category_id": task.category_id,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
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

            elif action == "search_tasks":
                # Phase 4: US4 - Search functionality
                query = action_data.get("query", "").strip()
                if not query:
                    return {"type": "error", "content": "Search query is required."}

                # Use TaskService to search
                tasks = TaskService.get_tasks_by_user(
                    self.session,
                    self.user_id,
                    search_query=query
                )

                if not tasks:
                    return {
                        "type": "message",
                        "content": f"No tasks found matching '{query}'."
                    }

                task_list = "\n".join(
                    [
                        f"{i+1}. [{('✓' if t.is_completed else ' ')}] {t.title} (ID: {t.id})"
                        for i, t in enumerate(tasks)
                    ]
                )
                return {
                    "type": "search_results",
                    "content": f"Found {len(tasks)} task(s) matching '{query}':\n{task_list}",
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

            elif action == "add_subtask":
                # Phase 4: US5 - Add subtask to task
                task_id = action_data.get("task_id")
                subtask_title = action_data.get("subtask_title", "").strip()

                if not task_id:
                    return {"type": "error", "content": "Task ID is required."}
                if not subtask_title:
                    return {"type": "error", "content": "Subtask title is required."}

                # Verify task exists and belongs to user
                task = TaskService.get_task_by_id(self.session, task_id, self.user_id)
                if not task:
                    return {"type": "error", "content": f"Task {task_id} not found."}

                # Import SubtaskService
                from ..services.subtask_service import SubtaskService
                from ..models.subtask import SubtaskCreate

                subtask_data = SubtaskCreate(title=subtask_title, is_completed=False, order=0)
                subtask = SubtaskService.create_subtask(self.session, task_id, subtask_data)

                return {
                    "type": "subtask_added",
                    "content": f"✓ Added subtask '{subtask.title}' to task: {task.title}",
                    "subtask": {
                        "id": subtask.id,
                        "title": subtask.title,
                        "parent_task_id": subtask.parent_task_id,
                        "is_completed": subtask.is_completed,
                    },
                }

            elif action == "complete_subtask":
                # Phase 4: US5 - Complete subtask
                subtask_id = action_data.get("subtask_id")
                if not subtask_id:
                    return {"type": "error", "content": "Subtask ID is required."}

                from ..services.subtask_service import SubtaskService
                from ..models.subtask import SubtaskUpdate

                # Get subtask and verify parent task ownership
                subtask = SubtaskService.get_subtask_by_id(self.session, subtask_id)
                if not subtask:
                    return {"type": "error", "content": f"Subtask {subtask_id} not found."}

                task = TaskService.get_task_by_id(self.session, subtask.parent_task_id, self.user_id)
                if not task:
                    return {"type": "error", "content": "Parent task not found or access denied."}

                subtask_update = SubtaskUpdate(is_completed=True)
                updated_subtask = SubtaskService.update_subtask(self.session, subtask_id, subtask_update)

                if not updated_subtask:
                    return {"type": "error", "content": f"Subtask {subtask_id} not found."}

                return {
                    "type": "subtask_completed",
                    "content": f"✓ Completed subtask: {updated_subtask.title}",
                    "subtask": {
                        "id": updated_subtask.id,
                        "title": updated_subtask.title,
                        "is_completed": updated_subtask.is_completed,
                    },
                }

            elif action == "delete_subtask":
                # Phase 4: US5 - Delete subtask
                subtask_id = action_data.get("subtask_id")
                if not subtask_id:
                    return {"type": "error", "content": "Subtask ID is required."}

                from ..services.subtask_service import SubtaskService

                # Get subtask and verify parent task ownership
                subtask = SubtaskService.get_subtask_by_id(self.session, subtask_id)
                if not subtask:
                    return {"type": "error", "content": f"Subtask {subtask_id} not found."}

                task = TaskService.get_task_by_id(self.session, subtask.parent_task_id, self.user_id)
                if not task:
                    return {"type": "error", "content": "Parent task not found or access denied."}

                success = SubtaskService.delete_subtask(self.session, subtask_id)
                if not success:
                    return {"type": "error", "content": f"Subtask {subtask_id} not found."}

                return {
                    "type": "subtask_deleted",
                    "content": f"✓ Deleted subtask ID {subtask_id}",
                }

            else:
                return {"type": "error", "content": f"Unknown action: {action}"}

        except ValueError as e:
            return {"type": "error", "content": str(e)}
        except Exception as e:
            return {"type": "error", "content": f"Error: {str(e)}"}


def create_chat_agent(session: Session, user_id: str, language: str = "en", conversation=None) -> ChatAgent:
    """Factory function to create a chat agent.

    Args:
        session: Database session
        user_id: User ID
        language: User's preferred language (en or ur)
        conversation: Conversation object for state persistence

    Returns:
        ChatAgent instance
    """
    return ChatAgent(session, user_id, language, conversation)
