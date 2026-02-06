"""Chat API routes."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from pydantic import BaseModel, Field

from ...services.chat_service import ChatService
from ...models.conversation import Conversation
from ...models.message import Message
from ..deps import get_db, get_current_user

router = APIRouter()


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    language: str = Field(default="en", pattern="^(en|ur)$")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: str
    message_id: str
    response: str
    type: str
    data: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Response model for a single message."""
    id: str
    role: str
    content: str
    created_at: str


class ConversationMessagesResponse(BaseModel):
    """Response model for conversation messages."""
    conversation_id: str
    messages: List[MessageResponse]


@router.post("/", response_model=ChatResponse)
async def send_message(
    request: Request,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Send a message to the AI chatbot and get a response.

    Args:
        request: FastAPI request object (for header access)
        chat_request: Chat request with message and optional conversation_id
        db: Database session
        current_user: Authenticated user ID from JWT

    Returns:
        AI response with conversation and message IDs
    """
    user_id = current_user

    print(f"=== CHAT REQUEST ===")
    print(f"User ID: {user_id}")
    print(f"Message: {chat_request.message[:50]}...")
    print(f"Language: {chat_request.language}")
    print(f"===================")

    chat_service = ChatService(db)

    try:
        # Convert conversation_id to UUID if provided
        conversation_uuid = None
        if chat_request.conversation_id:
            try:
                conversation_uuid = UUID(chat_request.conversation_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation ID format"
                )

        # Process message (stateless request cycle)
        result = await chat_service.process_message(
            user_id=user_id,
            message=chat_request.message,
            conversation_id=conversation_uuid,
            language=chat_request.language
        )

        return ChatResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Log the full error for debugging
        print(f"Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()

        # Provide a user-friendly error message
        error_msg = str(e)
        if "OpenRouter" in error_msg or "API" in error_msg:
            detail_msg = "AI service is temporarily unavailable. Please try again later."
        elif "database" in error_msg.lower() or "connection" in error_msg.lower():
            detail_msg = "Database connection error. Please try again later."
        elif "timeout" in error_msg.lower():
            detail_msg = "Request timed out. Please try again with a shorter message."
        else:
            detail_msg = "An error occurred while processing your message. Please try again."

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail_msg
        )


@router.get("/conversations/{conversation_id}/messages", response_model=ConversationMessagesResponse)
def get_conversation_messages(
    request: Request,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    limit: int = 50,
):
    """Get all messages from a conversation.

    Args:
        conversation_id: Conversation UUID
        db: Database session
        current_user: Authenticated user ID from JWT
        limit: Maximum number of messages to retrieve

    Returns:
        List of messages in chronological order
    """
    user_id = current_user

    print(f"Getting messages for conversation: {conversation_id}")

    try:
        conversation_uuid = UUID(conversation_id)
    except ValueError as e:
        print(f"Invalid UUID format: {conversation_id}, error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID format: {conversation_id}"
        )

    chat_service = ChatService(db)

    try:
        messages = chat_service.get_all_messages(
            conversation_id=conversation_uuid,
            user_id=user_id,
            limit=limit
        )

        return ConversationMessagesResponse(
            conversation_id=conversation_id,
            messages=[MessageResponse(**msg) for msg in messages]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )


@router.get("/conversations")
def get_user_conversations(
    request: Request,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Get all conversations for the authenticated user.

    Args:
        db: Database session
        current_user: Authenticated user ID from JWT

    Returns:
        List of user's conversations
    """
    user_id = current_user

    chat_service = ChatService(db)

    try:
        conversations = chat_service.get_user_conversations(user_id)
        return {"conversations": conversations}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversations: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    request: Request,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Delete a conversation.

    Args:
        conversation_id: Conversation UUID
        db: Database session
        current_user: Authenticated user ID from JWT

    Returns:
        Success message
    """
    user_id = current_user

    print(f"Deleting conversation: {conversation_id} for user: {user_id}")

    try:
        conversation_uuid = UUID(conversation_id)
    except ValueError as e:
        print(f"Invalid UUID format: {conversation_id}, error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID format: {conversation_id}"
        )

    try:
        # Verify conversation belongs to user
        statement = select(Conversation).where(
            Conversation.id == conversation_uuid,
            Conversation.user_id == user_id
        )
        result = db.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )

        # Delete all messages first (cascade)
        delete_messages_stmt = delete(Message).where(
            Message.conversation_id == conversation_uuid
        )
        messages_result = db.execute(delete_messages_stmt)
        print(f"Deleted {messages_result.rowcount} messages")

        # Delete conversation
        delete_conv_stmt = delete(Conversation).where(
            Conversation.id == conversation_uuid
        )
        db.execute(delete_conv_stmt)
        db.commit()

        print(f"Conversation {conversation_id} deleted successfully")
        return {"message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )
