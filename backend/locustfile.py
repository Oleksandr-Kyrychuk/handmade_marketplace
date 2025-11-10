from locust import HttpUser, task, between

# Клас, що описує одного користувача
class WebsiteUser(HttpUser):
    # Затримка між запитами (щоб не спамити надто швидко)
    wait_time = between(1, 3)

    @task
    def get_products(self):
        # Один користувач виконує цей GET-запит
        self.client.get("/products")
