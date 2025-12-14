"""Database session management with Neon PostgreSQL."""

from sqlmodel import Session, create_engine
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine with Neon PostgreSQL optimizations
# pool_pre_ping: Verify connections before using (prevents stale connections)
# pool_recycle: Recycle connections after 300 seconds (5 minutes)
# pool_size: Number of connections to maintain
# max_overflow: Maximum overflow connections beyond pool_size
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connection health before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=5,         # Maintain 5 connections in pool
    max_overflow=10      # Allow up to 10 overflow connections
)


def get_session():
    """Get database session.

    Yields:
        Session: SQLModel session for database operations
    """
    with Session(engine) as session:
        yield session
