"""Chat service for managing AI chatbot conversations."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from ..models.conversation import Conversation
from ..models.message import Message, MessageRole
from ..agent.chat_agent import create_chat_agent


class ChatService:
    """Service for managing chat conversations and messages."""

    def __init__(self, session: Session):
        """Initialize chat service.

        Args:
            session: Database session
        """
        self.session = session

    def create_conversation(self, user_id: str) -> Conversation:
        """Create a new conversation for user.

        Args:
            user_id: User ID

        Returns:
            New conversation instance
        """
        # Always create a new conversation
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        return conversation

    def get_conversation_history(
        self, conversation_id: UUID, limit: int = 10
    ) -> List[Message]:
        """Get conversation history (last N messages).

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages in chronological order
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )

        result = self.session.execute(statement)
        messages = result.scalars().all()

        # Reverse to get chronological order (oldest first)
        return list(reversed(messages))

    def save_message(
        self, conversation_id: UUID, role: MessageRole, content: str
    ) -> Message:
        """Save a message to the database.

        Args:
            conversation_id: Conversation ID
            role: Message role (user or assistant)
            content: Message content

        Returns:
            Created message
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)

        # Update conversation updated_at
        statement = select(Conversation).where(Conversation.id == conversation_id)
        result = self.session.execute(statement)
        conversation = result.scalar_one()
        conversation.updated_at = datetime.utcnow()
        self.session.commit()

        return message

    async def process_message(
        self, user_id: str, message: str, conversation_id: Optional[UUID] = None, language: str = "en"
    ) -> Dict[str, Any]:
        """Process user message and get AI response.

        This implements the stateless request cycle:
        1. Get or create conversation
        2. Save user message
        3. Fetch conversation history for context
        4. Initialize AI agent (fresh instance)
        5. Process message with agent
        6. Save assistant response
        7. Return response

        Args:
            user_id: User ID
            message: User's message
            conversation_id: Optional conversation ID
            language: User's preferred language (en or ur)

        Returns:
            Response dictionary with conversation_id, message_id, and AI response
        """
        # Step 1: Get or create conversation
        if conversation_id:
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            result = self.session.execute(statement)
            conversation = result.scalar_one_or_none()
            if not conversation:
                raise ValueError("Conversation not found or access denied")
        else:
            # Create new conversation when conversation_id is None
            conversation = self.create_conversation(user_id)

        # Step 2: Save user message
        user_message = self.save_message(
            conversation.id, MessageRole.user, message
        )

        # Step 3: Fetch conversation history (for context)
        history = self.get_conversation_history(conversation.id, limit=10)

        # Step 4: Initialize AI agent with conversation for state persistence
        print(f"Creating agent with language: {language}")
        agent = create_chat_agent(self.session, user_id, language, conversation)

        # Step 5: Process message
        try:
            response_data = await agent.process_message(message)
            response_content = response_data.get("content", "I'm not sure how to help with that.")
            # Commit any state changes made by the agent
            self.session.commit()
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            import traceback
            traceback.print_exc()

            # More user-friendly error message
            if "OpenRouter API error" in str(e):
                response_content = "Sorry, I'm having trouble connecting to the AI service right now. Please try again later."
            elif "invalid_grant" in str(e) or "invalid_client" in str(e):
                response_content = "Sorry, there's an issue with the AI service configuration. Please contact support."
            else:
                response_content = f"Sorry, I encountered an error: {str(e)[:200]}..." if len(str(e)) > 200 else f"Sorry, I encountered an error: {str(e)}"

            response_data = {"type": "error", "content": response_content}

        # Step 6: Save assistant response
        assistant_message = self.save_message(
            conversation.id, MessageRole.assistant, response_content
        )

        # Step 7: Return response
        # Agent instance will be garbage collected (stateless)

        # Prepare data - wrap lists in a dictionary for consistent response format
        data = None
        if "task" in response_data:
            data = {"task": response_data["task"]}
        elif "tasks" in response_data:
            data = {"tasks": response_data["tasks"]}

        return {
            "conversation_id": str(conversation.id),
            "message_id": str(assistant_message.id),
            "response": response_content,
            "type": response_data.get("type", "message"),
            "data": data,
        }

    def get_all_messages(
        self, conversation_id: UUID, user_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all messages from a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for authorization)
            limit: Maximum number of messages

        Returns:
            List of message dictionaries
        """
        # Verify conversation belongs to user
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = self.session.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise ValueError("Conversation not found or access denied")

        # Get messages
        messages = self.get_conversation_history(conversation_id, limit)

        return [
            {
                "id": str(msg.id),
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]

    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a user.

        Args:
            user_id: User ID

        Returns:
            List of conversation summaries
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
        )

        result = self.session.execute(statement)
        conversations = result.scalars().all()

        return [
            {
                "id": str(conv.id),
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            }
            for conv in conversations
        ]
