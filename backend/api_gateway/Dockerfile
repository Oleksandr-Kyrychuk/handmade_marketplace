# /mnt/d/handmade_marketplace/backend/api_gateway/Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Збір статичних файлів для Render
RUN python manage.py collectstatic --noinput

ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app.wsgi:application"]