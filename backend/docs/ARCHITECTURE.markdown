# Архітектура проекту Handmade Marketplace

## 1. Огляд системи
Handmade Marketplace реалізує мікросервісну архітектуру з трьома компонентами:
- **API Gateway**: Єдина точка входу, перенаправляє запити до User Service (`/users/*`) або Product Service (`/products/*`, `/moderation/*`). Генерує OpenAPI-схеми через `drf_spectacular`, кешує їх у Redis (`fetch_schema.py`, `apps.py`).
- **User Service**: Управління користувачами, автентифікація (JWT), верифікація email, скидання пароля, профілі, адмін-функції.
- **Product Service**: Управління продуктами, категоріями, зображеннями, відгуками, автоматична та ручна модерація.

**База даних**: PostgreSQL 17 з ізольованими схемами (`gateway_schema`, `users_schema`, `products_schema`, `init.sql`), розширеннями `uuid-ossp`, `unaccent`, `pg_trgm` (`init-extensions.sql`).
**Асинхронні задачі**: Celery з Redis 7.4 як брокером і backend (`REDIS_URL=redis://***HIDDEN***:***HIDDEN***@marketplace_redis:6379/0`).
**Логи**: Django logging з маскуванням чутливих даних (`password`, `email`, `token`).

## 2. Компоненти системи

### 2.1. API Gateway
- **Функціонал**:
  - Перенаправлення запитів через `ProxyView` до User Service (`http://user-service:8001`) або Product Service (`http://product-service:8002`).
  - Об’єднання OpenAPI-схем через `MergedSchemaView`, кешування в Redis (`merged_schema`, TTL 1 година).
  - Перевірка здоров’я через `HealthCheckView` (Redis, User/Product Service, схеми).
  - Фонова синхронізація схем через `background_schema_loader` (`apps.py`).
- **Технології**: Django, DRF, `drf_spectacular`, Redis, Gunicorn (2 воркери, 2 потоки, `entrypoint.sh`), Python 3.12 (`Dockerfile.local`).
- **Схема БД**: `gateway_schema` (створюється через `init.sql`, `entrypoint.sh`).
- **Кешування**: Redis (`redis://***HIDDEN***:***HIDDEN***@marketplace_redis:6379/0`) для `user_service_schema`, `product_service_schema`, `merged_schema`.
- **Логи**: У `api_gateway/logs/api_gateway.log`, формат `[timestamp] level name message`, рівень `DEBUG`.
- **Особливості**:
  - Фоновий потік (`apps.py`) оновлює схеми кожні 60с (з експоненційною затримкою, max 60с).
  - Троттлінг: `AnonRateThrottle` (1M/день), `UserRateThrottle` (10M/день).
  - CORS: `http://localhost:5173`, `http://localhost:3000` (`.env.local`).
  - **Кешування HTTP-відповідей** (GET):  
        - **Ключ: `gateway:response:{md5(path+query)}`**  
        - **TTL: 60 секунд**  
        - **Тільки 200 OK, JSON**  
        - **Реалізовано в `ProxyView.dispatch()`**

### 2.2. User Service
- **Функціонал**:
  - Реєстрація, логін (через `LoginSerializer`), верифікація email, скидання пароля, профіль. Реєстрація викликає `send_verification_email` через Celery для підтвердження.
  - Управління користувачами (адмін): список, деталі, оновлення, видалення.
  - Асинхронні задачі: `delete_unverified_users`, `send_verification_email`, `send_password_reset_email`. `delete_unverified_users` очищає базу від не верифікованих після 24 годин.
- **Моделі**:
  - `User` (розширення `AbstractUser`): `id` (UUID), `email` (унікальний, `USERNAME_FIELD`), `username`, `surname`, `avatar` (Cloudinary), `roles` (ArrayField: `user`, `admin`), `is_verified`, `verification_token_created_at`, `search_vector` (GinIndex). `is_verified` блокує доступ до функцій до підтвердження.
- **Серійалізатори**:
  - `LoginSerializer`: Валідація `email`, `password`, `is_active`, повертає `refresh`, `access`.
  - Реєстрація: Валідація `password` (мін. 12 символів, велика літера, цифра, спецсимвол), `username`, `surname`, `avatar`.
  - Профіль, скидання пароля, список користувачів.
- **Views**:
  - `RegisterView`, `VerifyEmailView`, `ResendVerificationCodeView`, `LoginView`, `PasswordResetRequestView`, `PasswordResetConfirmView`, `UserProfileView`, `LogoutView`, `UserViewSet`, `HealthCheckView`.
- **Permissions**:
  - `HasRolePermission`: Перевірка ролей та ownership.
- **Фільтри**:
  - `UserFilter`: `email`, `username`, `roles`, `is_verified`, `created_after/before`.
- **Tasks** (Celery):
  - `delete_unverified_users`: Видаляє не верифікованих (24 години).
  - `send_verification_email`: Верифікаційний лист (троттлінг: 1/хв).
  - `send_password_reset_email`: Лист для скидання пароля.
- **Логи**: `user_service/logs`, маскування через `SensitiveDataFilter`.
- **Інтеграції**:
  - Cloudinary: Аватари (max 5MB, PNG/JPEG).
  - Redis: Кеш, троттлінг, Celery.
  - PostgreSQL: `users_schema`.
  - SMTP: Email.

### 2.3. Product Service
- **Функціонал**:
  - Управління продуктами, категоріями, зображеннями, відгуками, модерація. Створення продукту викликає `moderate_content` для перевірки.
  - Асинхронні задачі: `upload_image_to_cloudinary`, `send_moderation_notification`, `moderate_content`. `upload_image_to_cloudinary` обробляє зображення асинхронно.
- **Моделі**:
  - `Category`: `id`, `name`, `parent_id`, `category_image` (Cloudinary), `category_href` (slug), `search_vector`.
  - `Product`: `id`, `vendor_id`, `category_id`, `name`, `description`, `price`, `discount_price`, `sale_type` (fixed/auction), `stock`, `is_approved`, `search_vector`.
  - `ProductImage`: `id`, `product_id`, `user_id`, `image_url`, `image` (Cloudinary).
  - `Review`: `id`, `product_id`, `user_id`, `rating` (0-5), `comment`, `created_at`, `is_approved`.
- **Серійалізатори**:
  - Продукти: Розрахунок `discount_percentage`.
  - Категорії, зображення, відгуки (з інтеграцією User Service).
- **Views**:
  - `ProductViewSet`: CRUD, фільтри через `ProductFilter`.
  - `ModerationViewSet`: Схвалення/відхилення.
  - `HealthCheckView`: Redis, PostgreSQL.
- **Permissions**:
  - `HasRolePermission`: Перевірка `vendor_id`, ролей.
  - `ReviewPermission`: Обмеження на відгуки.
- **Фільтри**:
  - `ProductFilter`: `category`, `min_price`, `max_price`, `sale_type`, `is_approved`.
- **Tasks** (Celery):
  - `upload_image_to_cloudinary`: Завантаження зображень.
  - `send_moderation_notification`: Нотифікації через User Service.
  - `moderate_content`: Перевірка тексту.
- **Інтеграції**:
  - Cloudinary: Зображення (max 32MB).
  - User Service: Дані користувача, нотифікації.
  - Зовнішній сервіс: Модерація (`/moderate`).
  - Redis: Черги `images`, `moderation`, `auto_moderation`.
  - PostgreSQL: `products_schema`, `search_vector`, `unaccent`, `pg_trgm`.
- **Логи**: `product_service/logs`, маскування чутливих даних.

### 2.4. Frontend
- **Проект**: `handmade-marketplace-client` (Next.js, TypeScript).
- **Компоненти**: `shared`, `widgets`, API-утиліти (`shared/api`), локалізація (`i18n`).

## 3. Технологічний стек
- **Backend**: Python 3.12, Django, DRF, Celery, PostgreSQL 17, Redis 7.4, `drf_spectacular`, `django-cors-headers`, `rest_framework_simplejwt`, `django_celery_beat`, Cloudinary.
- **Frontend**: Next.js, TypeScript, ESLärgint, PostCSS.
- **Інфраструктура**: Docker, Docker Compose, Gunicorn, `postgresql-client`, `curl`.

## 4. Схема бази даних
- **gateway_schema**: Для API Gateway (метадані, кешовані схеми, `init.sql`).
- **users_schema**:
  - `users_user`: `id` (UUID, PK), `email` (unique), `username`, `surname`, `avatar`, `roles` (array), `is_verified`, `verification_token_created_at`, `search_vector` (GinIndex).
- **products_schema**:
  - `products_category`: `id`, `name`, `parent_id`, `category_image`, `category_href`, `search_vector` (GinIndex).
  - `products_product`: `id`, `vendor_id`, `category_id`, `name`, `description`, `price`, `discount_price`, `sale_type`, `stock`, `is_approved`, `search_vector` (GinIndex).
  - `products_productimage`: `id`, `product_id`, `user_id`, `image_url`, `image`.
  - `products_review`: `id`, `product_id`, `user_id`, `rating`, `comment`, `created_at`, `is_approved`.

## 5. Комунікація
- **API Gateway**:
  - Перенаправлення через `ProxyView`:
    - `/users/*` -> `http://user-service:8001`.
    - `/products/*`, `/moderation/*` -> `http://product-service:8002`.
  - Таймаут: 20с, обробка помилок (503, `ProxyErrorSerializer`).
- **Celery**:
  - Redis (`redis://***HIDDEN***:***HIDDEN***@marketplace_redis:6379/0`) для задач:
    - User Service: `delete_unverified_users`, `send_verification_email`, `send_password_reset_email`.
    - Product Service: `upload_image_to_cloudinary`, `send_moderation_notification`, `moderate_content`.
- **Логи**: Django logging, файли/консоль, маскування чутливих даних.
- **Кешування**: Redis для OpenAPI-схем (TTL 1 година), троттлінгу email.
- ### Кеш (Redis)
- **Спільний Redis**: `redis://redis:6379/1`
- **Префікси ключів**:
  - `user:` — User Service
  - `product:` — Product Service
  - `gateway:` — API Gateway
- **Типи кешу**:
  1. **Swagger Cache** (вже є)
  2. **Data Cache** (профілі, продукти)
  3. **Response Cache** (Gateway)

## 6. Здоров’я сервісів
- **Ендпоінт /health**:
  - API Gateway: Перевіряє Redis, User Service, Product Service, кешовані схеми (`HealthCheckSerializer`).
  - User/Product Service: Перевіряє Redis, PostgreSQL.
  - Відповідь: `{"status": "ok"|"error", "services": {...}}` (200/503).