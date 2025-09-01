#!/bin/sh
echo "Applying migrations..."
python manage.py migrate

echo "Initializing user_service schema..."
python manage.py fetch_schema

echo "Starting Gunicorn..."
PORT=${PORT:-8000}
exec gunicorn --bind 0.0.0.0:$PORT app.wsgi:application --workers 2 --threads 2
