# api_gateway/app/management/commands/fetch_schema.py

import requests
import json
import logging
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch OpenAPI schemas from all services and cache them'

    def handle(self, *args, **kwargs):
        services = {
            'user_service': f"{settings.USER_SERVICE_URL}/schema/",
            'product_service': f"{settings.PRODUCT_SERVICE_URL}/schema/",
            'order_service': f"{settings.ORDER_SERVICE_URL}/schema/",
        }

        headers = {'Accept': 'application/json'}

        for name, url in services.items():
            for attempt in range(5):
                try:
                    logger.info(f"Fetching {name} from {url}")
                    response = requests.get(url, headers=headers, timeout=20)

                    if response.status_code == 406:
                        logger.warning("406 → forcing JSON")
                        response = requests.get(f"{url}?format=json", headers=headers, timeout=20)

                    response.raise_for_status()
                    schema = response.json()  # Тепер 100% JSON

                    # Зберігаємо у файл (для дебага)
                    filename = f'app/{name}_schema.json'
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(schema, f, indent=2, ensure_ascii=False)

                    # Кешуємо в Redis
                    cache.set(f'{name}_schema', schema, timeout=3600)

                    self.stdout.write(self.style.SUCCESS(f'SUCCESS: {name} → cached + saved'))
                    break

                except requests.exceptions.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from {name}: {response.text[:200]}")
                    self.stdout.write(self.style.ERROR(f'JSON ERROR: {name}'))
                    time.sleep(5)
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed for {name}: {e}")
                    if attempt == 4:
                        self.stdout.write(self.style.ERROR(f'FAILED: {name}'))
                    time.sleep(5)