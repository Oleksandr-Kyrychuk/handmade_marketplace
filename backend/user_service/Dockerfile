FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y postgresql-client netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Додаємо Celery (якщо використовується в user-service)
RUN pip install --no-cache-dir celery redis

COPY . .
RUN python manage.py collectstatic --noinput || true

ENV PYTHONUNBUFFERED=1
CMD ["sh", "entrypoint.sh"]