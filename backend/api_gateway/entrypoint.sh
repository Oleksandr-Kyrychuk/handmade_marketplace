#!/bin/sh
echo "Waiting for database..."
# Витягуємо хост, порт і користувача з DATABASE_URL
DB_HOST=$(echo $DATABASE_URL | sed -E 's/.*@([^:/]+).*/\1/')
DB_PORT=$(echo $DATABASE_URL | sed -E 's/.*:([0-9]+)\/.*/\1/')
DB_USER=$(echo $DATABASE_URL | sed -E 's/.*:\/\/([^:]+):.*/\1/')
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    sleep 1
done
echo "Database is ready!"

echo "Applying migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
# Використовуємо PORT, якщо він визначений, або 8000 за замовчуванням
PORT=${PORT:-8000}
exec gunicorn --bind 0.0.0.0:$PORT app.wsgi:application --workers 2 --threads 2