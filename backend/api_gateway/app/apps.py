# api_gateway/app/apps.py
from django.apps import AppConfig
import threading
import time
import requests
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def background_schema_loader():
    # Ініціалізуємо змінні один раз
    attempt = 0
    max_sleep = 60  # максимальна затримка

    while True:
        success_count = 0
        total_services = 3  # user, product, order

        for service_name, url in [
            ('user_service', f'{settings.USER_SERVICE_URL}/schema'),
            ('product_service', f'{settings.PRODUCT_SERVICE_URL}/schema'),
            ('order_service', f'{settings.ORDER_SERVICE_URL}/schema'),
        ]:
            try:
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200:
                    cache.set(f'{service_name}_schema', resp.json(), timeout=3600)
                    logger.info(f"Successfully updated schema: {service_name}")
                    success_count += 1
                else:
                    logger.warning(f"Schema fetch failed ({resp.status_code}): {service_name}")
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch schema from {service_name}: {e}")

        # Логіка бекоффу тільки якщо ВСІ сервіси впали
        if success_count == total_services:
            attempt = 0  # все добре — скидаємо
        else:
            attempt += 1
            logger.warning(f"Schema sync failed for {total_services - success_count} service(s). Attempt: {attempt}")

        # Експоненційний бекофф з jitter
        sleep_time = min(2 ** attempt, max_sleep)
        jitter = sleep_time * 0.1 * (2 * (time.time() % 1) - 1)  # ±10%
        time.sleep(sleep_time + jitter)


class ApiGatewayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Запускаємо тільки один раз
        if not hasattr(self, 'schema_thread_started'):
            self.schema_thread_started = True
            thread = threading.Thread(target=background_schema_loader, daemon=True)
            thread.start()
            logger.info("Background schema loader started")