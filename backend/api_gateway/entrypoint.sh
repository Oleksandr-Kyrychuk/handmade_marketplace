#!/bin/sh
echo "Waiting for database..."
while ! pg_isready -h marketplace_database -p 5432 -U postgres; do
    sleep 1
done
echo "Database is ready!"

echo "Applying migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 app.wsgi:application --workers 2 --threads 2