#!/bin/sh
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

echo "Creating users_schema if not exists..."
python manage.py dbshell <<EOF
CREATE SCHEMA IF NOT EXISTS users_schema;
GRANT ALL ON SCHEMA users_schema TO $DB_USER;
ALTER SCHEMA users_schema OWNER TO $DB_USER;
EOF

echo "Making migrations for all apps..."
python manage.py makemigrations --noinput

echo "Applying migrations for all apps..."
python manage.py migrate --noinput

# Optional: Collect static files
# python manage.py collectstatic --noinput

# Optional: Create superuser
# python manage.py createsuperuser --noinput --email admin@example.com --username admin --surname Admin || true

PORT=${PORT:-8001}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT user_service.wsgi:application --workers 2 --threads 2
