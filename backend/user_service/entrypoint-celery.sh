#!/bin/bash
set -e

# Перевірка, що DATABASE_URL встановлено
: "${DATABASE_URL:?DATABASE_URL is not set}"

# Розбираємо DATABASE_URL за допомогою Python
DB_HOST=$(python -c "import dj_database_url, os; print(dj_database_url.parse(os.environ['DATABASE_URL'])['HOST'])")
DB_PORT=$(python -c "import dj_database_url, os; print(dj_database_url.parse(os.environ['DATABASE_URL'])['PORT'] or 5432)")
DB_USER=$(python -c "import dj_database_url, os; print(dj_database_url.parse(os.environ['DATABASE_URL'])['USER'])")
DB_NAME=$(python -c "import dj_database_url, os; print(dj_database_url.parse(os.environ['DATABASE_URL'])['NAME'])")

echo "Waiting for database at $DB_HOST:$DB_PORT..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; do
  echo "$(date) - Database is unavailable - sleeping"
  sleep 2
done

echo "Database ready!"

# Якщо Celery потрібно переконатися, що міграції застосовані:
# echo "Ensuring migrations are applied..."
# python manage.py migrate --noinput || true

echo "Starting Celery worker for user-service..."
exec celery -A user_service.celery worker --loglevel=info -Q user_queue,default
