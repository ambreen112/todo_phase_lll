#!/usr/bin/env python3
"""Helper script to list user IDs from the database for MCP configuration."""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
load_dotenv()

from sqlmodel import Session, select, create_engine
from models.user import User


def get_database_url() -> str:
    """Get database URL from environment."""
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise ValueError("DATABASE_URL environment variable is required")
    if "postgresql://" in url and "postgresql+psycopg://" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://")
    return url


def main():
    """List all users and their IDs."""
    engine = create_engine(get_database_url(), echo=False, pool_pre_ping=True)

    with Session(engine) as session:
        users = session.exec(select(User)).all()

        if not users:
            print("No users found in the database.")
            print("\nTo create a user, register via the frontend or API:")
            print("  POST /api/auth/register")
            print('  Body: {"email": "user@example.com", "password": "yourpassword", "name": "Your Name"}')
            return

        print("Users in database:")
        print("-" * 80)
        for user in users:
            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Name: {user.name}")
            print("-" * 80)

        print(f"\nTo configure MCP, set MCP_USER_ID to one of the IDs above.")
        print(f"Example: MCP_USER_ID={users[0].id}")


if __name__ == "__main__":
    main()
