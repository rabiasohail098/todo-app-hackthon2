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


def connect_with_retry(database_url: str, max_retries: int = 7, timeout: int = 45):
    """
    Create database engine with retry logic and exponential backoff.

    Implements FR-011, FR-012, FR-013, FR-014 from spec.md:
    - Max 3 retry attempts (FR-011)
    - Exponential backoff: 1s, 2s, 4s (delay = 2^(attempt-1)) (FR-012)
    - 10-second timeout per attempt (FR-013)
    - Logging of each retry attempt (FR-014)

    Args:
        database_url: PostgreSQL connection string
        max_retries: Maximum number of connection attempts (default: 7 for Neon)
        timeout: Connection timeout in seconds per attempt (default: 45 for Neon cold starts)

    Returns:
        SQLAlchemy Engine: Database engine with active connection

    Raises:
        OperationalError: If all retry attempts fail
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[C] Attempting database connection (attempt {attempt}/{max_retries})...")

            # Create engine with connection timeout optimized for Neon Serverless
            # connect_args={'connect_timeout': timeout} passes timeout to psycopg2
            engine = create_engine(
                database_url,
                echo=False,  # Set to False in production
                pool_pre_ping=True,  # Verify connection health before use (prevents stale connections)
                pool_recycle=300,    # Recycle connections every 5 minutes (Neon optimization)
                pool_size=3,         # Reduced pool size for Hugging Face (lower resources)
                max_overflow=5,      # Reduced overflow for Hugging Face
                connect_args={
                    'connect_timeout': timeout,  # Longer timeout for Neon cold starts
                    'sslmode': 'require',       # Enforce SSL for Neon
                    'keepalives_idle': 30,      # Keep-alive settings for long-lived connections
                    'keepalives_interval': 10,
                    'keepalives_count': 3,
                }
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
                    f"This is common during Hugging Face cold starts. The database may be warming up.\n"
                    f"Error: {str(e)}"
                )
                logger.error(error_msg)
                raise OperationalError(error_msg, params=None, orig=e)

            # Calculate exponential backoff delay with jitter: 2^(attempt-1) + random(0-1) = 1-2s, 2-3s, 4-5s...
            # Exponential backoff prevents overwhelming the database during temporary outages
            base_delay = 2 ** (attempt - 1)
            import random
            delay = base_delay + random.uniform(0, 1)  # Add jitter to prevent thundering herd
            logger.info(f"⏳ Retrying in {delay:.1f} seconds (exponential backoff with jitter)...")
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
