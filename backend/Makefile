#!/usr/bin/make

DOCKER_COMPOSE_BIN := $(shell command -v docker-compose 2>/dev/null || echo "docker compose")

# Запуск усіх сервісів
up:
	@echo "🚀 Будуємо образи без кешу..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml build
	@echo "🚀 Запуск усіх контейнерів (api_gateway, user_service, product_service, marketplace_database, redis)..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml up -d
	@echo "⏳ Очікування запуску сервісів..."
	@sleep 10
	@echo "✅ Всі сервіси запущені!"

# Запуск лише api_gateway
gate:
	@echo "🚀 Запуск api_gateway..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml up -d api-gateway
	@echo "⏳ Очікування запуску api_gateway..."
	@sleep 5
	@echo "✅ api_gateway запущено!"

# Запуск лише user_service
user:
	@echo "🚀 Запуск user_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml up -d user-service
	@echo "⏳ Очікування запуску user_service..."
	@sleep 5
	@echo "✅ user_service запущено!"

# Запуск лише product_service
product:
	@echo "🚀 Запуск product_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml up -d product-service
	@echo "⏳ Очікування запуску product_service..."
	@sleep 5
	@echo "✅ product_service запущено!"

# Зупинка всіх контейнерів
down:
	@echo "🛑 Зупинка всіх контейнерів..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml down

# Перезапуск усіх контейнерів
restart: down up
	@echo "🔄 Перезапуск усіх контейнерів виконано!"

# Виведення логів всіх сервісів
logs:
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml logs -f

# Показати активні контейнери
ps:
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml ps

# Створення міграцій для user_service
makemigrations-user:
	@echo "Створення нових міграцій для user_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec user-service-local python manage.py makemigrations

# Створення міграцій для product_service
makemigrations-product:
	@echo "🛠 Створення нових міграцій для product_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec product-service python manage.py makemigrations

# Виконання міграцій для user_service
migrate-user:
	@echo "🔄 Виконання міграцій для user_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec user_service python manage.py migrate

# Виконання міграцій для product_service
migrate-product:
	@echo "🔄 Виконання міграцій для product_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec product-service python manage.py migrate

# Створення суперкористувача для user_service
super-user:
	@echo "👤 Створення суперкористувача для user_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec user_service python manage.py createsuperuser

# Створення суперкористувача для product_service
super-product:
	@echo "👤 Створення суперкористувача для product_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec product-service python manage.py createsuperuser

# Очищення користувачів
flush-user:
	@echo "Очищення користувачів в user_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec user-service python manage.py flush_users

# Заповнення користувачів
seed-user:
	@echo "Заповнення користувачів в user_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec user-service python manage.py seed_users

# Очищення продуктів
flush-product:
	@echo "Очищення продуктів в product_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec product-service python manage.py flush_products

# Заповнення продуктів
seed-product:
	@echo "Заповнення продуктів в product_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec product-service python manage.py seed_products


# === ТЕСТУВАННЯ ===

# Запуск тестів для product_service
test-product:
	@echo "Запуск тестів для product_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec product-service python manage.py test products --verbosity=2

# Запуск тестів з покриттям (coverage)
test-product-cov:
	@echo "Запуск тестів з покриттям (coverage)..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec product-service sh -c "\
		pip install coverage && \
		coverage run --source=products manage.py test products && \
		coverage report -m && \
		coverage html"

# Запуск тестів для user_service (на майбутнє)
test-user:
	@echo "Запуск тестів для user_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec user-service python manage.py test users --verbosity=2

# Запуск всіх тестів
test-all: test-user test-product
	@echo "Всі тести завершено!"

# Очищення кешу тестів
test-clean:
	@echo "Очищення кешу тестів..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec product-service rm -rf .coverage htmlcov/