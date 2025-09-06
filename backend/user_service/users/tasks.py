from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from django.db import transaction
import logging
import re
from django.core.cache import cache
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

logger = logging.getLogger(__name__)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

def is_throttled(email, action):
    key = f"email_{action}_{email}"
    if cache.get(key):
        logger.warning(f"Email throttled for {action} to {email}")
        return True
    cache.set(key, True, timeout=60)  # Блокування на 1 хвилину
    return False

@shared_task(name="users.tasks.delete_unverified_users")
def delete_unverified_users():
    try:
        with transaction.atomic():
            expiration_time = now() - timedelta(hours=24)
            unverified_users = User.objects.filter(
                is_verified=False,
                verification_token_created_at__lt=expiration_time
            )
            count = unverified_users.count()
            if count > 0:
                unverified_users.delete()
                logger.info(f"Deleted {count} unverified users.")
            else:
                logger.info("No unverified users found for deletion.")
    except Exception as e:
        logger.error(f"Error deleting unverified users: {str(e)}")
        send_mail(
            'Critical Error in Celery Task',
            f"Error in delete_unverified_users: {str(e)}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )

@shared_task(name="users.tasks.send_verification_email")
def send_verification_email(user_id):
    try:
        with transaction.atomic():
            user = User.objects.get(pk=user_id)
            if not is_valid_email(user.email):
                logger.warning(f"Invalid email format for user {user.id}: {user.email}")
                return
            if is_throttled(user.email, 'verify'):
                return
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            user.verification_token_created_at = now()
            user.save()
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"
            # print для дебагу:
            print(f"Verification URL for user {user.email}: {verification_url}")
            send_mail(
                'Підтвердження email',
                f'Вітаємо, {user.username}!\n\n'
                f'Перейдіть за посиланням для підтвердження email: {verification_url}\n'
                f'Посилання дійсне протягом 1 години.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            logger.info(f"Verification email sent to {user.email}")
    except Exception as e:
        logger.error(f"Error sending verification email to user {user_id}: {str(e)}")
        send_mail(
            'Error Sending Verification Email',
            f"Error sending verification email to user {user_id}: {str(e)}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )

@shared_task(name="users.tasks.send_password_reset_email")
def send_password_reset_email(user_id):
    try:
        with transaction.atomic():
            user = User.objects.get(pk=user_id)
            if not is_valid_email(user.email):
                logger.warning(f"Invalid email format for user {user.id}: {user.email}")
                return
            if is_throttled(user.email, 'reset'):
                return
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/{uid}/{token}"
            send_mail(
                'Скидання пароля',
                f'Вітаємо, {user.username}!\n\n'
                f'Перейдіть за посиланням для скидання пароля: {reset_url}\n'
                f'Посилання дійсне протягом 1 години.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            logger.info(f"Password reset email sent to {user.email}")
    except Exception as e:
        logger.error(f"Error sending password reset email to user {user_id}: {str(e)}")
        send_mail(
            'Error Sending Password Reset Email',
            f"Error sending password reset email to user {user_id}: {str(e)}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )