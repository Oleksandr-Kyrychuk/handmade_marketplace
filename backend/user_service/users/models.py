import random
import re
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.timezone import now
from datetime import timedelta
from django.core.validators import RegexValidator, MinLengthValidator
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from django.contrib.postgres.search import SearchVector
name_validator = RegexValidator(
    regex=r'^(?!-)[A-Za-zА-Яа-яїЇіІєЄґҐ]+(-[A-Za-zА-Яа-яїЇіІєЄґҐ]+)*(?<!-)$',
    message="Ім'я та прізвище: лише літери (кирилиця/латиниця), дефіс не на початку чи в кінці.",
    code='invalid_name'
)

def validate_email_custom(value):
    """Валідація email за суворими вимогами"""
    if not value or '@' not in value:
        raise ValidationError("Невірний формат email.")

    parts = value.rsplit('@', 1)
    if len(parts) != 2:
        raise ValidationError("Невірний формат email.")

    local, domain = parts

    # Локальна частина
    if not (1 <= len(local) <= 35):
        raise ValidationError("Локальна частина email повинна бути від 1 до 35 символів.")
    if local.startswith('.') or local.endswith('.'):
        raise ValidationError("Крапка не може бути на початку чи в кінці локальної частини.")
    if '..' in local:
        raise ValidationError("Крапки не можуть йти послідовно в локальній частині.")
    if not re.match(r'^[A-Za-z0-9!#$%&\'*+/=?^_`{|}~.-]{1,35}$', local):
        raise ValidationError(
            "Локальна частина email може містити латиницю, цифри та спеціальні символи !#$%&'*+/=?^_`{|}~.-")

    # Доменна частина
    if not (3 <= len(domain) <= 35):
        raise ValidationError("Доменна частина повинна бути від 3 до 35 символів.")
    if domain[0] in '-.' or domain[-1] in '-.':
        raise ValidationError("Дефіс або крапка не можуть бути на початку чи в кінці домену.")
    if '..' in domain:
        raise ValidationError("Крапки не можуть йти послідовно в домені.")
    if not re.match(r'^[A-Za-z0-9\-\.]+$', domain):
        raise ValidationError("Домен може містити лише латиницю, цифри, дефіс та крапку.")

    return value

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, surname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('roles', ['admin'])

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, surname, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    email = models.CharField(
        max_length=71,  # 35 + @ + 35
        unique=True,
        validators=[validate_email_custom],
        help_text="Email: локальна частина 1–35, домен 3–35, без послідовних крапок"
    )
    username = models.CharField(
        max_length=50,
        validators=[name_validator, MinLengthValidator(1)],
        help_text="Ім'я: 1–50 символів, кирилиця/латиниця, дефіс (не на початку/кінці)"
    )
    surname = models.CharField(
        max_length=50,
        validators=[name_validator, MinLengthValidator(1)],
        help_text="Прізвище: 1–50 символів, кирилиця/латиниця, дефіс (не на початку/кінці)"
    )
    avatar = CloudinaryField('image', blank=True, null=True)  # Додано поле для аватара
    roles = ArrayField(
        models.CharField(max_length=10, choices=ROLE_CHOICES),
        default=list,
        blank=True,
        db_index=True
    )
    is_verified = models.BooleanField(default=False, db_index=True)
    verification_token_created_at = models.DateTimeField(null=True, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'surname']

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.is_superuser and not self.roles:
                self.roles = ['user']
            super().save(*args, **kwargs)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector'], name='user_search_idx'),
        ]

    def __str__(self):
        return f"{self.username} (ID: {self.id})"

@receiver(post_save, sender=User)
def update_search_vector(sender, instance, **kwargs):
    User.objects.filter(pk=instance.pk).update(
        search_vector=(
            SearchVector('username', weight='A', config='simple') +
            SearchVector('surname', weight='B', config='simple')
        )
    )