from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
import os
import certifi
import re
import logging

logger = logging.getLogger(__name__)
os.environ['SSL_CERT_FILE'] = certifi.where()

from django.contrib.auth import get_user_model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=User.ROLE_CHOICES),
        required=False
    )
    avatar = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'surname', 'email', 'roles', 'avatar']

    def validate_avatar(self, value):
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise ValidationError("Розмір зображення не повинен перевищувати 5MB.")
        valid_types = ['image/png', 'image/jpeg']
        if value.content_type not in valid_types:
            raise ValidationError("Дозволені формати: PNG, JPEG.")
        return value

    def update(self, instance, validated_data):
        if 'avatar' in validated_data:
            instance.avatar = validated_data.pop('avatar')
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    avatar = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'surname', 'password', 'password_confirm', 'avatar']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise ValidationError({"password": _("Паролі не співпадають.")})

        password = data['password']
        if len(password) < 12:
            raise ValidationError({"password": _("Пароль має бути довжиною щонайменше 12 символів.")})
        if not re.search(r'[A-Z]', password):
            raise ValidationError({"password": _("Пароль має містити принаймні одну велику літеру.")})
        if not re.search(r'[0-9]', password):
            raise ValidationError({"password": _("Пароль має містити принаймні одну цифру.")})
        if not re.search(r'[!@#$%^&*]', password):
            raise ValidationError({"password": _("Пароль має містити принаймні один спеціальний символ.")})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)  # видаляємо зайве поле
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise ValidationError({"new_password": _("Паролі не співпадають.")})

        password = data['new_password']
        if len(password) < 12:
            raise ValidationError({"new_password": _("Пароль має бути довжиною щонайменше 12 символів.")})
        if not re.search(r'[A-Z]', password):
            raise ValidationError({"new_password": _("Пароль має містити принаймні одну велику літеру.")})
        if not re.search(r'[0-9]', password):
            raise ValidationError({"new_password": _("Пароль має містити принаймні одну цифру.")})
        if not re.search(r'[!@#$%^&*]', password):
            raise ValidationError({"new_password": _("Пароль має містити принаймні один спеціальний символ.")})
        return data


class ResendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        email = data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": [_("Користувача з таким email не знайдено.")]})
        if user.is_verified:
            raise serializers.ValidationError({"email": [_("Email вже підтверджений.")]})
        return data

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        user.verification_token_created_at = now()
        user.save()
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"
        send_mail(
            'Новий код підтвердження',
            f'Вітаємо, {user.username} ({user.email})!\n\n'
            f'Будь ласка, перейдіть за посиланням для підтвердження вашого email: {verification_url}\n'
            f'Посилання дійсне протягом 1 години.\n',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'surname', 'email', 'roles', 'avatar']


class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=10)
    services = serializers.DictField(
        child=serializers.DictField(
            child=serializers.CharField(allow_null=True)
        )
    )


class VerifyEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {
            "id": self.user.id,
            "username": self.user.username,
            "surname": self.user.surname,
            "email": self.user.email,
            "roles": self.user.roles,
        }
        return data


