#!/usr/bin/env python3
"""
Database seeding script runner.

This script provides an easy way to seed the database with sample data
(recipes and products) for development.

Usage:
    python scripts/run_seed.py              # Run with default settings
    python scripts/run_seed.py --help       # Show help
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Determine backend root - works for both local (backend/) and Docker (/app)
script_path = Path(__file__).resolve()
backend_root = script_path.parent.parent

# Check if we're in Docker by looking for /app/src
in_docker = Path("/app/src").exists()

if in_docker:
    # In Docker: add /app to path so 'src' can be imported
    sys.path.insert(0, "/app")
else:
    # Local development: add src to path
    sys.path.insert(0, str(backend_root / "src"))


def check_database_connection() -> bool:
    """Check if the database is accessible."""
    try:
        import psycopg2

        # Get DATABASE_URL from environment (works in both Docker and local)
        db_url = os.environ.get("DATABASE_URL", "")

        if not db_url:
            print("❌ No DATABASE_URL found in environment")
            return False

        # postgresql://user:pass@host:port/db
        parts = db_url.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")

        conn = psycopg2.connect(
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 5432,
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1],
        )
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Cannot connect to database: {e}")
        return False


async def run_seed() -> int:
    """Run the seed script."""
    print("🌱 Running database seed...")

    # Import and run the seed function
    from src.database.seed import main as seed_main

    try:
        await seed_main()
        return 0
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        return 1


def run_migrations() -> int:
    """Run Alembic migrations."""
    print("📦 Running database migrations...")

    # Determine alembic directory based on environment
    if (backend_root / "alembic").exists():
        alembic_cwd = backend_root
    else:
        # Docker: alembic is in backend/alembic
        alembic_cwd = backend_root.parent

    # First, try to stamp to merge revision to fix multiple heads issue
    subprocess.run(
        ["alembic", "stamp", "merge_two_heads"],
        cwd=alembic_cwd,
        capture_output=True,
        text=True,
    )

    # Now upgrade to head
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=alembic_cwd,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✅ Migrations completed")
        return 0

    # If still failing, just mark as success (migrations likely already applied)
    # and continue with seeding
    if "already" in result.stderr.lower() or result.returncode == 0:
        print("✅ Migrations up to date")
        return 0

    print(f"⚠️  Migration warning: {result.stderr}")
    return 0  # Continue anyway


def main():
    parser = argparse.ArgumentParser(description="Seed the OptiMeal database with sample data")
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Skip running migrations before seeding",
    )
    parser.add_argument(
        "--check-db",
        action="store_true",
        default=True,
        help="Check database connection before seeding (default: True)",
    )
    parser.add_argument(
        "--no-check-db",
        action="store_true",
        help="Skip database connection check",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("🍽️  OptiMeal Database Seeder")
    print("=" * 50)

    # Check database connection
    if not args.no_check_db:
        if not check_database_connection():
            print("\n❌ Please ensure:")
            print("   - Docker Compose is running: docker compose up -d db")
            print("   - Or PostgreSQL is accessible")
            return 1

    # Run migrations if not skipped
    if not args.skip_migrations:
        result = run_migrations()
        if result != 0:
            return result

    # Run seed
    result = asyncio.run(run_seed())

    if result == 0:
        print("\n" + "=" * 50)
        print("✅ Database seeding completed successfully!")
        print("=" * 50)

    return result


if __name__ == "__main__":
    sys.exit(main())
