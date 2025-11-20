#order_service
#!/bin/bash
echo "Waiting for database..."
until pg_isready -h marketplace-database -p 5432 -U dev -d marketplace; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database ready!"
echo "Starting Celery worker for order-service..."
exec celery -A order_service.celery worker --loglevel=info
