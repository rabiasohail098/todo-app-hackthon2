"""Service layer for file attachment operations using Cloudinary."""

import os
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import UploadFile, HTTPException
import cloudinary
import cloudinary.uploader
import cloudinary.api

from ..models.attachment import Attachment, AttachmentRead
from ..models.task import Task


class AttachmentService:
    """Service for managing task file attachments with Cloudinary storage."""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_TYPES = {
        "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain", "text/csv",
        "application/zip", "application/x-zip-compressed"
    }

    @staticmethod
    async def upload_attachment(
        db: Session,
        task_id: int,
        user_id: str,
        file: UploadFile
    ) -> AttachmentRead:
        """Upload file to Cloudinary and create attachment record.

        Args:
            db: Database session
            task_id: ID of task to attach file to
            user_id: ID of user uploading file (for security check)
            file: Uploaded file from FastAPI

        Returns:
            Created attachment record

        Raises:
            HTTPException: If task not found, user doesn't own task, file too large, or invalid type
        """
        # Verify task exists and user owns it
        task = db.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found or you don't have permission"
            )

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size
        if file_size > AttachmentService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size ({file_size} bytes) exceeds maximum {AttachmentService.MAX_FILE_SIZE} bytes (10MB)"
            )

        # Validate file type
        content_type = file.content_type or "application/octet-stream"
        if content_type not in AttachmentService.ALLOWED_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"File type {content_type} not allowed. Allowed types: {', '.join(AttachmentService.ALLOWED_TYPES)}"
            )

        # Upload to Cloudinary
        try:
            # Reset file pointer
            await file.seek(0)

            # Determine resource type
            resource_type = "image" if content_type.startswith("image/") else "raw"

            # Upload with user-specific folder structure
            upload_result = cloudinary.uploader.upload(
                file.file,
                folder=f"todo-attachments/{user_id}/task-{task_id}",
                resource_type=resource_type,
                use_filename=True,
                unique_filename=True
            )

            # Create attachment record
            attachment = Attachment(
                task_id=task_id,
                user_id=user_id,
                filename=upload_result["public_id"].split("/")[-1],
                original_filename=file.filename or "unnamed",
                file_type=content_type,
                file_size=file_size,
                cloudinary_url=upload_result["secure_url"],
                cloudinary_public_id=upload_result["public_id"]
            )

            db.add(attachment)
            db.commit()
            db.refresh(attachment)

            return AttachmentRead.model_validate(attachment)

        except Exception as e:
            db.rollback()
            # Try to delete from Cloudinary if DB save failed
            try:
                if 'upload_result' in locals():
                    cloudinary.uploader.destroy(upload_result["public_id"])
            except:
                pass
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file: {str(e)}"
            )

    @staticmethod
    def get_task_attachments(
        db: Session,
        task_id: int,
        user_id: str
    ) -> List[AttachmentRead]:
        """Get all attachments for a task.

        Args:
            db: Database session
            task_id: ID of task
            user_id: ID of user (for security check)

        Returns:
            List of attachments

        Raises:
            HTTPException: If task not found or user doesn't own task
        """
        # Verify task exists and user owns it
        task = db.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found or you don't have permission"
            )

        # Get attachments
        attachments = db.exec(
            select(Attachment)
            .where(Attachment.task_id == task_id, Attachment.user_id == user_id)
            .order_by(Attachment.created_at.desc())
        ).all()

        return [AttachmentRead.model_validate(att) for att in attachments]

    @staticmethod
    def delete_attachment(
        db: Session,
        attachment_id: int,
        user_id: str
    ) -> None:
        """Delete attachment from Cloudinary and database.

        Args:
            db: Database session
            attachment_id: ID of attachment to delete
            user_id: ID of user (for security check)

        Raises:
            HTTPException: If attachment not found or user doesn't own it
        """
        # Get attachment
        attachment = db.exec(
            select(Attachment)
            .where(Attachment.id == attachment_id, Attachment.user_id == user_id)
        ).first()

        if not attachment:
            raise HTTPException(
                status_code=404,
                detail=f"Attachment {attachment_id} not found or you don't have permission"
            )

        # Delete from Cloudinary
        try:
            cloudinary.uploader.destroy(attachment.cloudinary_public_id)
        except Exception as e:
            # Log error but continue with DB deletion
            print(f"Warning: Failed to delete from Cloudinary: {e}")

        # Delete from database
        db.delete(attachment)
        db.commit()
