"""FastAPI application entry point."""

import logging
import os
from pathlib import Path

# Rebuild triggered on 2026-02-06 to refresh Hugging Face Space

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

# Validate required environment variables (FR-015, FR-016, FR-017)
import sys

REQUIRED_ENV_VARS = {
    "DATABASE_URL": "Database connection string (PostgreSQL)",
    "JWT_SECRET": "Secret key for JWT token generation",
    "CORS_ORIGINS": "Allowed CORS origins (comma-separated)"
}

missing_vars = []
for var, description in REQUIRED_ENV_VARS.items():
    if not os.getenv(var):
        missing_vars.append(f"  [X] {var}: {description}")
        print(f"[X] ERROR: {var} environment variable is not set", file=sys.stderr)
        print(f"Fix: Add {var}=your-value to your .env file", file=sys.stderr)

if missing_vars:
    print("\n" + "=" * 60, file=sys.stderr)
    print("[X] MISSING REQUIRED ENVIRONMENT VARIABLES", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    for var_msg in missing_vars:
        print(var_msg, file=sys.stderr)
    print("\nFix: Create a .env file in the backend directory with the required variables.", file=sys.stderr)
    print(f"Location: {env_path}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    sys.exit(1)

# Load environment variables
print("=" * 60)
print("[INFO] BACKEND STARTING WITH DEBUG MODE")
print("=" * 60)
print(f"Loaded .env file: {env_path}")
print(f"File exists: {env_path.exists()}")
print(f"[V] DATABASE_URL: ***{os.getenv('DATABASE_URL', 'MISSING')[-20:]}")
print(f"[V] JWT_SECRET: {'*' * 20}")
print(f"[V] CORS_ORIGINS: {os.getenv('CORS_ORIGINS', 'MISSING')}")
print(f"OpenRouter API Key: {os.getenv('OPENAI_API_KEY', 'MISSING')[:30]}...")
print(f"OpenRouter Base URL: {os.getenv('OPENAI_BASE_URL', 'MISSING')}")
print(f"AI Model: {os.getenv('AI_MODEL', 'MISSING')}")
print("=" * 60)


# Create FastAPI application (lifespan added in Phase 5 section below)
app = FastAPI(
    title="Todo App API",
    description="RESTful API for multi-tenant task management with event-driven architecture",
    version="2.0.0",
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
    allow_headers=["Content-Type", "Authorization", "X-User-Id"],
    expose_headers=["Content-Type"],
    max_age=3600,  # Cache preflight requests for 1 hour
)


# =============================================================================
# Phase 4: APScheduler Setup for Recurring Tasks
# =============================================================================

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from contextlib import asynccontextmanager
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

        logger.info(f"[V] Generated {generated_count} recurring task occurrences")

    except Exception as e:
        logger.error(f"[X] Error generating recurring tasks: {e}", exc_info=True)


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
logger.info("[T] APScheduler started - recurring tasks will be generated every hour")

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


# =============================================================================
# Phase 5: Kafka Producer and Metrics Setup
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup/shutdown tasks.
    """
    # Startup
    logger.info("🚀 Starting Phase 5 services...")

    # Initialize Kafka producer (non-blocking, will connect on first use)
    kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
    if kafka_enabled:
        try:
            from ..services.kafka.producer import get_kafka_producer
            producer = await get_kafka_producer()
            logger.info("[V] Kafka producer initialized")
        except Exception as e:
            logger.warning(f"[!] Kafka producer not available: {e}")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Phase 5 services...")
    if kafka_enabled:
        try:
            from ..services.kafka.producer import shutdown_kafka_producer
            await shutdown_kafka_producer()
            logger.info("[V] Kafka producer stopped")
        except Exception as e:
            logger.error(f"Error stopping Kafka producer: {e}")


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
from .routes import categories, chat, health, tasks, subtasks, statistics, tags, attachments, activity

app.include_router(health.router, tags=["Health"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(categories.router, prefix="/api", tags=["Categories"])  # Phase 4: US1
app.include_router(subtasks.router, prefix="/api", tags=["Subtasks"])  # Phase 4: US5
app.include_router(statistics.router, prefix="/api", tags=["Statistics"])  # Phase 4: US6
app.include_router(tags.router, prefix="/api", tags=["Tags"])  # Phase 4: US7
app.include_router(attachments.router, tags=["Attachments"])  # Phase 4: US9
app.include_router(activity.router, tags=["Activity"])  # Phase 4: US10
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


# =============================================================================
# Phase 5: Prometheus Metrics Endpoint
# =============================================================================

@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus exposition format for scraping.
    """
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi.responses import Response

        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        return JSONResponse(
            status_code=501,
            content={"detail": "Prometheus client not installed"}
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
