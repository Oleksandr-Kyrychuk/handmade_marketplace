#!/bin/bash
set -e

echo "Waiting for database..."
until pg_isready -h marketplace-database -p 5432 -U dev -d marketplace; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database ready!"

# No need for makemigrations/migrate here—main service handles it.
# But if Celery needs to ensure migrations are applied (rare), add:
# echo "Ensuring migrations are applied..."
# python manage.py migrate --noinput || true  # '|| true' to not fail if already applied

echo "Starting Celery worker for user-service..."
exec celery -A user_service.celery worker --loglevel=info -Q default