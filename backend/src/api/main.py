"""FastAPI application entry point."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Load .env from backend directory explicitly
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / ".env"
print(f"Loading .env from: {env_path}")
load_dotenv(env_path, override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
print("=" * 60)
print("🚀 BACKEND STARTING WITH DEBUG MODE")
print("=" * 60)
print(f"Loaded .env file: {env_path}")
print(f"File exists: {env_path.exists()}")
print(f"OpenRouter API Key: {os.getenv('OPENAI_API_KEY', 'MISSING')[:30]}...")
print(f"OpenRouter Base URL: {os.getenv('OPENAI_BASE_URL', 'MISSING')}")
print(f"AI Model: {os.getenv('AI_MODEL', 'MISSING')}")
print("=" * 60)


# Create FastAPI application
app = FastAPI(
    title="Todo App API",
    description="RESTful API for multi-tenant task management",
    version="1.0.0",
)

# Get CORS origins from environment variable
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
origins_list = [origin.strip() for origin in cors_origins.split(",")]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,  # Specific origins from environment
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type"],
    max_age=3600,  # Cache preflight requests for 1 hour
)


# =============================================================================
# Phase 4: APScheduler Setup for Recurring Tasks
# =============================================================================

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

# Initialize background scheduler
scheduler = BackgroundScheduler()


def generate_recurring_tasks():
    """
    Background job to generate next occurrences for recurring tasks.
    Runs every hour to check if new task instances should be created.
    """
    logger.info("🔄 Running recurring task generation job...")

    try:
        from ..db.session import get_session
        from ..models.task import Task
        from ..models.enums import RecurrencePattern
        from ..utils.recurrence import calculate_next_occurrence, should_generate_occurrence
        from datetime import datetime

        # Get database session
        session = next(get_session())

        # Find tasks that need next occurrence generated
        recurring_tasks = session.query(Task).filter(
            Task.recurrence_pattern.isnot(None),
            Task.next_recurrence_date <= datetime.utcnow()
        ).all()

        generated_count = 0

        for task in recurring_tasks:
            # Create next occurrence
            new_task = Task(
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                priority=task.priority,
                category_id=task.category_id,
                recurrence_pattern=task.recurrence_pattern,
                recurrence_interval=task.recurrence_interval,
                parent_recurrence_id=task.id,  # Link to original recurring task
                next_recurrence_date=calculate_next_occurrence(
                    datetime.utcnow(),
                    task.recurrence_pattern,
                    task.recurrence_interval
                )
            )

            session.add(new_task)
            generated_count += 1

            # Update original task's next_recurrence_date
            task.next_recurrence_date = calculate_next_occurrence(
                task.next_recurrence_date or datetime.utcnow(),
                task.recurrence_pattern,
                task.recurrence_interval
            )

        session.commit()
        session.close()

        logger.info(f"✅ Generated {generated_count} recurring task occurrences")

    except Exception as e:
        logger.error(f"❌ Error generating recurring tasks: {e}", exc_info=True)


# Schedule the job to run every hour
scheduler.add_job(
    func=generate_recurring_tasks,
    trigger=IntervalTrigger(hours=1),
    id="generate_recurring_tasks",
    name="Generate recurring task occurrences",
    replace_existing=True
)

# Start the scheduler
scheduler.start()
logger.info("⏰ APScheduler started - recurring tasks will be generated every hour")

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


# Global exception handlers


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions (4xx, 5xx status codes).

    Returns appropriate error response without exposing internal details.
    """
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url.path}"
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors (invalid request body, query params, etc.).

    Returns 400 Bad Request with validation error details.
    """
    logger.warning(
        f"Validation error: {exc.errors()} - {request.method} {request.url.path}"
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.

    Logs the full error internally but returns generic 500 error to client
    to avoid exposing internal implementation details.
    """
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)} - "
        f"{request.method} {request.url.path}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later."},
    )


@app.get("/")
async def root():
    """Root endpoint.

    Returns:
        dict: Welcome message
    """
    return {
        "message": "Todo App API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Import and include routers
from .routes import chat, health, tasks

app.include_router(health.router, tags=["Health"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
