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

    Represents a chat session between a user and the AI assistant.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Owner of the conversation (from JWT)
        created_at: When conversation was started
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationCreate(SQLModel):
    """Schema for creating a conversation.

    Note: user_id is assigned by server from JWT, not from request body.
    """
    pass


class ConversationRead(SQLModel):
    """Schema for reading a conversation."""
    id: UUID
    user_id: UUID
    created_at: datetime
