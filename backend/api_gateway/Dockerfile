FROM python:3.12-slim

# Встановлюємо postgresql-client + netcat (альтернатива pg_isready)
RUN apt-get update && \
    apt-get install -y postgresql-client netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копіюємо тільки requirements спочатку (для кешування)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код
COPY . .

# Статичні файли (якщо є)
RUN python manage.py collectstatic --noinput || true

ENV PYTHONUNBUFFERED=1
CMD ["sh", "entrypoint.sh"]