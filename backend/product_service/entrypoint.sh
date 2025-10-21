#!/bin/sh
set -e

echo "Waiting for database..."
# Замінено dbshell на pg_isready
until pg_isready -h marketplace-database -p 5432 -U dev -d marketplace; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database ready!"

echo "Creating products_schema if not exists..."
# Створюємо products_schema
python manage.py dbshell <<EOF
CREATE SCHEMA IF NOT EXISTS products_schema;
GRANT ALL ON SCHEMA products_schema TO dev;
ALTER SCHEMA products_schema OWNER TO dev;
EOF

echo "Applying migrations for products app..."
# Мігруємо тільки products app
python manage.py migrate products --noinput

# Запускаємо Gunicorn
PORT=${PORT:-8002}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT product_service.wsgi:application --workers 2 --threads 2