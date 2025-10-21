-- Ініціалізація бази даних, користувачів і схем
CREATE USER dev WITH PASSWORD 'sysadmin';
ALTER USER dev CREATEDB;
CREATE DATABASE marketplace;
GRANT ALL PRIVILEGES ON DATABASE marketplace TO dev;

-- Підключаємося до БД marketplace
\c marketplace

-- Створюємо схеми
CREATE SCHEMA IF NOT EXISTS users_schema;
CREATE SCHEMA IF NOT EXISTS products_schema;
CREATE SCHEMA IF NOT EXISTS gateway_schema;

-- Надаємо права
GRANT ALL ON SCHEMA users_schema TO dev;
GRANT ALL ON SCHEMA products_schema TO dev;
GRANT ALL ON SCHEMA gateway_schema TO dev;

ALTER SCHEMA users_schema OWNER TO dev;
ALTER SCHEMA products_schema OWNER TO dev;
ALTER SCHEMA gateway_schema OWNER TO dev;