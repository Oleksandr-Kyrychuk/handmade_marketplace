from celery import shared_task
from django.conf import settings
from django.db import transaction
from .models import Category, ProductImage, Review, Product
import cloudinary.uploader
import logging
import requests

cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    name="products.tasks.upload_image_to_cloudinary",
    max_retries=3,
    default_retry_delay=60,
    queue="images"
)
def upload_image_to_cloudinary(self, model_type, instance_id, user_id, image_data, image_name):
    try:
        upload_result = cloudinary.uploader.upload(
            image_data,
            public_id=image_name.rsplit('.', 1)[0],
            resource_type="image"
        )
        image_url = upload_result["url"]
        logger.info(f"Image uploaded to Cloudinary: {image_url}")

        with transaction.atomic():
            if model_type == "category":
                category = Category.objects.get(id=instance_id)
                category.category_image = image_url
                category.save()
                logger.info(f"Updated category {instance_id} with image URL: {image_url}")
            elif model_type == "product":
                product_image = ProductImage.objects.create(
                    product_id=instance_id,
                    image_url=image_url
                )
                logger.info(f"Created ProductImage for product {instance_id} with URL: {image_url}")
            else:
                raise ValueError(f"Invalid model_type: {model_type}")

        return {"success": True, "image_url": image_url}

    except Exception as e:
        logger.error(f"Error in upload_image_to_cloudinary for {model_type} {instance_id} by user {user_id}: {str(e)}")
        raise self.retry(exc=e)

@shared_task(queue='moderation')
def send_moderation_notification(content_type, content_id, is_approved, recipient_email):
    try:
        response = requests.post(
            f"{settings.USER_SERVICE_URL}/api/emails/send/",
            json={
                'recipient': recipient_email,
                'subject': f"{content_type.capitalize()} {'схвалено' if is_approved else 'відхилено'}",
                'message': f"Ваш {content_type} (ID: {content_id}) був {'схвалений' if is_approved else 'відхилений'} адміністратором."
            },
            timeout=5
        )
        response.raise_for_status()
        logger.info(f"Moderation notification for {content_type} {content_id} sent to {recipient_email}")
    except requests.RequestException as e:
        logger.error(f"Error sending moderation notification for {content_type} {content_id}: {str(e)}")

@shared_task(
    bind=True,
    name="products.tasks.moderate_content",
    max_retries=3,
    default_retry_delay=60,
    queue="auto_moderation"
)
def moderate_content(self, model_type, instance_id, text):
    try:
        response = requests.post(
            "http://127.0.0.1:8001/moderate",
            json={"text": text},
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        is_toxic = result["is_toxic"]
        score = result["score"]

        with transaction.atomic():
            if model_type == "product":
                obj = Product.objects.get(id=instance_id)
            elif model_type == "review":
                obj = Review.objects.get(id=instance_id)
            else:
                raise ValueError(f"Invalid model_type: {model_type}")
            obj.is_approved = not is_toxic
            obj.save()

        if is_toxic:
            recipient_email = obj.vendor_id if model_type == "product" else obj.user_id
            recipient_email = self._get_user_email(recipient_email)
            send_moderation_notification.delay(model_type, instance_id, False, recipient_email)
        logger.info(f"Moderated {model_type} {instance_id}: is_toxic={is_toxic}, score={score}")
    except Exception as e:
        logger.error(f"Error moderating {model_type} {instance_id}: {str(e)}")
        raise self.retry(exc=e)

    def _get_user_email(self, user_id):
        try:
            response = requests.get(
                f"{settings.USER_SERVICE_URL}/api/users/{user_id}/",
                timeout=5
            )
            response.raise_for_status()
            return response.json().get('email', '')
        except requests.RequestException as e:
            logger.error(f"Error fetching email for user {user_id}: {str(e)}")
            return ''
