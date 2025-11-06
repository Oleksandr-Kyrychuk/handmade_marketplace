# Функціональні Вимоги до Product Service  
*Версія 1.0 — Enterprise-Ready Product Management Service*

> **Мета**: Забезпечити ефективне керування продуктами, категоріями, відгуками та модерацією в системі Handmade Marketplace.  
> **Стан**: 45% реалізованих вимог, 55% — у плані розширення.  
> **Технології**: Django, DRF, JWT, Celery, Redis, PostgreSQL, Cloudinary, Swagger.

---

## Легенда
- [x] — **вже реалізовано**  
- [ ] — **планується до реалізації**  
- [~] — **частково реалізовано**

---

## 2.1 Керування категоріями

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| CAT-01 | Ієрархічні категорії: назва, parent, image (Cloudinary), slug (авто-генерація) | [x] | `Category` model |
| CAT-02 | Full-text пошук по назві (search_vector) | [x] | `search_vector` в `Category` |
| CAT-03 | Upload зображення для категорії (≤32MB, JPG/PNG/GIF) | [x] | `upload_category_image` в `ProductViewSet` |
| CAT-04 | Авто-генерація унікального slug | [x] | `save()` в `Category` |
| CAT-05 | CRUD для категорій (створення/редагування/видалення) | [~] | Serializer є, але ViewSet відсутній |
| CAT-06 | Валідація назви: літери, цифри, пробіли, дефіси, лапки | [x] | `name_validator` в models |
| CAT-07 | Імпорт/експорт категорій (CSV/JSON) | [ ] | — |
| CAT-08 | Авто-дерево категорій (nested sets або materialized path) | [ ] | — |
| CAT-09 | Кешування дерева категорій (Redis) | [ ] | — |

---

## 2.2 Керування продуктами

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| PROD-01 | CRUD продуктів: vendor_id, category, name, description, sale_type (fixed/auction), price, discount_price, start_price, auction_end_time, stock, rating_count, product_href, is_approved | [x] | `Product` model, `ProductViewSet` |
| PROD-02 | Валідація назви: літери, цифри, пробіли, дефіси, лапки | [x] | `name_validator` |
| PROD-03 | Валідація для fixed: price обов'язкова, discount < price | [x] | `save()` в `Product` |
| PROD-04 | Для auction: start_price, auction_end_time; discount = None | [x] | `save()` |
| PROD-05 | Авто-генерація унікального slug (product_href) | [x] | `save()` |
| PROD-06 | Full-text пошук: name (A), description (B) | [x] | `search_vector` |
| PROD-07 | Фільтри: category, min/max price, sale_type, is_approved | [x] | `ProductFilter` |
| PROD-08 | Доступність: stock > 0 та is_approved | [x] | `is_available()` |
| PROD-09 | Інтеграція з User Service: get_vendor (username, surname) | [x] | `get_vendor` в `ProductSerializer` |
| PROD-10 | Тільки авторизовані: створення/редагування (vendor_id = user.id) | [x] | `perform_create/update` |
| PROD-11 | Адміни: повний доступ; користувачі: тільки свої продукти | [x] | `HasRolePermission` |
| PROD-12 | Авто-модерація при створенні (is_approved = False) | [x] | `perform_create` |
| PROD-13 | Асинхронна модерація контенту (toxic check via external API) | [x] | `moderate_content` task |
| PROD-14 | Ручна модерація: схвалити/відхилити (update is_approved) | [x] | `ModerationViewSet` |
| PROD-15 | Нотифікація про модерацію (email via User Service) | [x] | `send_moderation_notification` |
| PROD-16 | Пагінація для списку продуктів | [~] | ViewSet, але не явно |
| PROD-17 | Варіанти продуктів (розміри, кольори) | [ ] | — |
| PROD-18 | Рекомендації (similar products via ML) | [ ] | — |
| PROD-19 | Імпорт/експорт продуктів (CSV) | [ ] | — |
| PROD-20 | Аукціон: біддинг, таймер, авто-закриття | [ ] | — |

---

## 2.3 Зображення продуктів

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| IMG-01 | Багато зображень на продукт: image (Cloudinary), image_url | [x] | `ProductImage` model |
| IMG-02 | Upload зображення: ≤32MB, JPG/PNG/GIF | [x] | `upload_image` в `ProductViewSet` |
| IMG-03 | Асинхронне завантаження в Cloudinary (Celery) | [x] | `upload_image_to_cloudinary` task |
| IMG-04 | Валідація: розмір, формат | [x] | `ProductImageUploadSerializer` |
| IMG-05 | Авто-оптимізація (resize, compress) | [ ] | — |
| IMG-06 | Водяні знаки | [ ] | — |

---

## 2.4 Відгуки та рейтинги

| ID | Вимога | Статус | Джерело |
|----|-------|-------|--------|
| REV-01 | CRUD відгуків: product, user_id, rating (0-5), comment, created_at, is_approved | [x]   | `Review` model, `add_review` в `ProductViewSet` |
| REV-02 | Валідація rating: 0-5 | [x]   | `validate_rating` |
| REV-03 | Авто-оновлення rating_count на продукті | [x]   | `save/delete` в `Review` |
| REV-04 | Інтеграція з User Service: get_user (username) | [x]   | `get_user` в `ReviewSerializer` |
| REV-05 | Тільки авторизовані: створення (user_id = user.id) | [x]   | `add_review` |
| REV-06 | Дозволи: адміни — все; користувачі — свої відгуки | [x]   | `ReviewPermission` |
| REV-07 | Авто-модерація: is_approved = False при створенні | [x]   | `add_review` |
| REV-08 | Асинхронна модерація (toxic check) | [x]   | `moderate_content` task |
| REV-09 | Ручна модерація | [x]   | `ModerationViewSet` |
| REV-10 | Нотифікація про модерацію | [x]   | `send_moderation_notification` |
| REV-11 | Фільтри: по продукту, даті, рейтингу | [x]   | — |
| REV-12 | Відповіді на відгуки (nested) | [ ]   | — |
| REV-13 | Helpful votes | [ ]   | — |

---

## 2.5 Модерація

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| MOD-01 | Авто-модерація тексту (product/review) via external API | [x] | `moderate_content` task |
| MOD-02 | Ручна модерація: update is_approved для product/review | [x] | `ModerationViewSet` |
| MOD-03 | Нотифікація vendor/user про результат (email) | [x] | `send_moderation_notification` |
| MOD-04 | Черга модерації (list pending) | [~] | Фільтр is_approved=False |
| MOD-05 | Причини відхилення (field) | [ ] | — |
| MOD-06 | Аудит-лог модерації | [ ] | — |

---

## 2.6 Безпека та дозволи

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| SEC-01 | JWT автентифікація | [x] | `REST_FRAMEWORK` |
| SEC-02 | Ролі: user (свої продукти), admin (все) | [x] | `HasRolePermission` |
| SEC-03 | Throttling: 1M/день (anon), 10M/день (user) | [x] | `REST_FRAMEWORK` |
| SEC-04 | CORS з origins | [x] | Settings |
| SEC-05 | Логування дій (CRUD, moderation) | [x] | Logging config |
| SEC-06 | CSRF protection | [x] | Middleware |
| SEC-07 | Rate limit по IP для upload | [ ] | — |
| SEC-08 | CAPTCHA для відгуків | [ ] | — |

---

## 2.7 Інтеграції та tasks

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| INT-01 | Інтеграція з User Service: fetch user data (email, username) | [x] | Serializers, tasks |
| INT-02 | Celery tasks: upload image, moderate, notify | [x] | `tasks.py` |
| INT-03 | Redis broker/backend | [x] | Settings |
| INT-04 | Cloudinary для images | [x] | Models, tasks |
| INT-05 | External moderation API | [x] | `moderate_content` |
| INT-06 | Webhooks: product.created, approved | [ ] | — |
| INT-07 | Integration з Payment Service | [ ] | — |

---

## 2.8 API та документація

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| API-01 | OpenAPI (Swagger UI) | [x] | `drf_spectacular`, urls |
| API-02 | JSON Schema | [x] | `SpectacularAPIView` |
| API-03 | gRPC endpoint | [ ] | — |

---

## 2.9 Моніторинг

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| MON-01 | Health check: Redis + DB | [x] | `HealthCheckView` |
| MON-02 | Prometheus метрики | [ ] | — |
| MON-03 | Tracing (OpenTelemetry) | [ ] | — |
| MON-04 | Alerting | [ ] | — |

---

## 2.10 Тестування

| ID | Вимога | Статус |
|----|-------|--------|
| TEST-01 | Unit + integration tests | [ ] |
| TEST-02 | Load testing | [ ] |
| TEST-03 | Security scan | [ ] |

---

## 2.11 Кешування

| ID | Вимога | Статус | Джерело |
|----|-------|-----|--------|
| PCACHE-01 | Кеш списків продуктів | [] | `product:list:*`, TTL 5 хв |
| PCACHE-02 | Кеш деталей продукту | [] | `product:detail:{id}`, TTL 10 хв |
| PCACHE-03 | Інвалідатор при змінах | [] | `invalidate_product_cache` |



## План розширення (Roadmap)

| Етап | Термін | Вимоги |
|------|--------|-------|
| **MVP+** | &&&    | Аукціон, варіанти, CAPTCHA |
| **Production** | &&&    | Webhooks, імпорт, рекомендації |
| **Enterprise** | 2+ міс | gRPC, аудит, ML модерація |

---
