"""MCP tool implementations for task management.

All tools receive user_id from the API layer (not from AI inference)
to ensure security and proper user isolation.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlmodel import Session

from .base import BaseMCPTool, MCPToolResult, MCPToolError
from ..models.task import Task, TaskCreate, TaskUpdate
from ..services.task_service import TaskService


class AddTaskTool(BaseMCPTool):
    """MCP tool for adding a new task."""

    def __init__(self, session: Session):
        self.session = session

    @property
    def name(self) -> str:
        return "add_task"

    @property
    def description(self) -> str:
        return "Add a new task with a title and optional description"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the task (required)"
                },
                "description": {
                    "type": "string",
                    "description": "Optional description of the task"
                }
            },
            "required": ["title"]
        }

    def execute(self, user_id: UUID, **kwargs) -> MCPToolResult:
        """Add a new task for the user."""
        try:
            title = kwargs.get("title")
            if not title or not title.strip():
                return MCPToolResult(
                    success=False,
                    error="Title is required and cannot be empty",
                    error_code="INVALID_TITLE"
                )

            description = kwargs.get("description")

            task_data = TaskCreate(
                title=title.strip(),
                description=description.strip() if description else None
            )

            task = TaskService.create_task(self.session, task_data, user_id)

            return MCPToolResult(
                success=True,
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "message": f"Task '{task.title}' created successfully with ID {task.id}"
                }
            )
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Failed to create task: {str(e)}",
                error_code="CREATE_FAILED"
            )


class ListTasksTool(BaseMCPTool):
    """MCP tool for listing tasks."""

    def __init__(self, session: Session):
        self.session = session

    @property
    def name(self) -> str:
        return "list_tasks"

    @property
    def description(self) -> str:
        return "List all tasks, optionally filtered by status (pending or completed)"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter by status: all, pending, or completed"
                }
            }
        }

    def execute(self, user_id: UUID, **kwargs) -> MCPToolResult:
        """List tasks for the user."""
        try:
            status = kwargs.get("status", "all")

            tasks = TaskService.get_tasks_by_user(self.session, user_id)

            # Filter by status if specified
            if status == "pending":
                tasks = [t for t in tasks if not t.is_completed]
            elif status == "completed":
                tasks = [t for t in tasks if t.is_completed]

            if not tasks:
                return MCPToolResult(
                    success=True,
                    data={
                        "tasks": [],
                        "count": 0,
                        "message": "No tasks found"
                    }
                )

            task_list = [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "is_completed": t.is_completed,
                    "created_at": t.created_at.isoformat()
                }
                for t in tasks
            ]

            return MCPToolResult(
                success=True,
                data={
                    "tasks": task_list,
                    "count": len(task_list),
                    "message": f"Found {len(task_list)} task(s)"
                }
            )
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Failed to list tasks: {str(e)}",
                error_code="LIST_FAILED"
            )


class CompleteTaskTool(BaseMCPTool):
    """MCP tool for marking a task as complete."""

    def __init__(self, session: Session):
        self.session = session

    @property
    def name(self) -> str:
        return "complete_task"

    @property
    def description(self) -> str:
        return "Mark a task as complete by its ID"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to mark as complete"
                }
            },
            "required": ["task_id"]
        }

    def execute(self, user_id: UUID, **kwargs) -> MCPToolResult:
        """Mark a task as complete."""
        try:
            task_id = kwargs.get("task_id")
            if task_id is None:
                return MCPToolResult(
                    success=False,
                    error="Task ID is required",
                    error_code="INVALID_TASK_ID"
                )

            # Get the task to check if it exists and belongs to user
            task = TaskService.get_task_by_id(self.session, task_id, user_id)
            if not task:
                return MCPToolResult(
                    success=False,
                    error=f"Task with ID {task_id} not found",
                    error_code="TASK_NOT_FOUND"
                )

            # Check if already completed
            if task.is_completed:
                return MCPToolResult(
                    success=True,
                    data={
                        "task_id": task.id,
                        "title": task.title,
                        "message": f"Task '{task.title}' is already marked as complete"
                    }
                )

            # Update task
            update_data = TaskUpdate(is_completed=True)
            updated_task = TaskService.update_task(
                self.session, task_id, user_id, update_data
            )

            return MCPToolResult(
                success=True,
                data={
                    "task_id": updated_task.id,
                    "title": updated_task.title,
                    "message": f"Task '{updated_task.title}' marked as complete"
                }
            )
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Failed to complete task: {str(e)}",
                error_code="COMPLETE_FAILED"
            )


class DeleteTaskTool(BaseMCPTool):
    """MCP tool for deleting a task."""

    def __init__(self, session: Session):
        self.session = session

    @property
    def name(self) -> str:
        return "delete_task"

    @property
    def description(self) -> str:
        return "Delete a task by its ID"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to delete"
                }
            },
            "required": ["task_id"]
        }

    def execute(self, user_id: UUID, **kwargs) -> MCPToolResult:
        """Delete a task."""
        try:
            task_id = kwargs.get("task_id")
            if task_id is None:
                return MCPToolResult(
                    success=False,
                    error="Task ID is required",
                    error_code="INVALID_TASK_ID"
                )

            # Get the task first to show title in message
            task = TaskService.get_task_by_id(self.session, task_id, user_id)
            if not task:
                return MCPToolResult(
                    success=False,
                    error=f"Task with ID {task_id} not found",
                    error_code="TASK_NOT_FOUND"
                )

            title = task.title
            deleted = TaskService.delete_task(self.session, task_id, user_id)

            if deleted:
                return MCPToolResult(
                    success=True,
                    data={
                        "task_id": task_id,
                        "title": title,
                        "message": f"Task '{title}' deleted successfully"
                    }
                )
            else:
                return MCPToolResult(
                    success=False,
                    error="Failed to delete task",
                    error_code="DELETE_FAILED"
                )
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Failed to delete task: {str(e)}",
                error_code="DELETE_FAILED"
            )


class UpdateTaskTool(BaseMCPTool):
    """MCP tool for updating a task."""

    def __init__(self, session: Session):
        self.session = session

    @property
    def name(self) -> str:
        return "update_task"

    @property
    def description(self) -> str:
        return "Update a task's title and/or description by its ID"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to update"
                },
                "title": {
                    "type": "string",
                    "description": "New title for the task (optional)"
                },
                "description": {
                    "type": "string",
                    "description": "New description for the task (optional)"
                }
            },
            "required": ["task_id"]
        }

    def execute(self, user_id: UUID, **kwargs) -> MCPToolResult:
        """Update a task."""
        try:
            task_id = kwargs.get("task_id")
            if task_id is None:
                return MCPToolResult(
                    success=False,
                    error="Task ID is required",
                    error_code="INVALID_TASK_ID"
                )

            title = kwargs.get("title")
            description = kwargs.get("description")

            if title is None and description is None:
                return MCPToolResult(
                    success=False,
                    error="At least one field (title or description) must be provided",
                    error_code="NO_UPDATES"
                )

            # Check if task exists
            task = TaskService.get_task_by_id(self.session, task_id, user_id)
            if not task:
                return MCPToolResult(
                    success=False,
                    error=f"Task with ID {task_id} not found",
                    error_code="TASK_NOT_FOUND"
                )

            # Build update data
            update_data = TaskUpdate(
                title=title.strip() if title else None,
                description=description.strip() if description else None
            )

            updated_task = TaskService.update_task(
                self.session, task_id, user_id, update_data
            )

            return MCPToolResult(
                success=True,
                data={
                    "task_id": updated_task.id,
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "message": f"Task '{updated_task.title}' updated successfully"
                }
            )
        except Exception as e:
            return MCPToolResult(
                success=False,
                error=f"Failed to update task: {str(e)}",
                error_code="UPDATE_FAILED"
            )


def get_all_tools(session: Session) -> List[BaseMCPTool]:
    """Get all MCP tools with the given session."""
    return [
        AddTaskTool(session),
        ListTasksTool(session),
        CompleteTaskTool(session),
        DeleteTaskTool(session),
        UpdateTaskTool(session),
    ]
