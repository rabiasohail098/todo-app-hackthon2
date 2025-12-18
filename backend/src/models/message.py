"""Message model for AI chatbot conversations."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Role of the message sender."""
    user = "user"
    assistant = "assistant"


class MessageBase(SQLModel):
    """Base model for Message."""
    role: MessageRole
    content: str = Field(max_length=10000)


class Message(MessageBase, table=True):
    """Database model for Message entity.

    Represents a single message in a conversation.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Parent conversation
        role: Message sender role (user or assistant)
        content: Message content
        created_at: When message was created
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True, nullable=False)
    role: MessageRole
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")


class MessageCreate(SQLModel):
    """Schema for creating a message."""
    content: str = Field(max_length=10000)


class MessageRead(SQLModel):
    """Schema for reading a message."""
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
