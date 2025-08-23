# /mnt/d/handmade_marketplace/backend/api_gateway/Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]