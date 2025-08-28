#!/bin/bash
set -e

# Function to handle shutdown
shutdown() {
    echo "Shutting down gracefully..."
    exit 0
}

trap shutdown SIGTERM SIGINT

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for Redis
echo "Waiting for Redis..."
while ! redis-cli -h redis ping > /dev/null 2>&1; do
  sleep 1
done
echo "Redis is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
exec uvicorn chat_store.main:app --host 0.0.0.0 --port 8000