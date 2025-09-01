# user_service/entrypoint.sh
#!/bin/bash
set -e

echo "Creating schema if not exists..."
psql "$DATABASE_URL" -c "CREATE SCHEMA IF NOT EXISTS users_schema; GRANT ALL ON SCHEMA users_schema TO dev;"

echo "Applying migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
PORT=${PORT:-8001}
gunicorn --bind 0.0.0.0:$PORT user_service.wsgi:application --workers 2 --threads 2 &

echo "Starting Celery worker..."
celery -A user_service worker --loglevel=info --uid=nobody