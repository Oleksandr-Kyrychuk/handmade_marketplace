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

echo "Creating orders_schema if not exists..."
python manage.py dbshell <<EOF
CREATE SCHEMA IF NOT EXISTS orders_schema;
GRANT ALL ON SCHEMA orders_schema TO $DB_USER;
ALTER SCHEMA orders_schema OWNER TO $DB_USER;
EOF

echo "Making migrations for orders app..."
python manage.py makemigrations orders --noinput

echo "Applying migrations for orders app..."
python manage.py migrate orders --noinput

PORT=${PORT:-8003}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT order_service.wsgi:application --workers 2 --threads 2