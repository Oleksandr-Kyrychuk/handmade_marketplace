#!/bin/sh
set -e

echo "Waiting for database..."
# Замінено dbshell на pg_isready для надійнішого чекання
until pg_isready -h marketplace-database -p 5432 -U dev -d marketplace; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database ready!"

echo "Creating users_schema if not exists..."
# Створюємо users_schema і надаємо права
python manage.py dbshell <<EOF
CREATE SCHEMA IF NOT EXISTS users_schema;
GRANT ALL ON SCHEMA users_schema TO dev;
ALTER SCHEMA users_schema OWNER TO dev;
EOF

echo "Applying migrations for users app..."
# Мігруємо тільки users app
python manage.py migrate users --noinput

echo "Applying migrations for other apps..."
# Мігруємо загальні Django apps
python manage.py migrate --noinput

# Запускаємо Gunicorn
PORT=${PORT:-8001}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT user_service.wsgi:application --workers 2 --threads 2