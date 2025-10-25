# Документація Product Service

## 1. Огляд
Product Service управляє продуктами, категоріями, зображеннями, відгуками та модерацією в маркетплейсі Handmade Marketplace. Доступний через API Gateway (`http://localhost:8000/api/products/*`, `/moderation/*`).

## 2. Основні функції
- **Продукти**: CRUD-операції, типи продажів (`fixed`, `auction`), знижки (`discount_price`), управління запасами (`stock`), автоматична модерація. Функціонал забезпечує контроль запасів для уникнення перепродажу, знижки для стимулювання продажів.
- **Категорії**: Ієрархічна структура, `slug` для URL, зображення (Cloudinary), повнотекстовий пошук (`search_vector`, розширення `unaccent`, `pg_trgm`). Ієрархія полегшує навігацію, пошук оптимізує запити для користувачів.
- **Зображення**: Асинхронне завантаження через Celery до Cloudinary (max 32MB, JPG/PNG/GIF). Обмеження розміру захищає від перевантаження, асинхронність покращує продуктивність.
- **Відгуки**: Створення, модерація, рейтинг (0-5), інтеграція з User Service для даних користувача. Рейтинг впливає на довіру, модерація запобігає спаму.
- **Модерація**:
  - **Автоматична**: Перевірка тексту (`name`, `description`, `comment`) на токсичність через зовнішній сервіс (`/moderate`). Забезпечує швидкий фільтр шкідливого контенту.
  - **Ручна**: Схвалення/відхилення продуктів і відгуків адмінами. Доповнює автоматичну для точності.
- **Фільтри**: Пошук за категорією, ціною, типом продажу, статусом схвалення (`is_approved`). Фільтри спрощують пошук для користувачів.
- **Пошук**: Повнотекстовий за `name`, `description` (українська мова, `search_vector` з GinIndex). Підтримує релевантність пошуку.
- **Асинхронні задачі** (Celery):
  - `upload_image_to_cloudinary`: Завантаження зображень з повторними спробами. Викликається після створення продукту, результат зберігається в моделі `ProductImage`.
  - `send_moderation_notification`: Нотифікації про модерацію через User Service. Надсилається після схвалення/відхилення для інформування власника.
  - `moderate_content`: Автоматична перевірка тексту. Запускається при створенні, оновлює `is_approved`.
- **Здоров’я**: Ендпоінт `/health` для перевірки Redis і PostgreSQL. Перевіряє з'єднання для моніторингу.

## 3. Структура
- **Моделі** (`models.py`):
  - `Category`: `id` (PK), `name`, `parent_id` (FK, ієрархія), `category_image` (Cloudinary), `category_href` (slug), `search_vector` (GinIndex). `parent_id` підтримує дерева категорій.
  - `Product`: `id` (PK), `vendor_id` (FK до `users_user`), `category_id` (FK), `name`, `description`, `price`, `discount_price`, `sale_type` (enum: `fixed`, `auction`), `stock`, `is_approved` (bool), `search_vector` (GinIndex). `is_approved` блокує показ до модерації.
  - `ProductImage`: `id` (PK), `product_id` (FK), `user_id` (FK), `image_url`, `image` (Cloudinary). Зв'язок з продуктом для множинних зображень.
  - `Review`: `id` (PK), `product_id` (FK), `user_id` (FK), `rating` (0-5), `comment`, `created_at`, `is_approved` (bool). `is_approved` для модерації відгуків.
- **Серійалізатори** (`serializers.py`):
  - Продукти: Розрахунок `discount_percentage`, валідація `price`, `stock`. Валідація забезпечує позитивні значення.
  - Категорії: Ієрархічна структура, `category_href`. Підтримує рекурсію для дерев.
  - Зображення: `image_url`, валідація розміру (max 32MB) і формату (JPG/PNG/GIF). Обмеження запобігає помилкам завантаження.
  - Відгуки: `rating`, `comment`, інтеграція з User Service для `user_id`. Інтеграція отримує дані користувача.
- **Views** (`views.py`):
  - `ProductViewSet` (GET/POST/PUT/PATCH/DELETE `/products/`, `/products/{id}/`): CRUD, фільтрація через `ProductFilter`, перевірка ownership (`vendor_id`). Власник може редагувати тільки свої продукти.
  - `ModerationViewSet` (POST `/moderation/approve/`): Схвалення/відхилення продуктів або відгуків (адмін). Викликає `send_moderation_notification`.
  - `HealthCheckView` (GET `/products/health/`): Перевірка Redis і PostgreSQL. Повертає статус сервісів.
- **Permissions** (`permissions.py`):
  - `HasRolePermission`: Перевірка ролей (`user`, `admin`) та `vendor_id`. Обмежує доступ до власних даних.
  - `ReviewPermission`: Обмеження на створення/редагування відгуків (власник або адмін). Запобігає фальсифікаціям.
- **Фільтри** (`filters.py`):
  - `ProductFilter`: Фільтрація за `category`, `min_price`, `max_price`, `sale_type`, `is_approved`. Використовує django_filters.
- **Tasks** (`tasks.py`):
  - `upload_image_to_cloudinary`: Асинхронне завантаження зображень. Повторні спроби для надійності.
  - `send_moderation_notification`: Нотифікації через User Service. Інформує про зміни статусу.
  - `moderate_content`: Перевірка тексту через `/moderate`. Оновлює статус автоматично.
- **URLs** (`urls.py`): Ендпоінти для всіх views, інтеграція зі Swagger.
- **Settings** (`settings.py`):
  - Django, DRF, Celery (`CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`).
  - Cloudinary (дані приховані).
  - Логування з маскуванням чутливих даних.

## 4. Інтеграції
- **Cloudinary**: Завантаження зображень продуктів/категорій (max 32MB, JPG/PNG/GIF, дані приховані).
- **User Service**: Запити для отримання даних користувача (`user_id`) та надсилання нотифікацій (`http://user-service:8001`).
- **Зовнішній сервіс модерації**: Перевірка тексту на токсичність (`/moderate`).
- **Redis**: Черги Celery (`images`, `moderation`, `auto_moderation`, `REDIS_URL=redis://***HIDDEN***:***HIDDEN***@marketplace_redis:6379/0`).
- **PostgreSQL**: Схема `products_schema` (створюється через `init.sql`), `search_vector` (GinIndex), розширення `unaccent`, `pg_trgm`.

## 5. Запуск
- **Docker**:
  - Сервіс: `make product` (запускає `product-service` і `product-service-celery`, `docker-compose.local.yml`). Залежить від `marketplace-database` і `redis`.
  - Порт: 8002.
  - Залежності: `marketplace-database` (PostgreSQL), `redis`.
  - Dockerfile: `Dockerfile.local` (Python 3.12, встановлення `postgresql-client`, `curl`, `requirements.txt`).
- **Міграції**:
  ```bash
  make migrate-product
  ```
- **Суперкористувач**:
  ```bash
  make super-product
  ```
- **Заповнення продуктів і категорій**:
  ```bash
  make seed-product
  ```
- **Очищення продуктів і категорій**:
  ```bash
  make flush-product
  ```
  

- **Healthcheck**:
  - Команда: `curl --fail http://product-service:8002/health`.
  - Інтервал: 10с, таймаут: 20с, 10 спроб, період запуску: 120с.

## 6. Безпека
- **Permissions**:
  - `HasRolePermission`: Доступ до продуктів за `vendor_id` або роллю `admin`. Захищає від несанкціонованого редагування.
  - `ReviewPermission`: Обмеження на відгуки. Забезпечує аутентичність.
- **Валідація**:
  - Зображення: Max 32MB, формати JPG/PNG/GIF. Запобігає вразливостям.
  - Ціни: Позитивні значення.
  - Stock: Нецелое значення >= 0.
- **Модерація**:
  - Автоматична: Перевірка тексту на токсичність. Захищає від шкідливого контенту.
  - Ручна: Схвалення/відхилення адмінами. Додає контроль.
- **Логи**: Маскування чутливих даних через `SensitiveDataFilter`.