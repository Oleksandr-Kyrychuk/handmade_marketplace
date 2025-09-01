FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y postgresql-client
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput

ENV PYTHONUNBUFFERED=1
CMD ["sh", "entrypoint.sh"]