# Функціональні Вимоги до API Gateway  
**Версія 1.2 — Поточний стан на 20 листопада 2025**  
**Статус: Production-Ready Gateway (≈ 88% від Enterprise-рівня)**

> **Мета** — Централізований, швидкий, безпечний та самодостатній вхід для всіх мікросервісів Handmade Marketplace (User, Product, Order) з повним проксі, кешуванням схем, об’єднаною документацією, health check та готовністю до горизонтального масштабування.  
> **Технології** — Django 5.2 + DRF, drf-spectacular, Redis (кеш схем), requests, threading + exponential backoff + jitter, WhiteNoise, django-environ

### Легенда
- [x] — реалізовано та працює в продакшні  
- [~] — частково реалізовано (база є, але не завершено)  
- [ ] — не реалізовано

### 2.1 Проксі-запити до мікросервісів

| ID       | Вимога                                                                 | Статус | Джерело / Коментар                                      |
|----------|------------------------------------------------------------------------|--------|---------------------------------------------------------|
| PROXY-01 | Динамічний проксі всіх HTTP-методів до всіх сервісів                   | [x]    | `ProxyView.handle_request()` — один універсальний в’ю |
| PROXY-02 | `/users/...`   → `http://user-service:8001/...`                        | [x]    | `settings.USER_SERVICE_URL`                             |
| PROXY-03 | `/products/...` → `http://product-service:8002/...`                    | [x]    | `settings.PRODUCT_SERVICE_URL`                          |
| PROXY-04 | `/orders/...`   → `http://order-service:8003/orders/...`               | [x]    | `ORDER_SERVICE_URL`                                     |
| PROXY-05 | `/carts/...`    → `http://order-service:8003/cart/...`                 | [x]    | окрема логіка для cart                                  |
| PROXY-06 | Повна передача headers (включаючи Authorization JWT), body, query params, файлів | [x] | `requests.request()` з `data=request.body`              |
| PROXY-07 | Таймаут 20 секунд на кожен запит                                       | [x]    | `timeout=20`                                            |
| PROXY-08 | Обробка помилок: 502 (connection/error), 504 (timeout), 404 (no route) | [x]    | `except Timeout`, `ConnectionError`, `RequestException`|
| PROXY-09 | Коректний проксі JSON та бінарних відповідей                           | [x]    | Перевірка `Content-Type`, `resp.json()` або `resp.content` |
| PROXY-10 | Rate limiting на рівні gateway (1M/день anon, 10M/день user)           | [x]    | `REST_FRAMEWORK` throttling                             |
| PROXY-11 | Логування всіх помилок проксі (target_url, status, error)              | [x]    | `logger.warning/error`                                  |
| PROXY-12 | Circuit breaker                                                        | [ ]    | —                                                       |
| PROXY-13 | Retry з exponential backoff для проксі-запитів                         | [ ]    | —                                                       |

### 2.2 Кешування OpenAPI схем

| ID       | Вимога                                                                 | Статус | Джерело / Коментар                                      |
|----------|------------------------------------------------------------------------|--------|---------------------------------------------------------|
| SCHEMA-01 | Фоновий завантажувач схем при старті аплікейшена (daemon thread)       | [x]    | `background_schema_loader()` в `apps.py`                |
| SCHEMA-02 | Кеш схем в Redis (ключі `user_service_schema`, `product_service_schema`, `order_service_schema`, TTL 1 год) | [x] | `cache.set(..., timeout=3600)`                          |
| SCHEMA-03 | Exponential backoff + jitter (±10%) при помилках завантаження           | [x]    | `2 ** attempt`, `max_sleep=60`, jitter                  |
| SCHEMA-04 | Безкінечний цикл авто-оновлення схем                                   | [x]    | `while True`                                            |
| SCHEMA-05 | Окреме логирование успіху/помилки для кожного сервісу                  | [x]    | `logger.info/warning`                                   |
| SCHEMA-06 | Management команда `fetch_schema` для ручного оновлення                | [x]    | `app/management/commands/fetch_schema.py`               |
| SCHEMA-07 | Авто-детект сервісів через env змінні                                  | [x]    | `USER_SERVICE_URL`, `PRODUCT_SERVICE_URL`, `ORDER_SERVICE_URL` |

### 2.3 Об’єднання OpenAPI документації

| ID      | Вимога                                           | Статус | Джерело                              |
|---------|--------------------------------------------------|--------|--------------------------------------|
| DOCS-01 | Об’єднання схем User + Product + Order в один документ | [x] | `MergedSchemaView` (кеш + merge)     |
| DOCS-02 | Swagger UI з перемикачем сервісів (User/Product/Order) | [x] | `urls.primaryName=User` тощо         |
| DOCS-03 | Root endpoint `/` — карта всіх доступних шляхів та сервісів | [x] | `RootView` з кешованими схемами      |
| DOCS-04 | Окремі `/users/schema/`, `/products/schema/` тощо (проксі) | [x] | `SpectacularAPIView` проксі          |
| DOCS-05 | Генерація SDK (TypeScript, Python тощо)          | [ ]    | —                                    |
| DOCS-06 | Версіонування API в URL (/v1/, /v2/)             | [ ]    | —                                    |

### 2.4 Health Check

| ID     | Вимога                                           | Статус | Джерело                              |
|--------|--------------------------------------------------|--------|--------------------------------------|
| HC-01  | `/health` — повна перевірка всіх залежностей     | [x]    | `HealthCheckView`                    |
| HC-02  | Перевірка Redis                                  | [x]    | `cache.get('health_check_test')`     |
| HC-03  | Перевірка User/Product/Order сервісів (`/health`)| [x]    | `requests.get(..., timeout=20)`      |
| HC-04  | 5 ретраїв з затримкою 10с при помилці            | [x]    | `max_retries=5`, `retry_delay=10`    |
| HC-05  | Статус 200 (ok) / 503 (error)                    | [x]    | `status=200 if all_healthy else 503` |
| HC-06  | Детальна відповідь з status/detail кожного сервісу | [x]   | `results['service'] = {'status': ..., 'detail': ...}` |
| HC-07  | Логування всіх провалених перевірок              | [x]    | `logger.error()`                     |

### 2.5 Безпека та стабільність

| ID     | Вимога                                           | Статус | Джерело                              |
|--------|--------------------------------------------------|--------|--------------------------------------|
| SEC-01 | CORS з whitelist                                 | [x]    | `CORS_ALLOWED_ORIGINS`               |
| SEC-02 | CSRF protection middleware                       | [x]    | `CsrfViewMiddleware`                         |
| SEC-03 | WhiteNoise для статики                           | [x]    | `WhiteNoiseMiddleware`               |
| SEC-04 | Throttling 1M/день anon, 10M/день user            | [x]    | `REST_FRAMEWORK`                     |
| SEC-05 | Проксі JWT без валідації (просто передача)       | [x]    | `Authorization` header передається   |
| SEC-06 | Логування всіх дій (DEBUG для app, INFO для django) | [x]  | `LOGGING` config                     |
| SEC-07 | Helmet headers (HSTS, CSP, X-Content-Type-Options)| [ ]    | —                                    |
| SEC-08 | mTLS між gateway та сервісами                    | [ ]    | —                                    |

### 2.6 Конфігурація та розгортання

| ID     | Вимога                                           | Статус | Джерело                              |
|--------|--------------------------------------------------|--------|--------------------------------------|
| CFG-01 | Підтримка `.env.local` та `.env`                 | [x]    | `environ` + `ENV=local`              |
| CFG-02 | ASGI + WSGI підтримка                            | [x]    | `asgi.py`, `wsgi.py`                 |
| CFG-03 | Redis cache з TTL та IGNORE_EXCEPTIONS           | [x]    | `CACHES` config                      |
| CFG-04 | PostgreSQL (schema: gateway_schema)              | [x]    | `DATABASES['default']['OPTIONS']`    |
| CFG-05 | Static files через WhiteNoise                    | [x]    | `STATIC_ROOT`, `WhiteNoiseMiddleware`|
| CFG-06 | Graceful degradation при падінні сервісів        | [x]    | Health check + 502/504 відповіді     |

### 2.7 Моніторинг та observability

| ID     | Вимога                                           | Статус | Джерело                              |
|--------|--------------------------------------------------|--------|--------------------------------------|
| MON-01 | Детальний health check                           | [x]    | `HealthCheckView`                    |
| MON-02 | Структуровані логи з timestamp, level, name      | [x]    | `LOGGING` formatter                  |
| MON-03 | Prometheus метрики (requests count, latency, errors) | [ ] | —                                    |
| MON-04 | OpenTelemetry tracing                            | [ ]    | —                                    |
| MON-05 | SLO 99.9%                                        | [ ]    | —                                    |

### 2.8 Кешування відповідей (Response Caching)

| ID       | Вимога                                           | Статус | Коментар                              |
|----------|--------------------------------------------------|--------|---------------------------------------|
| CACHE-01 | Кешування GET-запитів у gateway (MD5 key)         | [ ]    | планується                            |
| CACHE-02 | TTL 60 секунд, тільки 200 OK JSON                | [ ]    | планується                            |
| CACHE-03 | Інвалідатори з мікросервісів                     | [ ]    | планується                            |

### Roadmap (актуальний)

| Етап           | Термін         | Пріоритетні задачі                                          |
|----------------|----------------|-------------------------------------------------------------|
| **MVP+**       | грудень 2025   | Response caching, retry + circuit breaker, helmet headers   |
| **Production** | січень 2026    | Prometheus метрики, OpenTelemetry, mTLS                     |
| **Enterprise** | березень 2026+ | gRPC gateway, GraphQL фасад, SDK генерація, версіонування   |
