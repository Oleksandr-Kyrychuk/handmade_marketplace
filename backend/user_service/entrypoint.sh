#!/bin/sh
set -e

echo "Waiting for database..."
until pg_isready -h marketplace-database -p 5432 -U dev -d marketplace; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database ready!"

echo "Creating users_schema if not exists..."
# Use dbshell for schema creation (as in your original)
python manage.py dbshell <<EOF
CREATE SCHEMA IF NOT EXISTS users_schema;
GRANT ALL ON SCHEMA users_schema TO dev;
ALTER SCHEMA users_schema OWNER TO dev;
EOF

# Alternative: If you prefer using create_schema.py (but it's redundant here)
# python create_schema.py

echo "Making migrations for all apps (including users)..."
python manage.py makemigrations --noinput

echo "Applying migrations for all apps..."
python manage.py migrate --noinput

# Optional: Collect static files if your app uses them
# python manage.py collectstatic --noinput

# Optional: Create superuser if not exists (e.g., for admin access)
# echo "Creating superuser if not exists..."
# python manage.py createsuperuser --noinput --email admin@example.com --username admin --surname Admin || true

PORT=${PORT:-8001}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT user_service.wsgi:application --workers 2 --threads 2