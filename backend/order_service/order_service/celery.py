# order_service/order_service/celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')

app = Celery('order_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
