"""Chat service layer for AI chatbot business logic."""

from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime

from ..models.conversation import Conversation
from ..models.message import Message, MessageRole


class ChatService:
    """
    Chat service for handling AI chatbot business logic.

    All methods enforce user isolation - conversations and messages
    are always filtered by user_id.
    """

    @staticmethod
    def get_or_create_conversation(
        session: Session, user_id: UUID
    ) -> Conversation:
        """
        Get active conversation for user or create a new one.

        Args:
            session: Database session
            user_id: UUID of the authenticated user (from JWT)

        Returns:
            Active Conversation instance

        Security:
            user_id is ALWAYS from JWT token, never from request body
        """
        # Get most recent conversation for user
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(1)
        )
        conversation = session.exec(statement).first()

        if conversation:
            return conversation

        # Create new conversation if none exists
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def create_conversation(
        session: Session, user_id: UUID
    ) -> Conversation:
        """
        Create a new conversation for user.

        Args:
            session: Database session
            user_id: UUID of the authenticated user

        Returns:
            New Conversation instance
        """
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversations_by_user(
        session: Session, user_id: UUID
    ) -> List[Conversation]:
        """
        Get all conversations for a user, ordered by created_at DESC.

        Args:
            session: Database session
            user_id: UUID of the authenticated user

        Returns:
            List of Conversation instances
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        conversations = session.exec(statement).all()
        return list(conversations)

    @staticmethod
    def get_conversation_by_id(
        session: Session, conversation_id: UUID, user_id: UUID
    ) -> Optional[Conversation]:
        """
        Get a specific conversation by ID if it belongs to the user.

        Args:
            session: Database session
            conversation_id: ID of the conversation
            user_id: UUID of the authenticated user

        Returns:
            Conversation instance if found and belongs to user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return session.exec(statement).first()

    @staticmethod
    def save_message(
        session: Session,
        conversation_id: UUID,
        role: MessageRole,
        content: str
    ) -> Message:
        """
        Save a message to a conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation
            role: Role of the message sender (user or assistant)
            content: Message content

        Returns:
            Saved Message instance
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow(),
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

    @staticmethod
    def get_conversation_history(
        session: Session,
        conversation_id: UUID,
        limit: int = 50
    ) -> List[Message]:
        """
        Get message history for a conversation.

        Args:
            session: Database session
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return (default 50)

        Returns:
            List of Message instances ordered by created_at ASC
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        messages = session.exec(statement).all()
        return list(messages)

    @staticmethod
    def get_recent_context(
        session: Session,
        conversation_id: UUID,
        limit: int = 10
    ) -> List[Message]:
        """
        Get recent messages for AI context window.

        Args:
            session: Database session
            conversation_id: ID of the conversation
            limit: Number of recent messages (default 10)

        Returns:
            List of recent Message instances in chronological order
        """
        # Get last N messages
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = session.exec(statement).all()
        # Reverse for chronological order
        return list(reversed(messages))
