"""Cloudinary configuration and initialization."""

import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


def get_cloudinary_config():
    """Get current Cloudinary configuration status."""
    return {
        "cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME"),
        "configured": bool(os.getenv("CLOUDINARY_CLOUD_NAME") and
                          os.getenv("CLOUDINARY_API_KEY") and
                          os.getenv("CLOUDINARY_API_SECRET"))
    }
