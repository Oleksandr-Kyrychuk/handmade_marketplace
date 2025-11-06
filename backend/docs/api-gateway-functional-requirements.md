# Функціональні Вимоги до API Gateway  
*Версія 1.0 — Enterprise-Ready API Gateway for Handmade Marketplace*

> **Мета**: Централізований вхід для всіх мікросервісів (User Service, Product Service), з проксі, кешуванням схем, health check, Swagger, безпекою.  
> **Стан**: 70% реалізованих вимог, 30% — у плані розширення.  
> **Технології**: Django, DRF, Redis (cache), drf-spectacular, requests, threading, JWT (проксі), OpenAPI merging.

---

## Легенда
- [x] — **вже реалізовано**  
- [ ] — **планується до реалізації**  
- [~] — **частково реалізовано**

---

## 2.1 Проксі-запити до мікросервісів

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| PROXY-01 | **Динамічний проксі** всіх HTTP-методів (GET, POST, PUT, DELETE) до `user-service` та `product-service` | [x] | `ProxyView.handle_request()` |
| PROXY-02 | **Проксі за шляхом**: `/users/...` → `http://user-service:8001/...` | [x] | `ProxyView` + `settings.USER_SERVICE_URL` |
| PROXY-03 | **Проксі за шляхом**: `/products/...` → `http://product-service:8002/...` | [x] | `ProxyView` + `settings.PRODUCT_SERVICE_URL` |
| PROXY-04 | **Проксі headers, body, query params** (повна прозорість) | [x] | `requests.request()` з `headers`, `data`, `params` |
| PROXY-05 | **Таймаут 20с** на кожен запит | [x] | `timeout=20` |
| PROXY-06 | **Обробка помилок**: 502/503 при таймауті, з'єднанні, HTTP помилках | [x] | `except Timeout`, `ConnectionError`, `RequestException` |
| PROXY-07 | **Логування помилок проксі** (target_url, status, message) | [x] | `logger.error()` |
| PROXY-08 | **Проксі JSON → JSON**, текст → текст | [x] | `resp.json()` або `resp.text` |
| PROXY-09 | **Проксі файлів (multipart)** — підтримується | [x] | `data=request.body` |
| PROXY-10 | **Проксі авторизації (JWT)** — передача `Authorization` header | [x] | `headers['Authorization']` |
| PROXY-11 | **Rate limiting на рівні gateway** | [x] | `UserRateThrottle`, `AnonRateThrottle` |
| PROXY-12 | **Circuit breaker** (наприклад, при 5+ помилках — fallback) | [ ] | — |
| PROXY-13 | **Retry з backoff** для проксі-запитів | [ ] | — |

---

## 2.2 Кешування OpenAPI схем

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| SCHEMA-01 | **Фоновий завантажувач схем** при старті (thread) | [x] | `background_schema_loader()` в `apps.py` |
| SCHEMA-02 | **Кеш схем в Redis** (ключ: `user_service_schema`, TTL 1 година) | [x] | `cache.set(..., timeout=3600)` |
| SCHEMA-03 | **Exponential backoff** при помилці (2^n, max 60с + jitter) | [x] | `sleep_time = min(2 ** attempt, max_sleep)` |
| SCHEMA-04 | **Авто-оновлення схем** кожні N секунд | [x] | Безкінечний цикл |
| SCHEMA-05 | **Логування помилок завантаження** | [x] | `logger.warning()` |
| SCHEMA-06 | **Fallback при відсутності схеми** → 502 | [x] | `MergedSchemaView` |
| SCHEMA-07 | **Авто-детект нових сервісів** (через env) | [x] | `USER_SERVICE_URL`, `PRODUCT_SERVICE_URL` |

---

## 2.3 Об’єднання OpenAPI документації

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| DOCS-01 | **Об’єднання схем** з `user_service` + `product_service` | [x] | `MergedSchemaView` |
| DOCS-02 | **Динамічні назви**: `User`, `Product` у Swagger | [x] | `urls.primaryName=User` |
| DOCS-03 | **Swagger UI** з перемикачем сервісів | [x] | `SpectacularSwaggerView` |
| DOCS-04 | **Root endpoint** `/` — список доступних шляхів | [x] | `RootView` |
| DOCS-05 | **Кеш схем для root** | [x] | `cache.get('user_service_schema')` |
| DOCS-06 | **Генерація клієнтів (SDK)** | [ ] | — |
| DOCS-07 | **Версіонування API** (v1, v2) | [ ] | — |

---

## 2.8 Health Check

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| HC-01 | **Health check `/health`** — Redis + мікросервіси + схеми | [x] | `HealthCheckView` |
| HC-02 | **Перевірка Redis** | [x] | `cache.get()` |
| HC-03 | **Перевірка мікросервісів** (HTTP GET `/health`) | [x] | `requests.get()` |
| HC-04 | **Перевірка схем у кеші** | [x] | `cache.get()` |
| HC-05 | **Повторні спроби (5 разів, 10с)** | [x] | `max_retries`, `retry_delay` |
| HC-06 | **Статус 200 (ok) / 503 (error)** | [x] | `status=200 if all_healthy else 503` |
| HC-07 | **Деталі помилок** у відповіді | [x] | `detail` |
| HC-08 | **Логування провалених перевірок** | [x] | `logger.error()` |

---

## 2.9 Безпека та стабільність

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| SEC-01 | **CORS** з дозволеними origins | [x] | `CORS_ALLOWED_ORIGINS` |
| SEC-02 | **CSRF protection** | [x] | Middleware |
| SEC-03 | **WhiteNoise** для статики | [x] | `WhiteNoiseMiddleware` |
| SEC-04 | **Throttling**: 1M/день (anon), 10M/день (user) | [x] | `REST_FRAMEWORK` |
| SEC-05 | **Логування всіх дій** (INFO для django, DEBUG для app) | [x] | `LOGGING` |
| SEC-06 | **Проксі JWT** — без валідації в gateway | [x] | Передача `Authorization` |
| SEC-07 | **Helmet headers** (HSTS, CSP) | [ ] | — |
| SEC-08 | **mTLS між gateway та сервісами** | [ ] | — |

---

## 2.10 Конфігурація та розгортання

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| CFG-01 | **.env підтримка** (local / prod) | [x] | `environ.Env.read_env()` |
| CFG-02 | **Docker-ready** (entrypoint, staticfiles) | [x] | `Dockerfile`, `staticfiles` |
| CFG-03 | **ASGI / WSGI** | [x] | `asgi.py`, `wsgi.py` |
| CFG-04 | **Redis cache** (TTL 1 година) | [x] | `CACHES` |
| CFG-05 | **PostgreSQL** (schema: `gateway_schema`) | [x] | `DATABASES['default']['OPTIONS']` |
| CFG-06 | **Graceful degradation** при недоступності сервісу | [x] | Health check + fallback |

---

## 2.11 API та клієнти

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| API-01 | **OpenAPI 3.0+** (merged) | [x] | `MergedSchemaView` |
| API-02 | **Swagger UI** з перемикачем | [x] | `swagger-ui?urls.primaryName=...` |
| API-03 | **Root JSON** — карта API | [x] | `RootView` |
| API-04 | **gRPC gateway** | [ ] | — |
| API-05 | **GraphQL фасад** | [ ] | — |

---

## 2.12 Моніторинг та observability

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| MON-01 | **Health check** (включаючи залежності) | [x] | `HealthCheckView` |
| MON-02 | **Логи з timestamp, level, name** | [x] | `LOGGING` |
| MON-03 | **Prometheus метрики** (requests, latency, errors) | [ ] | — |
| MON-04 | **Tracing (OpenTelemetry)** | [ ] | — |
| MON-05 | **SLO: 99.9% доступність** | [ ] | — |

---

## 2.13 Тестування

| ID | Вимога | Статус |
|----|-------|--------|
| TEST-01 | Unit + integration tests | [ ] |
| TEST-02 | Load testing (k6, Locust) | [ ] |
| TEST-03 | Chaos testing (сервіс down) | [ ] |

---

## 2.14 Кешування відповідей (Response Caching)

| ID | Вимога | Статус | Джерело |
|----|-------|-------|--------|
| CACHE-01 | Кешування GET-запитів у API Gateway | [] | `ProxyView.dispatch()` |
| CACHE-02 | Ключ: MD5(path + query) | [] | `get_cache_key()` |
| CACHE-03 | TTL: 60 секунд | [] | `cache.set(..., timeout=60)` |
| CACHE-04 | Тільки 200 OK, JSON | [] | Умова в `dispatch()` |
| CACHE-05 | Авто-інвалідатори в мікросервісах | [] | `invalidate_product_cache` |

## 2.15 Data Caching (мікросервіси)

| ID | Вимога | Статус | Джерело |
|----|-------|--------|--------|
| DATA-01 | Кеш профілів у User Service | [] | `user:profile:{id}` |
| DATA-02 | Кеш списків продуктів | [] | `product:list:*` |
| DATA-03 | Інвалідатори при змінах | [] | `cache.delete_pattern()` |

## План розширення (Roadmap)

| Етап | Термін | Вимоги |
|------|--------|-------|
| **MVP+** | ???    | Circuit breaker, retry |
| **Production** | ???    | Prometheus, tracing, helmet |
| **Enterprise** | ???    | mTLS, gRPC, GraphQL, SDK |
