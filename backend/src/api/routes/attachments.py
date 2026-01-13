"""API routes for task file attachments."""

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session

from ..deps import get_db, get_current_user
from ...services.attachment_service import AttachmentService
from ...models.attachment import AttachmentRead

router = APIRouter(prefix="/api/tasks", tags=["attachments"])


@router.post("/{task_id}/attachments", response_model=AttachmentRead, status_code=201)
async def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload file attachment to a task.

    Args:
        task_id: ID of task to attach file to
        file: File to upload (max 10MB)
        current_user: User ID from JWT token
        db: Database session

    Returns:
        Created attachment record with Cloudinary URL

    Raises:
        404: Task not found or user doesn't own task
        413: File too large (>10MB)
        415: File type not allowed
        500: Upload failed
    """
    return await AttachmentService.upload_attachment(
        db=db,
        task_id=task_id,
        user_id=current_user,
        file=file
    )


@router.get("/{task_id}/attachments", response_model=List[AttachmentRead])
def get_task_attachments(
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all attachments for a task.

    Args:
        task_id: ID of task
        current_user: User ID from JWT token
        db: Database session

    Returns:
        List of attachments ordered by created_at desc

    Raises:
        404: Task not found or user doesn't own task
    """
    return AttachmentService.get_task_attachments(
        db=db,
        task_id=task_id,
        user_id=current_user
    )


@router.delete("/{task_id}/attachments/{attachment_id}", status_code=204)
def delete_attachment(
    task_id: int,
    attachment_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an attachment.

    Args:
        task_id: ID of task (for URL consistency)
        attachment_id: ID of attachment to delete
        current_user: User ID from JWT token
        db: Database session

    Raises:
        404: Attachment not found or user doesn't own it
    """
    AttachmentService.delete_attachment(
        db=db,
        attachment_id=attachment_id,
        user_id=current_user
    )
    return None
