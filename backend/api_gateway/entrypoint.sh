#!/bin/sh
set -e

: "${DATABASE_URL:?DATABASE_URL is not set}"

DB_HOST=$(python -c "import dj_database_url, os; print(dj_database_url.parse(os.environ['DATABASE_URL'])['HOST'])")
DB_PORT=$(python -c "import dj_database_url, os; print(dj_database_url.parse(os.environ['DATABASE_URL'])['PORT'] or 5432)")
DB_USER=$(python -c "import dj_database_url, os; print(dj_database_url.parse(os.environ['DATABASE_URL'])['USER'])")
DB_NAME=$(python -c "import dj_database_url, os; print(dj_database_url.parse(os.environ['DATABASE_URL'])['NAME'])")

echo "Waiting for database at $DB_HOST:$DB_PORT..."
until printf '.' && nc -z $DB_HOST $DB_PORT; do
    echo "$(date) - waiting for database..."
    sleep 2
done
echo "Database ready!"
68

echo "Database ready!"

echo "Creating gateway_schema if not exists..."
python manage.py dbshell <<EOF
CREATE SCHEMA IF NOT EXISTS gateway_schema;
GRANT ALL ON SCHEMA gateway_schema TO $DB_USER;
ALTER SCHEMA gateway_schema OWNER TO $DB_USER;
EOF

echo "Fixing possible inconsistent migration history..."
python manage.py migrate --fake-initial || true

echo "Applying migrations..."
python manage.py migrate

echo "Initializing api_gateway schema..."
python manage.py fetch_schema || echo "Failed to fetch schema, continuing..."

PORT=${PORT:-8000}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT app.wsgi:application --workers 2 --threads 2