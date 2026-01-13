"""Attachment model for file uploads on tasks."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class AttachmentBase(SQLModel):
    """Base model for Attachment - shared fields."""

    filename: str = Field(max_length=255, nullable=False)
    original_filename: str = Field(max_length=255, nullable=False)
    file_type: str = Field(max_length=100, nullable=False)  # MIME type
    file_size: int = Field(nullable=False)  # Size in bytes
    cloudinary_url: str = Field(max_length=500, nullable=False)
    cloudinary_public_id: str = Field(max_length=255, nullable=False)


class Attachment(AttachmentBase, table=True):
    """Database model for Attachment entity.

    Attributes:
        id: Auto-incrementing primary key
        task_id: Foreign key to Task
        user_id: Foreign key to User (for security checks)
        filename: Stored filename in Cloudinary
        original_filename: Original filename from upload
        file_type: MIME type (image/png, application/pdf, etc.)
        file_size: File size in bytes
        cloudinary_url: Full URL to file in Cloudinary
        cloudinary_public_id: Cloudinary public ID for deletion
        created_at: Timestamp when file was uploaded
    """

    __tablename__ = "attachments"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", nullable=False, index=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class AttachmentCreate(SQLModel):
    """Schema for creating an attachment.

    Note: Most fields are assigned by server after upload.
    """
    task_id: int


class AttachmentRead(AttachmentBase):
    """Schema for reading an attachment."""

    id: int
    task_id: int
    user_id: str
    created_at: datetime
