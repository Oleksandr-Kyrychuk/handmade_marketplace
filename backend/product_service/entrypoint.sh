#!/bin/sh
set -e

: "${DATABASE_URL:?DATABASE_URL is not set}"

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

echo "Creating products_schema if not exists..."
python manage.py dbshell <<EOF
CREATE SCHEMA IF NOT EXISTS products_schema;
GRANT ALL ON SCHEMA products_schema TO $DB_USER;
ALTER SCHEMA products_schema OWNER TO $DB_USER;
EOF

echo "Fixing possible inconsistent migration history..."
python manage.py migrate --fake-initial || true

echo "Making migrations for products app..."
python manage.py makemigrations products --noinput

echo "Applying migrations for products app..."
python manage.py migrate products --noinput

# Додано: автоматичний collectstatic перед запуском сервера
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

PORT=${PORT:-8002}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT product_service.wsgi:application --workers 2 --threads 2