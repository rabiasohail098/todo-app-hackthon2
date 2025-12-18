"""Chat API routes for AI chatbot."""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, Field

from ..deps import get_db, get_current_user
from ...services.chat_service import ChatService
from ...models.message import MessageRead, MessageRole
from ...models.conversation import ConversationRead
from ...agent.chat_agent import create_chat_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    """Request body for chat message."""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: str


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Send a chat message and get AI response.

    Security:
    - user_id comes from JWT token, not from request body
    - All operations are scoped to the authenticated user
    """
    # Get or create conversation
    if request.conversation_id:
        conversation = ChatService.get_conversation_by_id(
            session, request.conversation_id, user_id
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        conversation = ChatService.get_or_create_conversation(session, user_id)

    # Save user message
    user_message = ChatService.save_message(
        session,
        conversation.id,
        MessageRole.user,
        request.message
    )

    # Get conversation history for context
    history = ChatService.get_recent_context(session, conversation.id, limit=10)
    conversation_history = [
        {"role": msg.role.value, "content": msg.content}
        for msg in history
        if msg.id != user_message.id  # Exclude the just-saved message
    ]

    # Process with AI agent
    try:
        agent = create_chat_agent(session, user_id)
        ai_response_content = agent.process_message(
            request.message,
            conversation_history
        )
    except Exception as e:
        logger.error(f"AI agent error: {str(e)}")
        ai_response_content = "I apologize, but I'm having trouble processing your request right now. Please try again."

    # Save AI response
    ai_message = ChatService.save_message(
        session,
        conversation.id,
        MessageRole.assistant,
        ai_response_content
    )

    return ChatResponse(
        id=ai_message.id,
        conversation_id=conversation.id,
        role=ai_message.role.value,
        content=ai_message.content,
        created_at=ai_message.created_at.isoformat()
    )


@router.get("/history", response_model=List[MessageRead])
async def get_chat_history(
    conversation_id: Optional[UUID] = None,
    user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Get chat history for the current conversation.

    Security:
    - Only returns messages from conversations owned by the authenticated user
    """
    # Get conversation
    if conversation_id:
        conversation = ChatService.get_conversation_by_id(
            session, conversation_id, user_id
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        conversation = ChatService.get_or_create_conversation(session, user_id)

    # Get message history
    messages = ChatService.get_conversation_history(session, conversation.id)

    return [
        MessageRead(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]


@router.get("/conversations", response_model=List[ConversationRead])
async def get_conversations(
    user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Get all conversations for the current user.

    Security:
    - Only returns conversations owned by the authenticated user
    """
    conversations = ChatService.get_conversations_by_user(session, user_id)

    return [
        ConversationRead(
            id=conv.id,
            user_id=conv.user_id,
            created_at=conv.created_at
        )
        for conv in conversations
    ]


@router.post("/conversations", response_model=ConversationRead)
async def create_conversation(
    user_id: UUID = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Create a new conversation.

    Security:
    - Conversation is created for the authenticated user only
    """
    conversation = ChatService.create_conversation(session, user_id)

    return ConversationRead(
        id=conversation.id,
        user_id=conversation.user_id,
        created_at=conversation.created_at
    )
