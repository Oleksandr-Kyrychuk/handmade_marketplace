# Handmade Marketplace

Маркетплейс для handmade товарів з мікросервісною архітектурою, який дозволяє користувачам купувати та продавати унікальні вироби ручної роботи.

## Особливості
- **Мікросервіси**:
  - **API Gateway**: Єдина точка входу, перенаправляє запити до User Service (`/users/*`) та Product Service (`/products/*`, `/moderation/*`). Використовує `drf_spectacular` для генерації OpenAPI-схем, кешування в Redis (`merged_schema`, TTL 1 година). Фоновий потік у `apps.py` періодично оновлює схеми.
  - **User Service**: Управління користувачами, автентифікація (JWT), верифікація email, скидання пароля, профіль, адмін-функції.
  - **Product Service**: Управління продуктами, категоріями, зображеннями, відгуками, автоматична та ручна модерація.
- **Backend**:
  - Django + Django REST Framework (DRF) для REST API.
  - Celery для асинхронних задач (email, модерація, завантаження зображень) з Redis як брокером.
  - Логування з маскуванням чутливих даних (`password`, `email`, `token`) через `SensitiveDataFilter`.
- **База даних**:
  - PostgreSQL 17 з окремими схемами: `gateway_schema`, `users_schema`, `products_schema`.
  - Розширення: `uuid-ossp` (UUID), `unaccent`, `pg_trgm` (пошук, `init-extensions.sql`).
  - Використання `search_vector` з GinIndex для повнотекстового пошуку.
- **Frontend**:
  - Next.js з TypeScript, модульні UI-компоненти (`shared`, `widgets`).
  - Локалізація через `i18n`.
  - API-запити через `shared/api` до `http://localhost:8000/api/`.
- **Інфраструктура**:
  - Docker Compose для локального та продакшн розгортання (`Dockerfile.local`, `docker-compose.local.yml`).
  - Redis 7.4 для кешування (`merged_schema`, троттлінг) та черг Celery.
  - Gunicorn для API Gateway (2 воркери, 2 потоки, `entrypoint.sh`).
- **API Gateway**:
  - Генерація OpenAPI-схем через `drf_spectacular` та `fetch_schema.py` (зберігання у `user_service_schema.json`, `product_service_schema.json`).
  - Підтримка CORS для фронтенду (`http://localhost:5173`, `http://localhost:3000`).
  - Троттлінг: 1M/день для анонімних, 10M/день для авторизованих (`settings.py`).

## Вимоги
- Docker & Docker Compose
- Node.js >= 18
- Python >= 3.12
- PostgreSQL >= 17
- Redis >= 7.4
- Додаткові пакети: `postgresql-client`, `curl` (`Dockerfile.local`)

## Швидкий старт (локально)
1. Клонуйте репозиторій:
   ```bash
   git clone <repo-url>
   cd handmade_marketplace
   ```
2. Запустіть усі сервіси (API Gateway, User Service, Product Service, PostgreSQL, Redis):
   ```bash
   cd backend
   make up
   ```
   - Будує образи без кешу (`Dockerfile.local`, `docker-compose.local.yml`).
   - Встановлює залежності з `requirements.txt` (`pip install --no-cache-dir`).
   - Запускає контейнери: `api-gateway`, `user-service`, `user-service-celery`, `product-service`, `product-service-celery`, `marketplace-database`, `redis`.
   - Ініціалізує схему `gateway_schema` через `entrypoint.sh`.
   - Виконує міграції (`python manage.py migrate`) та завантажує схеми (`fetch_schema.py`).
   - Чекає 10 секунд для стабільного запуску (`Makefile`).
3. Запустіть frontend:
   ```bash
   cd ../frontend/handmade-marketplace-client
   npm install
   npm run dev
   ```
4. Доступ:
   - API Gateway: `http://localhost:8000` (Gunicorn, порт 8000)
   - User Service: `http://localhost:8001`
   - Product Service: `http://localhost:8002`
   - Frontend: `http://localhost:3000`
   - PostgreSQL: `localhost:5432` (user: `***HIDDEN***`, pass: `***HIDDEN***`, `.env.local`)
   - Redis: `localhost:6379`
5. Ініціалізація бази даних:
   - Скрипти: `infrastructure/postgres/init-extensions.sql` (`unaccent`, `pg_trgm`), `init.sql` (користувач `***HIDDEN***`, схеми `gateway_schema`, `users_schema`, `products_schema`).
   - Міграції:
     ```bash
     make migrate-user
     make migrate-product
     ```
6. Створення суперкористувача:
   ```bash
   make super-user  # User Service
   make super-product  # Product Service
   ```

## Тестування
- **Backend**:
  - У папках `api_gateway`, `user_service`, `product_service`:
    ```bash
    ./manage.py test
    ```
  - Тести для моделей, серійалізаторів (`HealthCheckSerializer`, `ProxyErrorSerializer`, `EmptySerializer`), view, permissions.
- **Frontend**:
  - У папці `frontend/handmade-marketplace-client`:
    ```bash
    npm run test
    ```
  - Тести для компонентів (`shared`, `widgets`) та API-утиліти (`shared/api`).

## Управління сервісами
- **Запуск окремих сервісів**:
   ```bash
   make gate  # API Gateway
   make user  # User Service + Celery
   make product  # Product Service + Celery
   ```
- **Перегляд логів**:
   ```bash
   make logs
   ```
   - Логи: `api_gateway/logs`, `user_service/logs`, `product_service/logs`.
   - Формат: `[timestamp] level name message`.
- **Створення міграцій**:
   ```bash
   make makemigrations-user
   make makemigrations-product
   ```
- **Застосування міграцій**:
   ```bash
   make migrate-user
   make migrate-product
   ```

- **Заповнення списку користувачів**:
  ```bash
  make seed-user
  ```
- **Очищення списку користувачі**:
  ```bash
  make flush-user
  ```


- **Заповнення продуктів і категорій**:
  ```bash
  make seed-product
  ```
- **Очищення продуктів і категорій**:
  ```bash
  make flush-product
  ```


## Ліцензія
MIT (див. `LICENSE` у корені репозиторію).


