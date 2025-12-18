"""OpenAI-based chat agent for task management.

This agent uses OpenAI's function calling to interact with MCP tools
for task management operations.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from openai import OpenAI
from sqlmodel import Session

from ..mcp.tools import get_all_tools, BaseMCPTool
from ..mcp.base import MCPToolResult

logger = logging.getLogger(__name__)

# System prompt for the AI agent
SYSTEM_PROMPT = """You are a helpful AI assistant for managing tasks. You help users create, view, update, complete, and delete their tasks using natural language.

Available actions:
1. Add a new task - use add_task when user wants to create a task
2. View tasks - use list_tasks when user wants to see their tasks
3. Complete a task - use complete_task when user wants to mark a task as done
4. Delete a task - use delete_task when user wants to remove a task
5. Update a task - use update_task when user wants to change a task's title or description

Guidelines:
- Always be helpful and friendly
- When adding tasks, extract the title and any description from the user's message
- When the user refers to tasks by name, try to match with existing tasks
- Confirm actions after they are completed
- If an action fails, explain the error in a user-friendly way
- If the user's intent is unclear, ask for clarification

Remember: You have access to tools to manage tasks. Use them to help the user!"""


class ChatAgent:
    """AI agent for processing chat messages and executing task operations."""

    def __init__(self, session: Session, user_id: UUID):
        """Initialize the chat agent.

        Args:
            session: Database session for tool operations
            user_id: UUID of the authenticated user (from JWT)
        """
        self.session = session
        self.user_id = user_id
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tools = get_all_tools(session)
        self.tool_map = {tool.name: tool for tool in self.tools}

    def _get_openai_tools(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI function format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self.tools
        ]

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute an MCP tool and return the result as a string.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments from OpenAI

        Returns:
            String representation of the tool result
        """
        tool = self.tool_map.get(tool_name)
        if not tool:
            return json.dumps({
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            })

        try:
            # Execute tool with user_id (security: always from JWT, not AI)
            result = tool.execute(self.user_id, **arguments)
            return json.dumps(result.to_dict())
        except Exception as e:
            logger.error(f"Tool execution error: {tool_name} - {str(e)}")
            return json.dumps({
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            })

    def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Process a user message and return the AI response.

        Args:
            user_message: The user's message
            conversation_history: Previous messages for context

        Returns:
            AI response string
        """
        # Build messages for OpenAI
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        try:
            # Call OpenAI with tools
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self._get_openai_tools(),
                tool_choice="auto"
            )

            message = response.choices[0].message

            # Handle tool calls
            if message.tool_calls:
                # Process each tool call
                tool_results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    logger.info(f"Executing tool: {tool_name} with args: {arguments}")

                    result = self._execute_tool(tool_name, arguments)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": result
                    })

                # Add assistant message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })

                # Add tool results
                messages.extend(tool_results)

                # Get final response
                final_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )

                return final_response.choices[0].message.content

            # No tool calls, return direct response
            return message.content

        except Exception as e:
            logger.error(f"Chat agent error: {str(e)}")
            return f"I apologize, but I encountered an error processing your request. Please try again. Error: {str(e)}"


def create_chat_agent(session: Session, user_id: UUID) -> ChatAgent:
    """Factory function to create a ChatAgent.

    Args:
        session: Database session
        user_id: UUID of the authenticated user

    Returns:
        ChatAgent instance
    """
    return ChatAgent(session, user_id)
