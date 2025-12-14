"""Health check endpoint."""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.

    This endpoint does not require authentication and can be used
    to verify that the API is running and responsive.

    Returns:
        dict: Status and timestamp
            - status: "ok" if service is healthy
            - timestamp: Current ISO 8601 timestamp

    Example response:
        {
            "status": "ok",
            "timestamp": "2025-12-10T22:45:30.123456"
        }
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }
