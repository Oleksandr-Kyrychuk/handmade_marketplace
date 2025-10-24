# Документація User Service

## 1. Огляд
User Service відповідає за управління користувачами, автентифікацію, верифікацію email, скидання пароля, профілі та адмін-функціонал у маркетплейсі Handmade Marketplace. Працює як мікросервіс, доступний через API Gateway (`http://localhost:8000/api/users/*`).

## 2. Основні функції
- **Реєстрація**: Створення користувача з валідацією пароля (мін. 12 символів, велика літера, цифра, спецсимвол), завантаженням аватара (Cloudinary, max 5MB, PNG/JPEG). Викликає `send_verification_email` через Celery.
- **Автентифікація**: JWT-токени (`access`, `refresh`) через `rest_framework_simplejwt`. Чорний список для логауту.
- **Верифікація email**: Лист з токеном (TTL 1 година), повторне надсилання (троттлінг: 1/хв).
- **Скидання пароля**: Запит через email, підтвердження з токеном через Celery.
- **Профіль користувача**: Перегляд/оновлення `username`, `surname`, `avatar`, `email`.
- **Управління користувачами**: Для адмінів — список, деталі, оновлення, видалення з фільтрами (`email`, `username`, `roles`, `is_verified`, `created_after/before`).
- **Асинхронні задачі** (Celery):
  - `delete_unverified_users`: Видаляє не верифікованих після 24 годин.
  - `send_verification_email`: Верифікаційний лист (троттлінг: 1/хв).
  - `send_password_reset_email`: Лист для скидання пароля.
- **Логування**: Маскування `password`, `email`, `token` через `SensitiveDataFilter`.
- **Здоров’я**: `/health` перевіряє Redis і PostgreSQL.

## 3. Структура
- **Моделі** (`models.py`):
  - `User` (розширення `AbstractUser`):
    - Поля: `id` (UUID, PK), `email` (унікальний, `USERNAME_FIELD`), `username`, `surname`, `avatar` (CloudinaryField), `roles` (ArrayField: `user`, `admin`), `is_verified`, `verification_token_created_at`, `search_vector` (GinIndex).
    - Валідатори: `name_validator` (лише літери, дефіс не на початку/кінці).
    - Signal: `post_save` оновлює `search_vector` (username A, surname B).
    - Менеджер: `CustomUserManager`.
- **Серійалізатори** (`serializers.py`):
  - `LoginSerializer`: Валідація `email`, `password`, `is_active`. Повертає `refresh`, `access`, дані користувача.
  - `RegisterSerializer`: Валідація `email`, `username`, `surname`, `password` (мін. 12, велика літера, цифра, спецсимвол), `avatar` (max 5MB).
  - Інші: `UserSerializer`, `PasswordResetRequestSerializer`, `PasswordResetConfirmSerializer`, `ResendVerificationCodeSerializer`, `UserProfileSerializer`, `HealthCheckSerializer`, `VerifyEmailSerializer`.
- **Views** (`views.py`):
  - `RegisterView` (POST `/register/`): Створює користувача, викликає `send_verification_email`.
  - `VerifyEmailView` (GET `/verify-email/{uidb64}/{token}/`): Підтверджує email.
  - `ResendVerificationCodeView` (POST `/resend-verification/`): Повторне надсилання.
  - `LoginView` (POST `/login/`): Повертає токени.
  - `CustomTokenRefreshView` (POST `/token/refresh/`): Оновлює токен.
  - `PasswordResetRequestView` (POST `/password-reset/`): Запит скидання пароля.
  - `PasswordResetConfirmView` (POST `/password-reset-confirm/{uidb64}/{token}/`): Новий пароль.
  - `UserProfileView` (GET/PATCH `/profile/`): Профіль користувача.
  - `LogoutView` (POST `/logout/`): Чорний список `refresh_token`.
  - `UserViewSet` (CRUD `/users-list/`): Для адмінів, пагінація (50/сторінка).
  - `HealthCheckView` (GET `/health/`): Redis, PostgreSQL.
- **Permissions** (`permissions.py`):
  - `HasRolePermission`: Перевірка ролей (`allowed_roles`), ownership (obj == request.user).
- **Фільтри** (`filters.py`):
  - `UserFilter`: `email` (icontains), `username` (icontains), `roles`, `is_verified`, `created_after/before`.
- **Tasks** (`tasks.py`):
  - `delete_unverified_users`: Видаляє після 24 годин.
  - `send_verification_email`: Лист з URL (троттлінг 1/хв).
  - `send_password_reset_email`: Аналогічно.
- **Log Filters** (`log_filters.py`):
  - `SensitiveDataFilter`: Маскує `password`, `email`, `token`.
- **URLs** (`urls.py`): Ендпоінти + Swagger.

## 4. Інтеграції
- **Cloudinary**: Аватар (max 5MB, PNG/JPEG, дані приховані).
- **Redis**: Кеш, троттлінг (1/хв), Celery (`REDIS_URL=redis://***HIDDEN***:***HIDDEN***@marketplace_redis:6379/0`).
- **PostgreSQL**: `users_schema`, `search_vector` (GinIndex), `unaccent`, `pg_trgm`.
- **SMTP**: Дані приховані.

## 5. Запуск
- **Docker**:
  - Сервіс: `make user` (`docker-compose.local.yml`).
  - Порт: 8001.
  - Залежності: `marketplace-database`, `redis`.
  - `Dockerfile.local`: Python 3.11-slim, `postgresql-client`.
  - `entrypoint.sh`: Чекає БД (`pg_isready`), створює `users_schema`, міграції, Gunicorn (2 workers/threads).
  - `entrypoint-celery.sh`: Celery worker (-Q default).
- **Міграції**:
  ```bash
  make migrate-user
  ```
- **Суперкористувач**:
  ```bash
  make super-user
  ```
- **Healthcheck**:
  - `curl --fail http://user-service:8001/health` (10с, таймаут 20с, 10 спроб).

## 6. Безпека
- **Валідація**:
  - Пароль: Мін. 12 символів, велика літера, цифра, спецсимвол.
  - Імена: Без дефісів на початку/кінці.
  - Аватар: Max 5MB, PNG/JPEG.
- **Троттлінг**: Email 1/хв (Redis), anon 1M/день, user 10M/день.
- **Permissions**: `HasRolePermission` для ролей, ownership.
- **Логи**: Маскування через `SensitiveDataFilter`.
- **JWT**: Чорний список для `refresh_token`.

## 7. Тестування
- **Запуск**: `./manage.py test`
- **Модулі**:
  - `test_models.py`: Створення користувача, `name_validator`, `search_vector`.
  - `test_serializers.py`: Валідація `RegisterSerializer`, `LoginSerializer`.
  - `test_views.py`: CRUD, верифікація, healthcheck.
  - `test_permissions.py`: `HasRolePermission` для ролей, ownership.
- **Покриття**: ~90% для моделей, серійалізаторів, views.
- **Приклад**:
  ```python
  class RegisterSerializerTest(APITestCase):
      def test_valid_data(self):
          data = {
              'email': '***HIDDEN***',
              'username': 'TestUser',
              'surname': 'TestSurname',
              'password': 'Password123!@#',
              'password_confirm': 'Password123!@#'
          }
          serializer = RegisterSerializer(data=data)
          self.assertTrue(serializer.is_valid())
  ```

## 8. Edge Cases
- Невалідний email: 400, `"email": ["Enter a valid email address."]`.
- Неактивний користувач: 400, `"error": "Користувач не активний"`.
- Верифікований email: 400, `"email": ["Email вже підтверджений."]`.
- Прострочений токен: 400, `"error": "Invalid token"`.
- Невалідний аватар: 400, `"Розмір зображення не повинен перевищувати 5MB."`.

## 9. Troubleshooting
- **Redis connection refused**:
  - Перевірте `REDIS_URL` у `.env.local`.
  - Логи: `docker-compose logs redis`.
  - Перезапустіть: `docker-compose restart redis`.
- **Celery задача не виконується**:
  - Логи: `docker-compose logs user-service-celery`.
  - Перевірте `CELERY_BROKER_URL`.
  - Перезапустіть: `make user`.
- **Міграції не застосовуються**:
  - Перевірте `entrypoint.sh` (створення `users_schema`).
  - Виконайте `make migrate-user`.
- **SMTP помилка**:
  - Перевірте SMTP налаштування.
  - Тест: `send_mail('Test', 'Test', '***HIDDEN***', ['***HIDDEN***'])`.

## 10. Взаємодія з фронтендом
- **POST /users/register/**:
  ```typescript
  const formData = new FormData();
  formData.append('email', '***HIDDEN***');
  formData.append('username', 'TestUser');
  formData.append('surname', 'TestSurname');
  formData.append('password', 'Password123!@#');
  formData.append('password_confirm', 'Password123!@#');
  const response = await api.post('/users/register/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  ```
- **Обробка помилок**:
  - 400: `"Validation error"`.
  - 429: `"Занадто багато запитів"`.
  - 503: `"Сервіс недоступний"`.