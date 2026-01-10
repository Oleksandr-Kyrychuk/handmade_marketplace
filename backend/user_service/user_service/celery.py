import os
from celery import Celery
import django
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')
django.setup()


celery_app = Celery('user_service')

# Завжди беремо конфіг з Django settings
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматично реєструємо таски з усіх INSTALLED_APPS
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
