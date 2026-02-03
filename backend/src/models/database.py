"""Database connection and session management."""

from sqlmodel import SQLModel, create_engine, Session
from ..core.config import get_settings
import socket


def get_engine():
    """Create database engine from settings."""
    settings = get_settings()
    # Use psycopg3 driver for Neon
    url = settings.database_url
    if "postgresql://" in url and "postgresql+psycopg://" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://")

    return create_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def get_session():
    """Get a database session."""
    engine = get_engine()
    with Session(engine) as session:
        yield session


def init_db():
    """Initialize database tables."""
    settings = get_settings()
    # Check if database URL is valid before connecting
    if not settings.database_url:
        print("WARNING: No database URL configured, skipping DB init")
        return

    try:
        engine = get_engine()
        with engine.connect() as conn:
            SQLModel.metadata.create_all(engine)
        print("Database initialized successfully")
    except Exception as e:
        print(f"WARNING: Database initialization failed: {e}")
        print("Server will continue without database connectivity")
