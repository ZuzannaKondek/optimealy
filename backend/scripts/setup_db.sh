#!/bin/bash
# Convenience script to set up and seed the database
# Usage: ./scripts/setup_db.sh

set -e

echo "=========================================="
echo "🍽️  OptiMeal Database Setup"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start database
echo ""
echo "📦 Starting PostgreSQL..."
docker compose up -d db

# Wait for database to be healthy
echo ""
echo "⏳ Waiting for database to be ready..."
until docker compose exec -T db pg_isready -U optimeal_user -d optimeal_db > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo " ✅ Database is ready!"

# Run migrations
echo ""
echo "🔄 Running migrations..."
docker compose exec backend alembic upgrade head || {
    echo "⚠️  No migrations to run (this is OK for first setup)"
}

# Run seed
echo ""
echo "🌱 Seeding database..."
docker compose exec backend python scripts/run_seed.py

echo ""
echo "=========================================="
echo "✅ Database setup complete!"
echo "=========================================="
