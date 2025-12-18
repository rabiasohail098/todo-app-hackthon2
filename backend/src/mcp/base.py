"""Base MCP tool interface.

All MCP tools must receive user_id from the API layer to ensure
security and proper user isolation (Constitution Principle III).
"""

from typing import Any, Dict, Optional
from uuid import UUID
from abc import ABC, abstractmethod


class MCPToolError(Exception):
    """Exception raised when an MCP tool encounters an error."""

    def __init__(self, message: str, code: str = "TOOL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class MCPToolResult:
    """Result from an MCP tool execution."""

    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        self.success = success
        self.data = data or {}
        self.error = error
        self.error_code = error_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        if self.success:
            return {"success": True, "data": self.data}
        return {
            "success": False,
            "error": self.error,
            "error_code": self.error_code
        }


class BaseMCPTool(ABC):
    """Base class for MCP tools.

    All MCP tools must:
    1. Receive user_id as a parameter (from API layer, NOT from AI inference)
    2. Return MCPToolResult with success/error information
    3. Never crash - always return error messages
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for registration with the agent."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for the AI agent."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON schema for tool parameters."""
        pass

    @abstractmethod
    def execute(self, user_id: UUID, **kwargs) -> MCPToolResult:
        """Execute the tool with the given parameters.

        Args:
            user_id: UUID of the authenticated user (ALWAYS from JWT)
            **kwargs: Tool-specific parameters

        Returns:
            MCPToolResult with success status and data/error
        """
        pass
