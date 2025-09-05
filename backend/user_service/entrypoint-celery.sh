#!/bin/sh
echo "Starting Celery worker..."
exec celery -A user_service worker --loglevel=info --uid=nobody