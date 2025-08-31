#!/bin/sh
echo "Applying migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
PORT=${PORT:-8001}  # Порт 8001 для user_service
exec gunicorn --bind 0.0.0.0:$PORT user_service.wsgi:application --workers 2 --threads 2