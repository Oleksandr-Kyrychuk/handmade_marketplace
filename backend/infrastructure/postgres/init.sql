-- init.sql
-- Базовий файл для ініціалізації бази даних
-- Тут можна додавати схеми, таблиці та індекси
-- Поки що залишаємо порожнім для міграцій

-- Приклад створення таблиці (розкоментувати при потребі):
-- CREATE TABLE IF NOT EXISTS users (
--     id SERIAL PRIMARY KEY,
--     username VARCHAR(255) NOT NULL UNIQUE,
--     email VARCHAR(255) NOT NULL UNIQUE,
--     created_at TIMESTAMP DEFAULT now()
-- );

-- Приклад створення індексу (розкоментувати при потребі):
-- CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE SCHEMA IF NOT EXISTS users_schema; CREATE SCHEMA IF NOT EXISTS gateway_schema;