#!/usr/bin/env python3
"""Run Alembic migrations with .env loading."""

import os
import sys

# Load .env file manually
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip("'\"")
    print(f"Loaded .env from {env_path}")
else:
    print(f".env file not found at {env_path}")
    sys.exit(1)

# Now run alembic
from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic.ini")

# First stamp the database with current head (002) since tables already exist
print("Stamping database with current revision (002)...")
command.stamp(alembic_cfg, "002")
print("Database stamped successfully!")

# Then run any pending migrations (should be none if stamped correctly)
print("Running migrations...")
command.upgrade(alembic_cfg, "head")
print("Migration completed successfully!")
