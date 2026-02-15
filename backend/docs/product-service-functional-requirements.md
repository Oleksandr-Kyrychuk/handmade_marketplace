# Функціональні Вимоги до Product Service  
*Версія 1.7 — Актуальний стан проекту (14 січня 2026)*

> **Мета**: Забезпечити повноцінне керування продуктами, категоріями, відгуками, зображеннями, модерацією контенту та резервуванням stock в мікросервісній архітектурі Handmade Marketplace.  
> **Стан**: ≈ **80–84%** реалізованих вимог  
> (MVP — 100%, MVP+ — **~78%**, Production-готовність — **~45%**)  
> **Технології**: Django 5.1+, DRF, Celery + Redis, PostgreSQL (GIN + search_vector), Cloudinary (асинхронний upload), drf-spectacular, кастомний JWT middleware (verify у User Service), RBAC vendor/admin, авто-модерація (заглушка)

---

## Легенда
- [x] — повністю реалізовано та працює  
- [~] — частково реалізовано (вказано деталі)  
- [ ] — не реалізовано

---

## 2.1 Керування категоріями

| ID     | Вимога                                                                 | Статус | Коментар |
|--------|------------------------------------------------------------------------|--------|---------|
| CAT-01 | Ієрархічні категорії (name, parent, image, slug)                     | [x]    | Модель повністю готова |
| CAT-02 | Full-text пошук по назві (search_vector + GIN)                       | [x]    | Працює |
| CAT-03 | Upload зображення для категорії (Cloudinary, ≤32MB, JPG/PNG/GIF)    | [x]    | Є серіалізатор + Celery task (model_type="category") |
| CAT-04 | Авто-генерація унікального slug                                      | [x]    | В save() моделі |
| CAT-05 | CRUD для категорій (ViewSet)                                         | [ ]    | **Немає ендпоінтів!** (немає CategoryViewSet) — критична прогалина |
| CAT-06 | Валідація назви категорії                                            | [ ]    | Немає |
| CAT-07 | Tree structure / nested response                                     | [ ]    | Поки простий FK |

**Висновок**: категорії технічно готові на ~85%, але **немає API** — тільки фільтр по продуктах.

---

## 2.2 Керування продуктами

| ID     | Вимога                                                                 | Статус | Коментар |
|--------|------------------------------------------------------------------------|--------|----------|
| PROD-01| Повний CRUD продуктів (всі поля)                                       | [x]    | ProductViewSet |
| PROD-02| RBAC: vendor — свої, admin — всі                                       | [x]    | HasRolePermission + vendor_id check |
| PROD-03| Нові продукти → is_approved=False + авто-модерація                     | [x]    | moderate_content.delay() в perform_create |
| PROD-04| Редагування продукту → повторна модерація (is_approved=False)         | [x]    | Так, в perform_update |
| PROD-05| Асинхронний upload зображень (Cloudinary)                              | [x]    | Celery task + action upload_image |
| PROD-06| Резервування stock (PATCH /products/{id}/reserve/)                    | [x]    | Повністю працює + Reservation модель + expires_at |
| PROD-07| Скасування резерву (cancel_reservation/)                               | [x]    | Є action |
| PROD-08| Авто-очищення прострочених резервів                                    | [x]    | Celery beat задача cleanup_expired_reservations |
| PROD-09| Фільтри: category, price, rating, sale_type, dates, is_approved       | [x]    | ProductFilter — один з найкращих у проєкті |
| PROD-10| Full-text пошук (назва + опис)                                         | [x]    | search_vector + GIN |
| PROD-11| Підтримка варіантів (size/color)                                       | [ ]    | Немає |
| PROD-12| Аукціони (bids, auction_end_time, current_bid)                         | [~]    | Поля є (sale_type='auction', auction_end_time, start_price), але **логіка ставок відсутня** |
| PROD-13| Кешування списків/деталей                                              | [ ]    | Не реалізовано |

---

## 2.3 Відгуки

| ID     | Вимога                                                                 | Статус | Коментар |
|--------|------------------------------------------------------------------------|--------|---------|
| REV-01 | CRUD відгуків (rating 0–5)                                             | [x]    | ReviewViewSet |
| REV-02 | Тільки авторизовані + один відгук тільки на куплений товар             | [~]    | Авторизація є, перевірка покупки — **немає** (можна залишити відгук на будь-який продукт) |
| REV-03 | Авто-модерація відгуків (Celery)                                       | [x]    | moderate_content.delay() в perform_create |
| REV-04 | Схвалені відгуки впливають на рейтинг продукту                         | [x]    | rating_count оновлюється в Review.save() |
| REV-05 | Фільтри: product, rating, is_approved, created_at                      | [x]    | filterset_fields |

---

## 2.4 Модерація контенту

| ID     | Вимога                                                                 | Статус | Коментар |
|--------|------------------------------------------------------------------------|--------|---------|
| MOD-01 | ModerationViewSet (ручна модерація)                                    | [x]    | Повністю працює |
| MOD-02 | Авто-модерація (toxicity check)                                        | [x]    | Celery задача → http://127.0.0.1:8001/moderate (заглушка, але працює) |
| MOD-03 | Нотифікація автору про результат модерації                             | [x]    | send_moderation_notification.delay() |
| MOD-04 | Черга модерації для адмінів                                            | [x]    | GET /moderation/ повертає все з is_approved=False |

---

## 2.5 Stock & Резервування

| ID      | Вимога                                                                 | Статус |
|---------|------------------------------------------------------------------------|--------|
| STOCK-01| Резерв stock на 30 хвилин (Reservation + expires_at)                  | [x]    |
| STOCK-02| Авто-очищення прострочених (Celery beat)                               | [x]    |
| STOCK-03| Ендпоінти reserve/ та cancel_reservation/                              | [x]    |

---

## 2.6 API та документація

| ID     | Вимога                                                                 | Статус |
|--------|------------------------------------------------------------------------|--------|
| API-01 | OpenAPI 3.0 + Swagger UI                                               | [x]    |
| API-02 | Усі ендпоінти задокументовані (extend_schema)                          | [x]    |
| API-03 | Версіонування (/v1/)                                                   | [ ]    |

**Актуальні ендпоінти (14.01.2026):**
- `GET/POST /products/`
- `GET/PUT/PATCH/DELETE /products/{id}/`
- `POST /products/{id}/upload_image/`
- `PATCH /products/{id}/reserve/`
- `PATCH /products/{id}/cancel_reservation/`
- `GET/POST /reviews/`
- `GET/PUT/PATCH/DELETE /reviews/{id}/`
- `GET/POST/PATCH /moderation/`
- `/health`, `/schema/`, `/swagger/`

---

## 2.7 Безпека та автентифікація

| ID     | Вимога                                                                 | Статус |
|--------|------------------------------------------------------------------------|--------|
| SEC-01 | Кастомний JWT middleware (verify token у User Service)                | [x]    |
| SEC-02 | RBAC vendor/admin                                                      | [x]    |
| SEC-03 | Throttling (1M/день anon, 10M/день user)                               | [x]    |
| SEC-04 | CORS + SensitiveDataFilter в логах                                     | [x]    |

---

## 2.8 Моніторинг

| ID     | Вимога                                                                 | Статус |
|--------|------------------------------------------------------------------------|--------|
| MON-01 | Health check (Redis + DB)                                              | [x]    |
| MON-02 | Prometheus / OpenTelemetry                                             | [ ]    |

---

## Оновлений Roadmap (реальний, 14 січня 2026)

| Етап          | Статус       | %    | Залишилось (ключові задачі)                                                                 |
|---------------|--------------|------|---------------------------------------------------------------------------------------------|
| **MVP**       | Виконано     | 100% | —                                                                                           |
| **MVP+**      | В процесі    | ~78% | 1. CategoryViewSet<br>2. Перевірка "відгук тільки після покупки"<br>3. Логіка аукціонів (bids)<br>4. Варіанти продуктів |
| **Production**| Початок      | ~45% | Кешування Redis, повноцінні тести, security headers, Reservation logic при замовленні     |
| **Enterprise**| Не почато    | 0%   | gRPC, ML-модерація (замість заглушки), Prometheus/OpenTelemetry, load testing              |

**Пріоритет на зараз (можна закрити за 1–3 тижні):**
1. Додати `CategoryViewSet` (CRUD + пошук) — блокуюча задача
2. Додати перевірку "відгук тільки після покупки" (запит до Order Service)
3. Написати базові тести на ключові сценарії (продукт, відгук, модерація)

