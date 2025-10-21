from django.core.management.base import BaseCommand
from app.settings import USER_SERVICE_URL, PRODUCT_SERVICE_URL
import requests
import json
import logging
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch OpenAPI schemas from services and save them'

    def handle(self, *args, **kwargs):
        services = {
            'user_service': USER_SERVICE_URL + '/schema/',
            'product_service': PRODUCT_SERVICE_URL + '/schema/'
        }
        max_retries = 5  # Збільшено кількість спроб
        retry_delay = 10  # Збільшено затримку
        timeout = 20  # Збільшено таймаут

        for service_name, schema_url in services.items():
            for attempt in range(max_retries):
                try:
                    response = requests.get(schema_url, timeout=timeout)
                    response.raise_for_status()
                    schema = response.json()
                    with open(f'app/{service_name}_schema.json', 'w') as f:
                        json.dump(schema, f, indent=2)
                    self.stdout.write(self.style.SUCCESS(f'Successfully fetched schema for {service_name}'))
                    break
                except requests.RequestException as e:
                    logger.error(f'Attempt {attempt + 1} failed for {service_name}: {e}')
                    if attempt == max_retries - 1:
                        logger.error(f'Failed to fetch schema for {service_name}: {e}')
                        self.stdout.write(self.style.WARNING(f'Failed to fetch schema for {service_name}, continuing...'))
                    time.sleep(retry_delay)