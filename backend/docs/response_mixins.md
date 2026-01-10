
# Документація API: Уніфікація відповідей та вьюшки в мікросервісах

**Мета**  
Документація для фронтенд-розробників (як інтегруватися з API) та для бекенд-розробників (нагадування про структуру, чому так зроблено, і як підтримувати).

**Джерела**  
`views.py` з сервісів (`product_service`, `user_service`, `order_service`) та `mixins.py`.



## 1. Загальний огляд уніфікації відповідей

У всіх сервісах застосовується **UnifiedResponseMixin** для стандартизації відповідей API.

### Формат уніфікованої відповіді

```json
{
  "success": true | false,
  "data":    any | null,
  "errors":  array | null,
  "message": string | null
}
```

- **success** — `true`, якщо статус-код < 400  
- **data** — основні дані (об'єкт, список тощо) або `null`  
- **errors** — масив об'єктів (тільки при помилці):

```json
[
  {
    "field": "email" | null,
    "message": "Email вже існує",
    "code": "validation_error" | "error"
  }
]
```

- **message** — опціональне текстове повідомлення

### Правила роботи mixin

- Якщо відповідь вже містить поле `"success"` (наприклад, пагінація) — mixin **не змінює** структуру.  
- Неуніфіковані відповіді використовуються лише в таких випадках:  
  - JWT-ендпоінти (`/login`, `/token/refresh`)  
  - Health-check (`/health`)  
  - Адмінські viewsets (`UserViewSet`)

## 2. User Service (user_service/views.py)

| Ендпоінт / Вьюшка                              | Метод                  | Уніфікація | Успішна відповідь приклад                                      | Помилка приклад                                                                | Примітка                              |
|------------------------------------------------|------------------------|------------|----------------------------------------------------------------|--------------------------------------------------------------------------------|---------------------------------------|
| /register (RegisterView)                       | POST                   | Так        | {"success": true, "message": "Registration successful"} + кука | {"success": false, "errors": [{"field": "email", "message": "Email вже існує"}]} | Реєстрація + сесійна кука            |
| /verify-email/{uidb64}/{token}                 | GET                    | Так        | {"success": true, "message": "Email verified successfully"}    | {"success": false, "errors": [{"message": "Invalid token or expired"}]}       | Верифікація email                     |
| /resend-verification                           | POST                   | Так        | {"success": true, "message": "Новий код відправлено"} + кука   | {"success": false, "errors": [{"message": "Зачекайте 60 секунд"}]}            | Повторна відправка + rate-limit       |
| /login (LoginView)                             | POST                   | Ні         | {"access": "...", "refresh": "..."}                            | {"detail": "No active account found"}                                          | Стандартний JWT                       |
| /token/refresh (CustomTokenRefreshView)        | POST                   | Ні         | {"access": "..."}                                              | {"detail": "Token is invalid"}                                                 | JWT refresh                           |
| /password-reset-request                        | POST                   | Так        | {"success": true, "message": "Password reset email sent"}      | {"success": false, "errors": [{"message": "User not found"}]}                 | Запит скидання паролю                 |
| /password-reset-confirm/{uidb64}/{token}       | POST                   | Так        | {"success": true, "message": "Password reset successful"}      | {"success": false, "errors": [{"message": "Invalid token"}]}                  | Підтвердження скидання                |
| /users/ (UserViewSet)                          | GET/PUT/PATCH/DELETE   | Ні         | [{"id": 1, "email": "..."}] або пагінація                      | {"detail": "Permission denied"}                                                | Тільки для адмінів                    |
| /profile (UserProfileView)                     | GET/PUT/PATCH          | Так        | {"success": true, "data": {"email": "...", "avatar": "..."}}   | {"success": false, "errors": [{"field": "password", "message": "Too short"}]} | Профіль користувача                   |
| /logout (LogoutView)                           | POST                   | Так        | {"success": true, "message": "Logout successful"}              | {"success": false, "errors": [{"message": "Invalid token"}]}                   | Blacklist refresh-токена              |
| /health (HealthCheckView)                      | GET                    | Ні         | {"status": "ok", "services": {"redis": {"status": "ok"}, ...}} | 503 з {"status": "error", ...}                                                 | Моніторинг                            |

## 3. Product Service (product_service/views.py)

| Ендпоінт / Вьюшка                              | Метод                  | Уніфікація | Успішна відповідь приклад                                      | Помилка приклад                                                                | Примітка                              |
|------------------------------------------------|------------------------|------------|----------------------------------------------------------------|--------------------------------------------------------------------------------|---------------------------------------|
| /products/ (ProductViewSet)                    | GET/POST/PUT/PATCH/DELETE | Так        | {"success": true, "data": [{"id": 1, "name": "Product", ...}]} | {"success": false, "errors": [{"message": "Авторизація обов'язкова"}]}        | CRUD продуктів + фільтри              |
| /products/{id}/upload-image                    | POST                   | Так        | {"success": true, "message": "Image uploaded"}                 | {"success": false, "errors": [{"message": "Invalid image"}]}                   | Завантаження зображення               |
| /products/{id}/moderate                        | POST                   | Так        | {"success": true, "message": "Product схвалено"}               | {"success": false, "errors": [{"detail": "Product не знайдено"}]}             | Модерація (адміни)                    |
| /reviews/ (ReviewViewSet)                      | GET/POST/PUT/PATCH/DELETE | Так        | {"success": true, "data": [{"id": 1, "comment": "...", "rating": 5}]} | {"success": false, "errors": [{"message": "Ви не можете редагувати цей відгук"}]} | Відгуки + модерація                   |
| /health (HealthCheckView)                      | GET                    | Ні         | {"status": "ok", "services": {...}}                            | —                                                                              | Моніторинг                            |

## 4. Order Service (order_service/views.py)

| Ендпоінт / Вьюшка                              | Метод                  | Уніфікація | Успішна відповідь приклад                                      | Помилка приклад                                                                | Примітка                              |
|------------------------------------------------|------------------------|------------|----------------------------------------------------------------|--------------------------------------------------------------------------------|---------------------------------------|
| /carts/ (CartViewSet)                          | GET/POST/DELETE        | Так        | {"success": true, "data": [{"product_id": 1, "quantity": 2}]}  | {"success": false, "errors": [{"message": "Invalid data"}]}                    | Кошик користувача                     |
| /orders/ (OrderViewSet)                        | GET/POST/PUT/PATCH/DELETE | Так        | {"success": true, "data": [{"id": 1, "total_amount": 200, "status": "pending"}]} | {"success": false, "errors": [{"message": "Invalid status"}]}                  | CRUD замовлень                        |
| /orders/create-from-cart                       | POST                   | Так        | {"success": true, "data": {"id": 1, ...}}                      | {"success": false, "errors": [{"message": "Кошик порожній"}]}                  | Замовлення з кошика                   |
| /orders/{id}/change-status                     | POST                   | Так        | {"success": true, "message": "updated"}                        | {"success": false, "errors": [{"message": "Invalid status"}]}                  | Зміна статусу                         |
| /health (HealthCheckView)                      | GET                    | Ні         | {"status": "ok", "services": {...}}                            | —                                                                              | Моніторинг                            |

## 5. Рекомендації

**Фронтенд:**
- Обробляйте `success` глобально (наприклад, axios interceptor)
- JWT-ендпоінти — стандартний формат, не обгортати
- Health — не використовуйте в UI

**Бекенд:**
- Нова вьюшка → додавати mixin, якщо не JWT/health/адмін
- Оновлення mixin → копіювати вручну в усі сервіси
- Тестуйте: `assert 'success' in response.data`
