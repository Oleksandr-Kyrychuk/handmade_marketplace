# Функціональні Вимоги до User Service  
*Версія 1.0 — Enterprise-Ready Auth Service*

> **Мета**: Забезпечити безпечне, масштабоване та зручне керування користувачами для Handmade Marketplace.  
> **Стан**: 40% реалізованих вимог, 60% — у плані розширення.  
> **Технології**: Django, DRF, JWT, Celery, Redis, PostgreSQL, Cloudinary, Swagger.

---

## Легенда
- [x] — **вже реалізовано**  
- [ ] — **планується до реалізації**  
- [~] — **частково реалізовано**

---

## 2.1 Реєстрація користувача

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| REG-01 | Користувач реєструється через API з полями: `email`, `username`, `surname`, `password`, `password_confirm`, `avatar` (опціонально) | [x] | `RegisterSerializer`, `RegisterView` |
| REG-02 | **Валідація пароля**: 8–16 символів, ≥1 велика літера, ≥1 цифра, ≥1 спец. символ (`!@#$%^&*`) | [x] | `validate` в `RegisterSerializer` |
| REG-03 | **Паролі повинні співпадати** (`password` = `password_confirm`) | [x] | `validate` |
| REG-04 | **Валідація email**: унікальний, локальна частина 1–35, домен 3–35, без `..`, без `-./` на початку/кінці | [x] | `validate_email_custom` в `models.py` |
| REG-05 | **Валідація `username` / `surname`**: 1–50 символів, лише літери + дефіс (не на початку/кінці) | [x] | `name_validator` |
| REG-06 | **Валідація `avatar`**: ≤5MB, лише PNG/JPEG | [x] | `validate_avatar` в `UserSerializer` |
| REG-07 | Після реєстрації — **автоматична відправка листа з верифікаційним посиланням** (дійсне 1 годину) | [x] | `send_verification_email` task |
| REG-08 | Нові користувачі отримують роль `user` за замовчуванням | [x] | `save()` в `User` model |
| REG-09 | **Автоматичне видалення непідтверджених акаунтів через 24 години** | [x] | `delete_unverified_users` task |
| REG-10 | **Throttling на відправку email**: 1 раз на хвилину на email | [x] | `is_throttled` в `tasks.py` |
| REG-11 | Реєстрація через **Google / GitHub / Apple (OAuth2)** | [ ] | — |
| REG-12 | **Invite-only режим**: реєстрація лише за запрошувальним посиланням | [ ] | — |
| REG-13 | **reCAPTCHA v3** для захисту від ботів | [ ] | — |
| REG-14 | **Rate limit по IP**: ≤5 реєстрацій/год з однієї IP | [ ] | — |
| REG-15 | **OTP на email замість посилання** (6 цифр, 10 хв) | [ ] | — |

---

## 2.2 Підтвердження email (верифікація)

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| VER-01 | Підтвердження через `uidb64` + `token` (дійсне 1 годину) | [x] | `VerifyEmailView` |
| VER-02 | Поле `is_verified` → `True` після підтвердження | [x] | `VerifyEmailView` |
| VER-03 | Повторна відправка коду (тільки для `is_verified=False`) | [x] | `ResendVerificationCodeView` |
| VER-04 | Маска email у логах: `te***@gmail.com` | [x] | `mask_email` |
| VER-05 | Валідація формату email перед відправкою | [x] | `is_valid_email` |
| VER-06 | HTML-шаблони email з брендингом | [ ] | — |

---

## 2.3 Логін та автентифікація

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| AUTH-01 | Логін через `email` + `password` → JWT `access` + `refresh` | [x] | `LoginView`, `LoginSerializer` |
| AUTH-02 | Повернення даних користувача: `id`, `username`, `surname`, `email`, `roles` | [x] | `LoginSerializer` |
| AUTH-03 | Оновлення токена через `refresh` | [x] | `CustomTokenRefreshView` |
| AUTH-04 | **Blacklist refresh token при логауті** | [x] | `LogoutView` |
| AUTH-05 | JWT автентифікація у всіх захищених ендпоінтах | [x] | `REST_FRAMEWORK` |
| AUTH-06 | **Блокування після 5 невдалих спроб** (15 хв, по email + IP) | [ ] | — |
| AUTH-07 | **Логування всіх спроб входу** (БД: email, IP, device, success/fail) | [ ] | — |
| AUTH-08 | **"Запам’ятати мене"** → refresh token на 30 днів | [ ] | — |
| AUTH-09 | **Двофакторна автентифікація (2FA)**: TOTP (Google Authenticator) | [ ] | — |
| AUTH-10 | 2FA: SMS/Email OTP | [ ] | — |
| AUTH-11 | 2FA: Backup codes | [ ] | — |
| AUTH-12 | **Список активних сесій** + можливість завершити сесію | [ ] | — |
| AUTH-13 | **Device fingerprinting** + сповіщення про новий вхід | [ ] | — |
| AUTH-14 | **Ротація refresh tokens** | [ ] | — |

---

## 2.4 Відновлення пароля

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| PASS-01 | Запит → email з посиланням (1 година) | [x] | `PasswordResetRequestView` |
| PASS-02 | Новий пароль з повною валідацією | [x] | `PasswordResetConfirmSerializer` |
| PASS-03 | Throttling: 1 раз/хв | [x] | `is_throttled` |
| PASS-04 | **OTP (6 цифр) на email** як альтернатива | [ ] | — |
| PASS-05 | Заборона використовувати **старі паролі** (історія 5) | [ ] | — |
| PASS-06 | **Автоматичний логаут з усіх пристроїв** після скидання | [ ] | — |

---

## 2.5 Профіль користувача

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| PROF-01 | Перегляд/оновлення: `username`, `surname`, `email`, `roles`, `avatar` | [x] | `UserProfileView` |
| PROF-02 | Оновлення `avatar` з валідацією | [x] | `validate_avatar` |
| PROF-03 | **Зміна email** → нова верифікація | [ ] | — |
| PROF-04 | **Зміна пароля** (з перевіркою старого) | [ ] | — |
| PROF-05 | Прив’язка соцмереж | [ ] | — |
| PROF-06 | Налаштування сповіщень | [ ] | — |
| PROF-07 | **Видалення акаунта (GDPR)**: запит → 30 днів → анонімізація | [ ] | — |

---

## 2.6 Адмін-панель та керування

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| ADMIN-01 | CRUD користувачів (тільки для `admin`) | [x] | `UserViewSet` |
| ADMIN-02 | Фільтри: `email`, `username`, `roles`, `is_verified`, `created_after/before` | [x] | `UserFilter` |
| ADMIN-03 | Пагінація: 50/стор, max 100 | [x] | `StandardResultsSetPagination` |
| ADMIN-04 | Full-text пошук по `username` + `surname` | [x] | `search_vector` |
| ADMIN-05 | Імпорт/експорт CSV | [ ] | — |
| ADMIN-06 | Масові дії: блокування, видалення | [ ] | — |
| ADMIN-07 | **Аудит-лог** (хто, коли, що змінив) | [ ] | — |
| ADMIN-08 | **RBAC**: кастомні ролі (`moderator`, `support`, `seller`) | [ ] | — |

---

## 2.7 Ролі та дозволи

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| ROLE-01 | Ролі: `user`, `admin` (array) | [x] | `roles` в `User` |
| ROLE-02 | Дозволи: адміни — повний доступ, користувачі — лише свій профіль | [x] | `HasRolePermission` |
| ROLE-03 | SAFE методи (GET) — для всіх авторизованих | [x] | `has_permission` |
| ROLE-04 | Кастомні ролі з permissions matrix | [ ] | — |

---

## 2.8 Безпека

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| SEC-01 | Паролі хешуються (`set_password`) | [x] | `CustomUserManager` |
| SEC-02 | JWT + blacklist | [x] | `simplejwt` |
| SEC-03 | Throttling: 1M/день (anon), 10M/день (user) | [x] | `REST_FRAMEWORK` |
| SEC-04 | CORS з обмеженими origins | [x] | `CORS_ALLOWED_ORIGINS` |
| SEC-05 | CSRF protection | [x] | Middleware |
| SEC-06 | Helmet headers (HSTS, etc.) | [ ] | — |
| SEC-07 | Брутфорс захист по IP | [ ] | — |
| SEC-08 | Моніторинг аномалій (багато країн) | [ ] | — |

---

## 2.9 Email та комунікація

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| EMAIL-01 | Асинхронна відправка через Celery | [x] | `send_*_email` tasks |
| EMAIL-02 | HTML-шаблони в БД | [ ] | — |
| EMAIL-03 | Unsubscribe link | [ ] | — |
| EMAIL-04 | Налаштування email preferences | [ ] | — |
| EMAIL-05 | Webhooks: `user.registered`, `user.verified` | [ ] | — |

---

## 2.10 API та інтеграції

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| API-01 | OpenAPI (Swagger UI) | [x] | `drf_spectacular` |
| API-02 | JSON Schema | [x] | `SpectacularAPIView` |
| API-03 | gRPC endpoint | [ ] | — |
| API-04 | Webhooks / Events (Kafka) | [ ] | — |

---

## 2.11 Моніторинг та observability

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| MON-01 | Health check: Redis + DB | [x] | `HealthCheckView` |
| MON-02 | Prometheus метрики | [ ] | — |
| MON-03 | OpenTelemetry tracing | [ ] | — |
| MON-04 | Alerting (Slack, email) | [ ] | — |
| MON-05 | SLO: 99.9% uptime, <500ms login | [ ] | — |

---

## 2.12 Тестування

| ID | Вимога | Статус |
|----|-------|--------|
| TEST-01 | Unit + integration tests (pytest) | [ ] |
| TEST-02 | Load testing (Locust) | [ ] |
| TEST-03 | Security scan (Bandit, ZAP) | [ ] |
| TEST-04 | Contract testing (Pact) | [ ] |

---

## План розширення (Roadmap)

| Етап | Термін | Вимоги |
|------|--------|-------|
| **MVP+** | ???    | 2FA (TOTP), блокування, сесії |
| **Production** | ???    | OAuth, CAPTCHA, аудит, метрики |
| **Enterprise** | 2+ міс | RBAC, GDPR, gRPC, SLO |

---
