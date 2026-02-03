#!/usr/bin/env python3
"""Run manual PostgreSQL migration to change tags column from VARCHAR(50)[] to TEXT[]."""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables")
    sys.exit(1)

print(f"Connecting to database...")
print(f"Database URL: {DATABASE_URL[:50]}...")

try:
    # Parse connection parameters
    # Remove the query parameters for psycopg2
    if '?' in DATABASE_URL:
        db_url_without_params = DATABASE_URL.split('?')[0]
    else:
        db_url_without_params = DATABASE_URL

    # Connect to PostgreSQL
    conn = psycopg2.connect(db_url_without_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    print("Connected successfully!")

    # 1. Check current column type
    print("\n1. Checking current column type...")
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'task' AND column_name = 'tags'
    """)
    current_type = cursor.fetchone()
    if current_type:
        print(f"   Current: {current_type}")
    else:
        print("   Error: 'tags' column not found in 'task' table")
        sys.exit(1)

    # 2. Check if column exists and is already TEXT[]
    cursor.execute("SELECT pg_typeof(tags) FROM task LIMIT 1")
    current_pg_type = cursor.fetchone()
    print(f"   PostgreSQL type: {current_pg_type[0] if current_pg_type else 'Unknown'}")

    # 3. Run the migration
    print("\n2. Running migration...")
    migration_sql = """
    ALTER TABLE task
    ALTER COLUMN tags
    TYPE TEXT[]
    USING tags::TEXT[];
    """

    try:
        cursor.execute(migration_sql)
        print("   ✓ Migration executed successfully")
    except Exception as e:
        print(f"   ✗ Migration failed: {e}")
        print("   Trying alternative approach...")

        # Alternative: try without USING clause
        migration_sql_alt = "ALTER TABLE task ALTER COLUMN tags TYPE TEXT[];"
        try:
            cursor.execute(migration_sql_alt)
            print("   ✓ Alternative migration executed successfully")
        except Exception as e2:
            print(f"   ✗ Alternative migration also failed: {e2}")
            print("\n   You may need to manually check constraints:")
            print("   1. Check if column has NOT NULL constraint: ALTER TABLE task ALTER COLUMN tags DROP NOT NULL;")
            print("   2. Check if column has DEFAULT value: ALTER TABLE task ALTER COLUMN tags DROP DEFAULT;")
            print("   3. Then retry the ALTER TYPE command.")
            sys.exit(1)

    # 4. Verify the change
    print("\n3. Verifying migration...")
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'task' AND column_name = 'tags'
    """)
    new_type = cursor.fetchone()
    if new_type:
        print(f"   New type: {new_type}")
        if new_type[1] == 'ARRAY' and new_type[2] is None:
            print("   ✓ Successfully changed to TEXT[]")
        else:
            print("   ⚠ Type may not be TEXT[] as expected")

    # Verify PostgreSQL type
    cursor.execute("SELECT pg_typeof(tags) FROM task LIMIT 1")
    new_pg_type = cursor.fetchone()
    print(f"   PostgreSQL type: {new_pg_type[0] if new_pg_type else 'Unknown'}")

    # Test with some sample data
    print("\n4. Testing array operations...")
    try:
        cursor.execute("SELECT id, title, tags FROM task WHERE tags IS NOT NULL LIMIT 3")
        sample_rows = cursor.fetchall()
        if sample_rows:
            print(f"   Found {len(sample_rows)} tasks with tags")
            for task_id, title, tags in sample_rows:
                print(f"   - Task '{title[:30]}...': tags = {tags}")
        else:
            print("   No tasks with tags found")

        # Test array overlap query
        cursor.execute("""
            SELECT COUNT(*) FROM task
            WHERE tags && ARRAY['test-tag-12345']::TEXT[]
        """)
        test_count = cursor.fetchone()[0]
        print(f"   Test query executed successfully: {test_count} rows match test tag")

    except Exception as e:
        print(f"   ⚠ Test query failed: {e}")
        print("   This might be expected if there's no data or different error")

    cursor.close()
    conn.close()
    print("\n✅ Migration completed successfully!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check database connection: psql 'DATABASE_URL'")
    print("2. Check if 'task' table exists")
    print("3. Check if 'tags' column exists in 'task' table")
    print("4. Check current type: \\d task")
    sys.exit(1)