"""
File Validator Utility - Phase 4: Intermediate Features
Validates file types, sizes, and content for safe uploads
"""

from typing import Optional
import os
import mimetypes


# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
MAX_FILENAME_LENGTH = 255

# Allowed MIME types for attachments
ALLOWED_MIME_TYPES = {
    # Documents
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
    "text/plain",
    "text/csv",
    "text/markdown",

    # Images
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",

    # Archives
    "application/zip",
    "application/x-rar-compressed",
    "application/x-7z-compressed",
    "application/gzip",

    # Code files
    "text/html",
    "text/css",
    "text/javascript",
    "application/json",
    "application/xml",
}

# File extensions to MIME type mapping (fallback)
EXTENSION_TO_MIME = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".md": "text/markdown",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".zip": "application/zip",
    ".rar": "application/x-rar-compressed",
    ".7z": "application/x-7z-compressed",
    ".gz": "application/gzip",
    ".html": "text/html",
    ".css": "text/css",
    ".js": "text/javascript",
    ".json": "application/json",
    ".xml": "application/xml",
}


class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    pass


def validate_file_size(file_size: int) -> None:
    """
    Validate file size does not exceed limit.

    Args:
        file_size: Size of file in bytes

    Raises:
        FileValidationError: If file size exceeds limit
    """
    if file_size > MAX_FILE_SIZE:
        raise FileValidationError(
            f"File size ({file_size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes / 10MB)"
        )

    if file_size == 0:
        raise FileValidationError("File is empty (0 bytes)")


def validate_filename(filename: str) -> None:
    """
    Validate filename is safe and meets requirements.

    Args:
        filename: Name of the file

    Raises:
        FileValidationError: If filename is invalid
    """
    if not filename or not filename.strip():
        raise FileValidationError("Filename cannot be empty")

    if len(filename) > MAX_FILENAME_LENGTH:
        raise FileValidationError(
            f"Filename too long (max {MAX_FILENAME_LENGTH} characters)"
        )

    # Check for path traversal attempts
    if ".." in filename or "/" in filename or "\\" in filename:
        raise FileValidationError(
            "Filename contains invalid characters (path traversal detected)"
        )

    # Check for dangerous characters
    dangerous_chars = ["<", ">", ":", '"', "|", "?", "*"]
    if any(char in filename for char in dangerous_chars):
        raise FileValidationError(
            f"Filename contains invalid characters: {dangerous_chars}"
        )


def get_mime_type(filename: str) -> Optional[str]:
    """
    Determine MIME type from filename extension.

    Args:
        filename: Name of the file

    Returns:
        MIME type string or None if cannot determine
    """
    # Get file extension
    _, ext = os.path.splitext(filename.lower())

    # Try our mapping first
    if ext in EXTENSION_TO_MIME:
        return EXTENSION_TO_MIME[ext]

    # Fallback to mimetypes module
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type


def validate_mime_type(filename: str, declared_mime: Optional[str] = None) -> str:
    """
    Validate and return MIME type for file.

    Args:
        filename: Name of the file
        declared_mime: MIME type declared by uploader (optional)

    Returns:
        Validated MIME type

    Raises:
        FileValidationError: If MIME type is not allowed
    """
    # Determine actual MIME type from filename
    actual_mime = get_mime_type(filename)

    if not actual_mime:
        raise FileValidationError(
            f"Cannot determine file type for: {filename}"
        )

    # Check if MIME type is allowed
    if actual_mime not in ALLOWED_MIME_TYPES:
        raise FileValidationError(
            f"File type not allowed: {actual_mime}. "
            f"Allowed types: PDF, images, documents, archives, text files"
        )

    # If declared MIME doesn't match actual, reject
    if declared_mime and declared_mime != actual_mime:
        raise FileValidationError(
            f"MIME type mismatch: declared '{declared_mime}' but detected '{actual_mime}'"
        )

    return actual_mime


def validate_file(filename: str, file_size: int, declared_mime: Optional[str] = None) -> dict:
    """
    Comprehensive file validation.

    Args:
        filename: Name of the file
        file_size: Size of file in bytes
        declared_mime: MIME type declared by uploader (optional)

    Returns:
        Dict with validation results: {
            "valid": True,
            "filename": sanitized filename,
            "mime_type": validated MIME type,
            "file_size": file size
        }

    Raises:
        FileValidationError: If any validation fails
    """
    # Validate filename
    validate_filename(filename)

    # Validate file size
    validate_file_size(file_size)

    # Validate and get MIME type
    mime_type = validate_mime_type(filename, declared_mime)

    # Sanitize filename (remove leading/trailing spaces)
    sanitized_filename = filename.strip()

    return {
        "valid": True,
        "filename": sanitized_filename,
        "mime_type": mime_type,
        "file_size": file_size,
    }


def is_image(mime_type: str) -> bool:
    """
    Check if MIME type is an image.

    Args:
        mime_type: MIME type string

    Returns:
        True if image, False otherwise
    """
    return mime_type.startswith("image/")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"

    kb = size_bytes / 1024
    if kb < 1024:
        return f"{kb:.2f} KB"

    mb = kb / 1024
    if mb < 1024:
        return f"{mb:.2f} MB"

    gb = mb / 1024
    return f"{gb:.2f} GB"


# Export all functions and constants
__all__ = [
    "validate_file",
    "validate_file_size",
    "validate_filename",
    "validate_mime_type",
    "get_mime_type",
    "is_image",
    "format_file_size",
    "FileValidationError",
    "MAX_FILE_SIZE",
    "ALLOWED_MIME_TYPES",
]
