#!/bin/sh
set -e

echo "DEBUG: Starting entrypoint.sh"

echo "Waiting for database..."
until pg_isready -h marketplace-database -p 5432 -U dev -d marketplace; do
  echo "Database is unavailable - sleeping"
  sleep 2
done
echo "Database ready!"

echo "DEBUG: Creating orders_schema if not exists..."
python manage.py dbshell <<EOF
CREATE SCHEMA IF NOT EXISTS orders_schema;
GRANT ALL ON SCHEMA orders_schema TO dev;
ALTER SCHEMA orders_schema OWNER TO dev;
EOF

echo "DEBUG: Making migrations for orders app..."
python manage.py makemigrations orders --noinput

echo "DEBUG: Applying migrations for orders app..."
python manage.py migrate orders --noinput

PORT=${PORT:-8003}
echo "DEBUG: Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT order_service.wsgi:application --workers 2 --threads 2
