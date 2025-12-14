"""API routes package.

This package organizes all API endpoint routers.
Import and include routers in main.py to register endpoints.
"""

from .health import router as health_router
from .tasks import router as tasks_router

__all__ = ["health_router", "tasks_router"]
