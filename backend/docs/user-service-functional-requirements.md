# Функціональні Вимоги до User Service  
**Версія 1.2 — Поточний стан на 20 листопада 2025**  
**Статус: Production-Ready (≈ 82–85% від Enterprise-рівня)**

> **Мета** — Безпечне, масштабоване, асинхронне та enterprise-ready керування користувачами для Handmade Marketplace  
> **Технології** — Django 4+, DRF, SimpleJWT + blacklist, Celery + Redis, PostgreSQL (users_schema), Cloudinary, drf-spectacular, django-filter, django-environ

### Легенда
- [x] — реалізовано та працює в продакшні  
- [~] — частково реалізовано (база є, але не завершено)  
- [ ] — не реалізовано

### 2.1 Реєстрація користувача

| ID     | Вимога                                                                 | Статус | Джерело / Коментар                                      |
|--------|------------------------------------------------------------------------|--------|---------------------------------------------------------|
| REG-01 | `email`, `username`, `surname`, `password`, `password_confirm`, `avatar` (опціонально) | [x] | `RegisterSerializer` + `RegisterView`                   |
| REG-02 | Пароль 8–16, ≥1 велика, ≥1 цифра, ≥1 спец. (`!@#$%^&*`)                | [x] | `RegisterSerializer.validate`                           |
| REG-03 | Паролі співпадають                                                     | [x] | `validate`                                              |
| REG-04 | Суворо валідований email (1–35 @ 3–35, без `..`, без `-./` на краях)   | [x] | `validate_email_custom` в `models.py`                   |
| REG-05 | `username`/`surname`: лише літери + дефіс (не на краях), 1–50 символів | [x] | `name_validator`                                        |
| REG-06 | Avatar ≤5MB, тільки PNG/JPEG                                           | [x] | `validate_avatar` в `UserSerializer`                    |
| REG-07 | Автоматична відправка верифікаційного листа (1 година)                 | [x] | `send_verification_email.delay()`                       |
| REG-08 | Новий користувач → роль `user` за замовчуванням                        | [x] | `User.save()`                                           |
| REG-09 | Автоматичне видалення непідтверджених акаунтів через 24 год             | [x] | `delete_unverified_users` Celery task                   |
| REG-10 | Throttling відправки email: 1 раз/хв на email                           | [x] | `is_throttled()` + Redis (TTL 60 сек)                   |
| REG-11 | OAuth2 (Google/GitHub/Apple)                                           | [ ] | allauth підключено, роути не налаштовано                |
| REG-12 | Invite-only режим                                                      | [ ] | —                                                       |
| REG-13 | reCAPTCHA v3                                                           | [ ] | —                                                       |
| REG-14 | Rate limit по IP (≤5 реєстрацій/год)                                   | [ ] | —                                                       |
| REG-15 | OTP на email замість посилання                                         | [ ] | —                                                       |

### 2.2 Підтвердження email

| ID     | Вимога                                      | Статус | Джерело                          |
|--------|---------------------------------------------|--------|----------------------------------|
| VER-01 | `uidb64` + `token`, дійсне 1 годину         | [x] | `VerifyEmailView`                |
| VER-02 | `is_verified = True` після підтвердження    | [x] | `VerifyEmailView`                |
| VER-03 | Повторна відправка (тільки для непідтверджених) | [x] | `ResendVerificationCodeView`     |
| VER-04 | Маскування email у логах (`te***@gmail.com`)| [x] | `mask_email()` в `tasks.py`      |
| VER-05 | Перевірка формату email перед відправкою    | [x] | `is_valid_email()`               |
| VER-06 | HTML-шаблони з брендингом                   | [ ] | зараз plain-text                 |

### 2.3 Логін та автентифікація

| ID     | Вимога                                           | Статус | Джерело                         |
|--------|--------------------------------------------------|--------|---------------------------------|
| AUTH-01 | Логін email+password → JWT access + refresh      | [x] | `LoginView` + `LoginSerializer` |
| AUTH-02 | Повернення профілю (`id`, `username`, `surname`, `email`, `roles`) | [x] | `LoginSerializer`               |
| AUTH-03 | Refresh token endpoint                           | [x] | `CustomTokenRefreshView`        |
| AUTH-04 | Blacklist refresh при логауті                    | [x] | `LogoutView`                    |
| AUTH-05 | JWT у всіх захищених ендпоінтах                   | [x] | `REST_FRAMEWORK` settings       |
| AUTH-06 | Блокування після 5 невдалих спроб                | [ ] | —                               |
| AUTH-07 | Логування всіх спроб входу в БД                  | [ ] | —                               |
| AUTH-08 | "Запам’ятати мене" (refresh 30 днів)             | [ ] | —                               |
| AUTH-09 | 2FA TOTP (Google Authenticator)                  | [ ] | —                               |
| AUTH-10 | 2FA SMS/Email OTP                                | [ ] | —                               |
| AUTH-11 | 2FA Backup codes                                 | [ ] | —                               |
| AUTH-12 | Список активних сесій + завершення сесії         | [ ] | —                               |
| AUTH-13 | Device fingerprinting + сповіщення про новий вхід| [ ] | —                               |
| AUTH-14 | Ротація refresh tokens                           | [ ] | —                               |

### 2.4 Відновлення пароля

| ID     | Вимога                                           | Статус | Джерело                              |
|--------|--------------------------------------------------|--------|--------------------------------------|
| PASS-01 | Запит → лист з посиланням (1 година)             | [x] | `PasswordResetRequestView` + task    |
| PASS-02 | Новий пароль з повною валідацією                 | [x] | `PasswordResetConfirmSerializer`     |
| PASS-03 | Throttling 1/хв                                  | [x] | `is_throttled('reset')`              |
| PASS-04 | OTP альтернатива (6 цифр)                        | [ ] | —                                    |
| PASS-05 | Заборона останніх 5 паролів                      | [ ] | —                                    |
| PASS-06 | Автоматичний логаут з усіх пристроїв             | [ ] | —                                    |

### 2.5 Профіль користувача

| ID     | Вимога                                           | Статус | Джерело               |
|--------|--------------------------------------------------|--------|-----------------------|
| PROF-01 | GET/PUT: `username`, `surname`, `email`, `roles`, `avatar` | [x] | `UserProfileView` |
| PROF-02 | Оновлення аватара з валідацією                  | [x] | `validate_avatar` |
| PROF-03 | Зміна email → нова верифікація                   | [ ] | —                     |
| PROF-04 | Зміна пароля (зі старим паролем)                 | [ ] | —                     |
| PROF-05 | Прив’язка соцмереж                               | [ ] | —                     |
| PROF-06 | Налаштування сповіщень                           | [ ] | —                     |
| PROF-07 | GDPR-видалення акаунта (запит → 30 днів)         | [ ] | —                     |

### 2.6 Адмін-панель та керування

| ID      | Вимога                                      | Статус | Джерело                              |
|---------|---------------------------------------------|--------|--------------------------------------|
| ADMIN-01 | CRUD користувачів (тільки `admin`)          | [x] | `UserViewSet` + `allowed_roles=['admin']` |
| ADMIN-02 | Фільтри: email, username, roles, is_verified, created_after/before | [x] | `UserFilter` |
| ADMIN-03 | Пагінація 50/стор (max 100)                 | [x] | `StandardResultsSetPagination`       |
| ADMIN-04 | Full-text пошук по username + surname       | [x] | `search_vector` + GinIndex           |
| ADMIN-05 | Імпорт/експорт CSV                          | [ ] | —                                    |
| ADMIN-06 | Масові дії (блокування, видалення)         | [ ] | —                                    |
| ADMIN-07 | Аудит-лог змін                              | [ ] | —                                    |
| ADMIN-08 | RBAC (moderator, support, seller тощо)      | [ ] | —                                    |

### 2.7 Ролі та дозволи

| ID     | Вимога                                      | Статус | Джерело                    |
|--------|---------------------------------------------|--------|----------------------------|
| ROLE-01 | Ролі `user`, `admin` (PostgreSQL ArrayField)| [x] | `roles` поле               |
| ROLE-02 | Адміни — повний доступ, користувачі — тільки свій профіль | [x] | `HasRolePermission` |
| ROLE-03 | SAFE методи — для всіх авторизованих        | [x] | `has_permission`           |
| ROLE-04 | Розширені кастомні ролі з permissions matrix| [~] | база є, поки тільки 2 ролі |

### 2.8 Безпека

| ID     | Вимога                                      | Статус | Джерело                          |
|--------|---------------------------------------------|--------|----------------------------------|
| SEC-01 | Хешування паролів                           | [x] | `set_password`                   |
| SEC-02 | JWT + blacklist                             | [x] | simplejwt                        |
| SEC-03 | Throttling 1M/день anon, 10M/день user       | [x] | REST_FRAMEWORK                   |
| SEC-04 | CORS whitelist                              | [x] | `CORS_ALLOWED_ORIGINS`           |
| SEC-05 | CSRF protection                             | [x] | middleware                       |
| SEC-06 | Helmet headers (HSTS тощо)                  | [ ] | —                                |
| SEC-07 | Брутфорс захист по IP                       | [ ] | —                                |
| SEC-08 | Моніторинг аномалій                         | [ ] | —                                |
| SEC-09 | Фільтрація чутливих даних у логах (password, token тощо) | [x] | `SensitiveDataFilter`            |

### 2.9 Email та комунікація

| ID      | Вимога                           | Статус | Джерело            |
|---------|----------------------------------|--------|--------------------|
| EMAIL-01 | Асинхронна відправка через Celery| [x] | `send_*_email` tasks |
| EMAIL-02 | HTML-шаблони в БД                | [ ] | —                  |
| EMAIL-03 | Unsubscribe link                 | [ ] | —                  |
| EMAIL-04 | Налаштування email preferences   | [ ] | —                  |
| EMAIL-05 | Webhooks (registered, verified)  | [ ] | —                  |

### 2.10 API та інтеграції

| ID     | Вимога             | Статус | Джерело              |
|--------|--------------------|--------|----------------------|
| API-01 | Swagger UI         | [x] | drf-spectacular      |
| API-02 | OpenAPI 3 schema   | [x] | SpectacularAPIView   |
| API-03 | gRPC endpoint      | [ ] | —                    |
| API-04 | Kafka / Webhooks   | [ ] | —                    |

### 2.11 Моніторинг та observability

| ID     | Вимога                     | Статус | Джерело            |
|--------|----------------------------|--------|--------------------|
| MON-01 | Health check Redis + DB    | [x] | `HealthCheckView`  |
| MON-02 | Prometheus метрики         | [ ] | —                  |
| MON-03 | OpenTelemetry tracing      | [ ] | —                  |
| MON-04 | Alerting (Slack, email)    | [ ] | —                  |
| MON-05 | SLO 99.9% uptime           | [ ] | —                  |

### 2.12 Тестування

| ID     | Вимога                     | Статус |
|--------|----------------------------|--------|
| TEST-01 | Unit + integration tests   | [ ] |
| TEST-02 | Load testing (Locust)      | [ ] |
| TEST-03 | Security scan (Bandit, ZAP)| [ ] |
| TEST-04 | Contract testing (Pact)    | [ ] |

### 2.13 Кешування (план)

| ID        | Вимога                        | Статус | Коментар                     |
|-----------|-------------------------------|--------|------------------------------|
| UCACHE-01 | Кеш профілів                  | [ ] | `user:profile:{id}`, TTL 30 хв |
| UCACHE-02 | Кеш списків адмінки           | [ ] | `user:list:page:{n}`, TTL 10 хв |
| UCACHE-03 | Інвалідація при оновленні     | [ ] | `cache.delete()`             |

### Roadmap (актуальний)

| Етап           | Термін         | Пріоритетні задачі                                          |
|----------------|----------------|-------------------------------------------------------------|
| **MVP+**       |  2025   | 2FA (TOTP), блокування після невдалих спроб, управління сесіями |
| **Production** |  2026    | OAuth2, reCAPTCHA, аудит-лог, метрики, HSTS                 |
| **Enterprise** |  2026+ | RBAC, GDPR-видалення, gRPC, SLO, OpenTelemetry             |