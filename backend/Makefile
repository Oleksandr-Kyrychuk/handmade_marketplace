#!/usr/bin/make

DOCKER_COMPOSE_BIN := $(shell command -v docker-compose 2>/dev/null || echo "docker compose")

# Запуск усіх сервісів
up:
	@echo "🚀 Запуск усіх контейнерів (api_gateway, user_service, marketplace_database, redis)..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml up -d --build
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
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml up -d user_service
	@echo "⏳ Очікування запуску user_service..."
	@sleep 5
	@echo "✅ user_service запущено!"

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

# Створення міграцій
makemigrations:
	@echo "🛠 Створення нових міграцій для user_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec user_service python manage.py makemigrations

# Виконання міграцій
migrate:
	@echo "🔄 Виконання міграцій для user_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec user_service python manage.py migrate

# Створення суперкористувача
super:
	@echo "👤 Створення суперкористувача для user_service..."
	$(DOCKER_COMPOSE_BIN) -f docker-compose.local.yml exec user_service python manage.py createsuperuser