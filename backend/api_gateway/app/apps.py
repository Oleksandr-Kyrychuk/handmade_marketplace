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
    max_sleep = 60
    attempt = 0
    while True:
        for service_name, url in [
            ('user_service', f'{settings.USER_SERVICE_URL}/schema'),
            ('product_service', f'{settings.PRODUCT_SERVICE_URL}/schema')
        ]:
            try:
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200:
                    cache.set(f'{service_name}_schema', resp.json(), timeout=3600)
                    attempt = 0  # reset backoff
            except Exception as e:
                logger.warning(f"Failed to fetch schema from {service_name}: {e}")
                attempt += 1
        sleep_time = min(2 ** attempt, max_sleep)
        time.sleep(sleep_time + (sleep_time * 0.1))  # jitter

class ApiGatewayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'  # або 'api_gateway.app', як у тебе

    def ready(self):
        threading.Thread(target=background_schema_loader, daemon=True).start()

