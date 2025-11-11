# api_gateway/app/management/commands/fetch_schema.py
import requests
import json
import logging
import time
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        services = {
            'user_service': f"{settings.USER_SERVICE_URL}/schema/",
            'product_service': f"{settings.PRODUCT_SERVICE_URL}/schema/",
            'order_service': f"{settings.ORDER_SERVICE_URL}/schema/",
        }

        headers = {'Accept': 'application/json'}  # ПРАВИЛЬНИЙ Accept

        for name, url in services.items():
            for attempt in range(5):
                try:
                    logger.info(f"Fetching {name} from {url}")
                    response = requests.get(url, headers=headers, timeout=20)

                    if response.status_code == 406:
                        response = requests.get(url + "?format=openapi", timeout=20)

                    response.raise_for_status()
                    schema = response.json()

                    with open(f'app/{name}_schema.json', 'w', encoding='utf-8') as f:
                        json.dump(schema, f, indent=2, ensure_ascii=False)

                    self.stdout.write(self.style.SUCCESS(f'Success: {name}'))
                    break

                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed for {name}: {e}")
                    if attempt == 4:
                        self.stdout.write(self.style.ERROR(f'FAILED: {name}'))
                    time.sleep(10)