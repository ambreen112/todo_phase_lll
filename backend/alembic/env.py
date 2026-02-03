"""Alembic migration environment configuration."""

import os
import sys
import logging
from sqlalchemy import create_engine
from alembic import context
from sqlmodel import SQLModel

# Add the src directory to path for model imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import all models to register them with SQLModel.metadata
from models import User, Task, Conversation, ChatMessage  # noqa: E402, F401

# Alembic Config object
config = context.config

# Minimal logging to avoid KeyError
logging.basicConfig(level=logging.INFO)

# Read DATABASE_URL from environment
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Set sqlalchemy.url at runtime
config.set_main_option("sqlalchemy.url", database_url)

# Target metadata for 'autogenerate'
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations() -> None:
    """Run migrations in 'online' mode."""
    url = config.get_main_option("sqlalchemy.url")
    # Ensure URL uses postgresql+psycopg:// for psycopg3
    if "postgresql://" in url and "postgresql+psycopg://" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://")
    engine = create_engine(url, echo=False)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations()
