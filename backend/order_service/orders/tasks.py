from celery import shared_task
from django.conf import settings
from .models import Order
import requests
import logging
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def reserve_stock(self, order_id):
    try:
        order = Order.objects.get(id=order_id)
        for item in order.items.all():
            response = requests.patch(
                f"{settings.PRODUCT_SERVICE_URL}/products/{item.product_id}/reserve/",
                json={
                    "quantity": item.quantity,
                    "order_id": str(order.id)
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code != 200:
                logger.error(f"Reserve failed for {item.product_id}: {response.text}")
                order.status = 'failed'
                order.save()
                send_order_notification.delay(order.id, 'failed')
                return {"success": False, "error": "stock_reserve_failed"}

        order.status = 'reserved'
        order.save()
        logger.info(f"Stock reserved for order {order_id}")
    except Exception as e:
        logger.error(f"Reserve task error: {e}")
        raise self.retry(exc=e)

@shared_task
def send_order_notification(order_id, event):
    order = Order.objects.get(id=order_id)
    try:
        # Отримати email з User Service
        user_resp = requests.get(
            f"{settings.USER_SERVICE_URL}/api/users/{order.customer_id}/",
            timeout=5
        )
        user_resp.raise_for_status()
        email = user_resp.json().get('email', 'default@email.com')

        requests.post(
            f"{settings.USER_SERVICE_URL}/api/emails/send/",
            json={
                "recipient": email,
                "subject": f"Замовлення #{order.id} — {event}",
                "message": f"Статус: {event}"
            },
            timeout=5
        )
    except Exception as e:
        logger.error(f"Notification error for order {order_id}: {e}")

@shared_task
def cancel_pending_orders():
    from django.utils import timezone
    from datetime import timedelta
    pending = Order.objects.filter(
        status='pending',
        created_at__lt=timezone.now() - timedelta(hours=24)
    )
    for order in pending:
        order.status = 'cancelled'
        order.save()
        send_order_notification.delay(order.id, 'cancelled')