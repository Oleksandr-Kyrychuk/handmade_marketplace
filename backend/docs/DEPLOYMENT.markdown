# Розгортання

## 1. Огляд
Проект розгортається через Docker Compose для локального середовища.
- **API Gateway**: Gunicorn (2 воркери, 2 потоки, `entrypoint.sh`)
- **Асинхронні задачі**: Celery через Redis
- **Логи**: файли (`api_gateway/logs`, `user_service/logs`, `product_service/logs`) та консоль

## 2. Локальне розгортання

### Вимоги
- Docker, Docker Compose  
- Node.js >= 18  
- Python >= 3.12  
- PostgreSQL >= 17  
- Redis >= 7.4  
- `postgresql-client`, `curl`

### Запуск backend
```bash
cd backend
make up
```
- Будує образи без кешу (`Dockerfile.local`, `docker-compose.local.yml`)  
- Встановлює залежності (`pip install --no-cache-dir`)  
- Запускає контейнери: `api-gateway`, `user-service`, `user-service-celery`, `product-service`, `product-service-celery`, `marketplace-database`, `redis`  
- Ініціалізує схему `gateway_schema` через `entrypoint.sh`  
- Виконує міграції та завантажує схеми (`fetch_schema.py`)  
- Чекає 10 секунд для стабільного запуску

Окремі сервіси:
```bash
make gate     # API Gateway
make user     # User Service + Celery
make product  # Product Service + Celery
```

### Запуск frontend
```bash
cd ../frontend/handmade-marketplace-client
npm install
npm run dev
```

### Доступ
- API Gateway: `http://localhost:8000`  
- User Service: `http://localhost:8001`  
- Product Service: `http://localhost:8002`  
- Frontend: `http://localhost:3000`  
- PostgreSQL: `localhost:5432` (user: `***HIDDEN***`, pass: `***HIDDEN***`)  
- Redis: `localhost:6379`

## 3. Продакшн розгортання

### Змінні середовища
| Змінна | Значення |
|--------|----------|
| `SECRET_KEY` | `***HIDDEN***` |
| `DATABASE_URL` | `postgresql://***HIDDEN***:***HIDDEN***@marketplace-database:5432/marketplace` |
| `REDIS_URL` | `redis://***HIDDEN***:***HIDDEN***@marketplace_redis:6379/0` |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:3000` |
| User Service | SMTP дані приховані |
| Product Service | Cloudinary API дані приховані |

### Запуск backend
```bash
cd backend
docker-compose -f docker-compose.yml up --build -d
```

### Запуск frontend
```bash
cd ../frontend/handmade-marketplace-client
npm install
npm run build
npm run start
```

## 4. Ініціалізація бази даних

### Скрипти
- `init-extensions.sql`: розширення `unaccent`, `pg_trgm`  
- `init.sql`: створює користувача `***HIDDEN***`, базу `marketplace`, схеми `gateway_schema`, `users_schema`, `products_schema`, надає права

### Міграції
```bash
make migrate-user
make migrate-product
```

### Суперкористувач
```bash
make super-user      # User Service
make super-product   # Product Service
```

## 5. Налаштування сервісів

### API Gateway
- Gunicorn: 2 воркери, 2 потоки, порт 8000  
- Схеми: генерація через `fetch_schema.py`, кеш у Redis (`merged_schema`, TTL 1 година)  
- CORS: `http://localhost:5173`, `http://localhost:3000`  
- Healthcheck: `curl --fail http://api-gateway:8000/health`

### User Service
- Порт: 8001  
- Celery: через `entrypoint-celery.sh`  
- Email: SMTP дані приховані  
- Cloudinary: аватар (max 5MB, PNG/JPEG)  
- Healthcheck: `curl --fail http://user-service:8001/health`

### Product Service
- Порт: 8002  
- Celery: черги `images`, `moderation`, `auto_moderation`  
- Cloudinary: зображення (max 32MB, JPG/PNG/GIF)  
- Модерація: зовнішній сервіс `/moderate`  
- Healthcheck: `curl --fail http://product-service:8002/health`

### Redis
- Порт: 6379  
- Healthcheck: `redis-cli ping`

### PostgreSQL
- Порт: 5432  
- Healthcheck: `pg_isready -U ***HIDDEN*** -d marketplace`

## 6. Логи
- Backend: `api_gateway/logs`, `user_service/logs`, `product_service/logs`  
- Формат: `[timestamp] level name message`  
- Фільтр: маскування `password`, `email`, `token`  
- Frontend: консоль браузера  
- Перегляд логів:
```bash
make logs
```

## 7. Моніторинг
- Healthchecks API Gateway, User Service, Product Service
- Celery: логи задач (`tasks.py`)  
- Docker:
```bash
make ps
```