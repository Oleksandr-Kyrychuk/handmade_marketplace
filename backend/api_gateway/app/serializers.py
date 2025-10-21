# /mnt/d/handmade_marketplace/backend/api_gateway/app/serializers.py
from rest_framework import serializers

class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=10)  # 'ok' або 'error'
    services = serializers.DictField(
        child=serializers.DictField(
            child=serializers.CharField(allow_null=True)
        )
    )

class ProxyErrorSerializer(serializers.Serializer):
    error = serializers.CharField(max_length=100)


class EmptySerializer(serializers.Serializer):
    pass


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            raise ValidationError({"detail": _("Невірний email або пароль.")})
        if not user.is_active:
            raise ValidationError({"detail": _("Користувач не активний.")})
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


