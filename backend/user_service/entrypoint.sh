#!/bin/sh user-service
echo "Creating users_schema if not exists..."
python manage.py dbshell <<EOF
CREATE SCHEMA IF NOT EXISTS users_schema;
EOF

echo "Applying migrations for users app..."
python manage.py migrate users

echo "Applying migrations for other apps..."
python manage.py migrate

echo "Starting Gunicorn..."
PORT=${PORT:-8001}
exec gunicorn --bind 0.0.0.0:$PORT user_service.wsgi:application --workers 2 --threads 2
