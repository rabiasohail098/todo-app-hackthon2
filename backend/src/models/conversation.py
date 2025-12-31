"""Conversation model for AI chatbot."""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

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
        messages: Related messages in this conversation
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")


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
