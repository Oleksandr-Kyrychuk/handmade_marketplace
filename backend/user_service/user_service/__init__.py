import os
import django

# Це гарантує ініціалізацію навіть при імпорті модуля
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')
django.setup()

default_app_config = 'user_service.apps.UserServiceConfig'

from .celery import celery_app
__all__ = ('celery_app',)