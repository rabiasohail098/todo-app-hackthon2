"""Conversation model for AI chatbot."""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
import json

if TYPE_CHECKING:
    from .message import Message


class ConversationBase(SQLModel):
    """Base model for Conversation."""
    pass


class Conversation(ConversationBase, table=True):
    """Database model for Conversation entity.

    Represents a chat conversation session between user and AI assistant.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Owner of the conversation
        created_at: When conversation started
        updated_at: When conversation was last modified
        guided_state: Current state in guided task creation flow
        pending_task_json: JSON string of pending task data during guided flow
        messages: Related messages in this conversation
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Guided task creation state (stored in DB for persistence across requests)
    guided_state: Optional[str] = Field(default="idle", nullable=True)
    pending_task_json: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")

    def get_pending_task(self) -> dict:
        """Get pending task data as dictionary."""
        if self.pending_task_json:
            try:
                return json.loads(self.pending_task_json)
            except:
                return {}
        return {}

    def set_pending_task(self, data: dict):
        """Set pending task data from dictionary."""
        self.pending_task_json = json.dumps(data) if data else None


class ConversationCreate(SQLModel):
    """Schema for creating a conversation."""
    pass  # Auto-created from user_id


class ConversationRead(SQLModel):
    """Schema for reading a conversation."""
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None
