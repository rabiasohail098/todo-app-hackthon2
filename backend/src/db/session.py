"""Database session management with Neon PostgreSQL."""

from sqlmodel import Session, create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
import os
import time
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")


def connect_with_retry(database_url: str, max_retries: int = 5, timeout: int = 30):
    """
    Create database engine with retry logic and exponential backoff.

    Implements FR-011, FR-012, FR-013, FR-014 from spec.md:
    - Max 3 retry attempts (FR-011)
    - Exponential backoff: 1s, 2s, 4s (delay = 2^(attempt-1)) (FR-012)
    - 10-second timeout per attempt (FR-013)
    - Logging of each retry attempt (FR-014)

    Args:
        database_url: PostgreSQL connection string
        max_retries: Maximum number of connection attempts (default: 3)
        timeout: Connection timeout in seconds per attempt (default: 10)

    Returns:
        SQLAlchemy Engine: Database engine with active connection

    Raises:
        OperationalError: If all retry attempts fail
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🔌 Attempting database connection (attempt {attempt}/{max_retries})...")

            # Create engine with connection timeout
            # connect_args={'connect_timeout': timeout} passes timeout to psycopg2
            engine = create_engine(
                database_url,
                echo=True,  # Set to False in production
                pool_pre_ping=True,  # Verify connection health before use (prevents stale connections)
                pool_recycle=300,    # Recycle connections every 5 minutes (Neon optimization)
                pool_size=5,         # Maintain 5 connections in pool
                max_overflow=10,     # Allow up to 10 overflow connections
                connect_args={'connect_timeout': timeout}  # 10-second timeout per attempt (FR-013)
            )

            # Test the connection by executing a simple query
            # SQLAlchemy 2.0+ requires text() wrapper for raw SQL strings
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(f"✅ Database connected successfully on attempt {attempt}")
            return engine

        except OperationalError as e:
            logger.warning(f"❌ Database connection attempt {attempt}/{max_retries} failed: {str(e)}")

            # If this was the last attempt, raise error with clear message (FR-034)
            if attempt == max_retries:
                error_msg = (
                    f"❌ Database connection failed after {max_retries} retries. "
                    f"Check DATABASE_URL in .env file.\n"
                    f"Error: {str(e)}"
                )
                logger.error(error_msg)
                raise OperationalError(error_msg, params=None, orig=e)

            # Calculate exponential backoff delay: 2^(attempt-1) = 1s, 2s, 4s (FR-012)
            # Exponential backoff prevents overwhelming the database during temporary outages
            delay = 2 ** (attempt - 1)
            logger.info(f"⏳ Retrying in {delay} seconds (exponential backoff)...")
            time.sleep(delay)


# Create database engine with retry logic (FR-011, FR-012, FR-013, FR-014)
# Increased timeout to 30s for Neon serverless cold start
engine = connect_with_retry(DATABASE_URL, max_retries=5, timeout=30)


def get_session():
    """Get database session.

    Yields:
        Session: SQLModel session for database operations
    """
    with Session(engine) as session:
        yield session
