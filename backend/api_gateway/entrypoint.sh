#!/bin/sh
echo "Creating gateway_schema if not exists..."
python manage.py dbshell <<EOF
CREATE SCHEMA IF NOT EXISTS gateway_schema;
EOF

echo "Applying migrations..."
python manage.py migrate

echo "Initializing api_gateway schema..."
python manage.py fetch_schema

echo "Starting Gunicorn..."
PORT=${PORT:-8000}
exec gunicorn --bind 0.0.0.0:$PORT app.wsgi:application --workers 2 --threads 2