# API Документація

## 1. Огляд
API маркетплейсу базується на REST з JSON-схемами, об’єднаними через `drf_spectacular`. Усі запити проходять через API Gateway (`http://localhost:8000/api/`), який перенаправляє їх до User Service (`/users/*`) або Product Service (`/products/*`, `/moderation/*`). Схеми генеруються через `fetch_schema.py` і кешуються в Redis.

## 2. Базовий URL
`http://localhost:8000/api/`

## 3. Аутентифікація
- **Метод**: JWT (SimpleJWT) у заголовку:
  ```
  Authorization: Bearer <access_token>
  ```
- **Токени**:
  - `access`: Короткостроковий токен для авторизації.
  - `refresh`: Для оновлення `access`-токена.
- **Чорний список**: Додає `refresh_token` при логауті (POST `/users/logout/`).
- **Логіка** (`LoginSerializer`): Валідація `email`, `password`, перевірка існування користувача (`User.objects.filter(email=email)`), пароля (`check_password`), активності (`is_active`). Повертає `refresh`, `access` через `RefreshToken.for_user`.

## 4. Ендпоінти

### 4.1. API Gateway
- **GET /health**
  - **Опис**: Перевіряє здоров’я API Gateway, Redis, User Service, Product Service, кешованих схем (`user_service_schema`, `product_service_schema`).
  - **Логіка** (`HealthCheckSerializer`, `HealthCheckView`):
    - Перевіряє Redis через `cache.get('health_check_test')`.
    - Запити до `/health` User Service (`http://user-service:8001/health`) та Product Service (`http://product-service:8002/health`) з таймаутом 20с, max 5 спроб, затримка 10с.
    - Перевіряє наявність кешованих схем у Redis.
  - **Відповідь (200)**:
    ```json
    {
      "status": "ok",
      "services": {
        "redis": {"status": "ok"},
        "user_service": {"status": "ok"},
        "product_service": {"status": "ok"},
        "user_service_schema": {"status": "ok"},
        "product_service_schema": {"status": "ok"}
      }
    }
    ```
  - **Відповідь (503)**:
    ```json
    {
      "status": "error",
      "services": {
        "redis": {"status": "error", "detail": "Connection error"},
        ...
      }
    }
    ```
  - **Логування**: Помилки (Redis, таймаути, з’єднання) записуються через логер `app` (рівень `ERROR`).
- **GET /schema**
  - **Опис**: Повертає об’єднану OpenAPI-схему з кешу (`merged_schema`) або генерує нову.
  - **Логіка** (`MergedSchemaView`, `apps.py`):
    - Отримує `user_service_schema`, `product_service_schema` з Redis.
    - Фоновий потік у `apps.py` оновлює схеми кожні 60с (з експоненційною затримкою, max 60с).
    - Генерує власну схему через `SchemaGenerator` (DRF Spectacular).
    - Кешує результат у `merged_schema` (TTL 1 година).
  - **Відповідь**: JSON-схема з шляхами та компонентами.
- **GET /swagger-ui**
  - **Опис**: Інтерфейс Swagger UI для перегляду документації (через `SpectacularSwaggerView`).
- **GET/POST/PUT/DELETE /** (ProxyView)
  - **Опис**: Перенаправляє запити до User Service (`/users/*`) або Product Service (`/products/*`, `/moderation/*`).
  - **Логіка** (`ProxyView`, `ProxyErrorSerializer`):
    - Виключає заголовки `host`, `content-length`, `connection`, `transfer-encoding`.
    - Використовує `requests.request` (таймаут 20с).
    - Повертає JSON (якщо `Content-Type: application/json`) або текст помилки (`ProxyErrorSerializer`).
    - Некоректні шляхи повертають `{"error": "No microservice available for path: <path>"}` (503).
  - **Троттлінг**: `AnonRateThrottle` (1M/день), `UserRateThrottle` (10M/день).

### 4.2. User Service (/users/*)
- **POST /users/register/**
  - **Опис**: Реєстрація користувача з аватаром (опціонально).
  - **Тіло (multipart/form-data або JSON)**:
    ```json
    {
      "email": "string",
      "username": "string",
      "surname": "string",
      "password": "string",
      "password_confirm": "string"
    }
    ```
  - **Відповідь (201)**: `{"success": true}`.
- **GET /users/verify-email/{uidb64}/{token}/**
  - **Опис**: Підтвердження email.
  - **Відповідь (200)**: `{"success": true}`.
- **POST /users/resend-verification/**
  - **Опис**: Повторне надсилання верифікаційного листа (троттлінг 1/хв).
  - **Тіло**: `{"email": "string"}`.
  - **Відповідь (200)**: `{"success": true}`.
- **POST /users/login/**
  - **Опис**: Логін, повертає токени.
  - **Тіло**:
    ```json
    {"email": "string", "password": "string"}
    ```
  - **Відповідь (200)**:
    ```json
    {"refresh": "string", "access": "string", "user": {...}}
    ```
- **POST /users/token/refresh/**
  - **Опис**: Оновлення access-токена.
  - **Тіло**: `{"refresh": "string"}`.
  - **Відповідь**: `{"access": "string"}`.
- **POST /users/password-reset/**
  - **Опис**: Запит на скидання пароля.
  - **Тіло**: `{"email": "string"}`.
  - **Відповідь (200)**: `{"success": true}`.
- **POST /users/password-reset-confirm/{uidb64}/{token}/**
  - **Опис**: Підтвердження нового пароля.
  - **Тіло**:
    ```json
    {"new_password": "string", "password_confirm": "string"}
    ```
  - **Відповідь (200)**: `{"success": true}`.
- **GET/PATCH /users/profile/**
  - **Опис**: Профіль (JWT).
  - **Відповідь (GET)**: Дані користувача.
  - **Тіло (PATCH)**: Оновлені поля.
  - **Відповідь (PATCH)**: Оновлені дані.
- **POST /users/logout/**
  - **Опис**: Логаут, додає refresh до чорного списку.
  - **Тіло**: `{"refresh_token": "string"}`.
  - **Відповідь (205)**: `{"success": true}`.
- **GET /users/users-list/**
  - **Опис**: Список користувачів (адмін, пагінація, фільтри).
  - **Параметри**: `?email=string&username=string&roles=user&is_verified=true&created_after=YYYY-MM-DD`
  - **Відповідь**:
    ```json
    {
      "success": true,
      "count": int,
      "next": "url",
      "prev": "url",
      "results": [{...}, ...]
    }
    ```
- **GET/PUT/PATCH/DELETE /users/users-list/{id}/**
  - **Опис**: Деталі/оновлення/видалення користувача (адмін).
  - **Відповідь (GET)**: Дані користувача.
  - **Відповідь (PUT/PATCH)**: Оновлені дані.
  - **Відповідь (DELETE, 204)**: Без тіла.
- **GET /users/health/**
  - **Опис**: Перевірка здоров’я (Redis, PostgreSQL).
  - **Відповідь (200)**:
    ```json
    {
      "status": "ok",
      "services": {
        "redis": {"status": "ok"},
        "database": {"status": "ok"}
      }
    }
    ```

### 4.3. Product Service (/products/*, /moderation/*)
- **GET /products/**
  - **Опис**: Список продуктів (схвалені, `stock > 0`, фільтри).
  - **Параметри**: `?category=id&min_price=float&max_price=float&sale_type=fixed|auction&is_approved=true`
  - **Відповідь**: Список продуктів з `discount_percentage`.
- **POST /products/**
  - **Опис**: Створення продукту (vendor_id = user.id, `is_approved=False`).
  - **Тіло**: Поля продукту (`name`, `description`, `price`, `discount_price`, `sale_type`, `stock`, `category_id`).
  - **Відповідь (201)**: Створений продукт.
- **GET/PUT/PATCH/DELETE /products/{id}/**
  - **Опис**: Деталі/оновлення/видалення продукту (власник або адмін).
  - **Відповідь (GET)**: Дані продукту.
  - **Відповідь (PUT/PATCH)**: Оновлені дані.
  - **Відповідь (DELETE, 204)**: Без тіла.
- **POST /products/{id}/upload-image/**
  - **Опис**: Завантаження зображення (асинхронно через Celery, max 32MB, JPG/PNG/GIF).
  - **Тіло**: `image` (файл).
  - **Відповідь (201)**: `{"image_url": "string"}`.
- **POST /moderation/approve/**
  - **Опис**: Схвалення/відхилення продукту або відгуку (адмін).
  - **Тіло**:
    ```json
    {"content_type": "product"|"review", "content_id": int, "is_approved": true|false}
    ```
  - **Дія**: Надсилає нотифікацію через `send_moderation_notification` (Celery).
  - **Відповідь (200)**: `{"success": true}`.
- **GET /products/health/**
  - **Опис**: Перевірка здоров’я (Redis, PostgreSQL).
  - **Відповідь (200)**:
    ```json
    {
      "status": "ok",
      "services": {
        "redis": {"status": "ok"},
        "database": {"status": "ok"}
      }
    }
    ```

## 5. Маршрутизація
- **Логіка** (`ProxyView`):
  - `/users/*` -> `http://user-service:8001`.
  - `/products/*`, `/moderation/*` -> `http://product-service:8002`.
  - Некоректні шляхи: `{"error": "No microservice available for path: <path>"}` (503, `ProxyErrorSerializer`).
- **Заголовки**: Виключаються `host`, `content-length`, `connection`, `transfer-encoding`.
- **Таймаут**: 20с, обробка помилок з’єднання/таймауту.

## 6. Схеми
- **Генерація**: Через `fetch_schema.py` (команда `python manage.py fetch_schema`):
  - Запити до `http://user-service:8001/schema/` та `http://product-service:8002/schema/`.
  - Max 5 спроб, затримка 10с, таймаут 20с.
  - Зберігання у `user_service_schema.json`, `product_service_schema.json`.
- **Фонова синхронізація** (`apps.py`):
  - Потік `background_schema_loader` оновлює `user_service_schema`, `product_service_schema` в Redis кожні 60с (з експоненційною затримкою).
- **Кеш**: Redis (`merged_schema`, TTL 1 година).

## 7. Обмеження
- **Троттлінг** (REST_FRAMEWORK, `settings.py`):
  - `AnonRateThrottle`: 1,000,000/день.
  - `UserRateThrottle`: 10,000,000/день.
- **Email-запити**: 1/хвилина (Redis, User Service).