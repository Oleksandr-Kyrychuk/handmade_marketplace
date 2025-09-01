from django.core.management.base import BaseCommand
from django.core.cache import cache
import requests
import logging

from backend.api_gateway.app.urls import USER_SERVICE_URL

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetches and caches OpenAPI schema for user_service'

    def handle(self, *args, **options):
        try:
            response = requests.get(
                f'{USER_SERVICE_URL}/schema/',
                timeout=10
            )
            response.raise_for_status()
            schema = response.json()
            cache.set('user_service_schema', schema, timeout=3600)
            self.stdout.write(self.style.SUCCESS('Successfully fetched and cached gateway_service schema'))
        except requests.RequestException as e:
            logger.error(f"Failed to fetch user_service schema: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Failed to fetch gateway_service schema: {str(e)}'))