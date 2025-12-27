from drf_spectacular.utils import extend_schema, extend_schema_view
import uuid
from django.utils.timezone import now
from datetime import timedelta
from rest_framework import viewsets, permissions, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django_filters.rest_framework import DjangoFilterBackend
from .filters import UserFilter
from django.contrib.auth import get_user_model
from django.conf import settings
from .permissions import HasRolePermission
from .models import User
from django.core.cache import cache
from redis.exceptions import RedisError
from .serializers import (
    UserSerializer, RegisterSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, VerifyEmailSerializer, LoginSerializer,
    ResendVerificationCodeSerializer, UserProfileSerializer, HealthCheckSerializer
)
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
import logging
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.pagination import PageNumberPagination
from users.tasks import send_verification_email, send_password_reset_email
from users.tasks import mask_email

logger = logging.getLogger(__name__)
User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "prev": self.get_previous_link(),
            "results": data
        })

@extend_schema(tags=["registration"], summary="Реєстрація нового користувача")
class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        tags=["auth"],
        summary="Реєстрація нового користувача",
        request=RegisterSerializer,
        responses={201: UserSerializer},
        description="""
        Обов'язкове поле `agree_terms=true` — користувач підтверджує, що ознайомлений 
        з умовами використання та політикою конфіденційності.
        """
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # Надсилаємо лист асинхронно
        send_verification_email.delay(user.id)

        # Генеруємо унікальний токен для сесії підтвердження
        session_token = str(uuid.uuid4())

        # Зберігаємо в кеші на 15 хвилин (ключ — токен, значення — user.id або email)
        cache.set(f"email_confirm_session:{session_token}", user.email, timeout=900)

        response = Response({"success": True}, status=status.HTTP_201_CREATED)

        # Встановлюємо cookie
        response.set_cookie(
            key='email_confirm_session',
            value=session_token,
            max_age=900,  # 15 хвилин
            secure=not settings.DEBUG,  # в проді буде True
            httponly=True,
            samesite='Strict'
        )

        return response


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyEmailSerializer

    @extend_schema(tags=["auth"], summary="Підтвердження email")
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            # Безпечна перевірка token + час створення
            if user.verification_token_created_at and \
               default_token_generator.check_token(user, token) and \
               (now() - user.verification_token_created_at) < timedelta(hours=1):
                user.is_verified = True
                user.save()
                return Response({"success": True}, status=status.HTTP_200_OK)
            return Response({"errors": "Invalid token or expired"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationCodeView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'resend'  # Використовує 'resend': '5/minute' з settings

    @extend_schema(
        tags=["auth"],
        summary="Повторна відправка коду верифікації",
        request=ResendVerificationCodeSerializer,  # Якщо fallback на body
        responses={200: dict},  # OpenAPI spec
        description="Спробує використати сесію з куки. Якщо ні — очікує email у body. Rate-limited."
    )
    def post(self, request):
        email = None
        session_token = request.COOKIES.get('email_confirm_session')

        # Крок 1: Спроба з куки (основний шлях для свіжої реєстрації)
        if session_token:
            email = cache.get(f"email_confirm_session:{session_token}")
            if email:
                logger.info(f"Resend attempt via cookie for masked email: {mask_email(email)}")  # З tasks.py

        # Крок 2: Fallback на body, якщо куки немає
        if not email:
            serializer = ResendVerificationCodeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    "success": False,
                    "errors": serializer.errors,
                    "require_email_input": True  # Для фронту: показати поле
                }, status=status.HTTP_400_BAD_REQUEST)
            email = serializer.validated_data['email']
            logger.info(f"Resend attempt via body for masked email: {mask_email(email)}")

        # Крок 3: Загальна логіка (atomic для consistency)
        with transaction.atomic():
            user = get_object_or_404(User, email=email)
            if user.is_verified:
                raise ValidationError({"email": "Email вже підтверджений."})

            # Додатковий cache-based rate limit по email (на додачу до DRF throttle по IP)
            cache_key = f"resend_email_limit:{email}"
            if cache.get(cache_key):
                logger.warning(f"Rate limit hit for email: {mask_email(email)}")
                return Response({
                    "success": False,
                    "message": "Зачекайте 60 секунд перед повторною відправкою"
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            cache.set(cache_key, 1, 60)

            # Оновлення timestamp (щоб токен не протух)
            user.verification_token_created_at = now()
            user.save()

        # Крок 4: Асинхронна відправка
        send_verification_email.delay(user.id)

        # Крок 5: Регенерація та оновлення куки (завжди, навіть якщо був body)
        new_token = str(uuid.uuid4())
        cache.set(f"email_confirm_session:{new_token}", email, 900)  # 15 хв

        response = Response({"success": True, "message": "Новий код відправлено"}, status=status.HTTP_200_OK)
        response.set_cookie(
            key='email_confirm_session',
            value=new_token,
            max_age=900,
            secure=not settings.DEBUG,
            httponly=True,
            samesite='Strict'
        )

        logger.info(f"Resend successful for masked email: {mask_email(email)}")
        return response

@extend_schema(tags=["authentication"], summary="Логін користувача")
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    @extend_schema(tags=["auth"], summary="Логін користувача")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(tags=["auth"], summary="Оновлення токену")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["auth"], summary="Запит на скидання паролю")
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            send_password_reset_email.delay(user.id)
            return Response({"success": True}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"errors": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["auth"], summary="Підтвердження скидання паролю")
    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"success": True}, status=status.HTTP_200_OK)
            return Response({"errors": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["users"])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [HasRolePermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    allowed_roles = ['admin']
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'put', 'patch', 'delete']

@extend_schema_view(
    get=extend_schema(summary="Отримати профіль користувача", tags=["profile"]),
    put=extend_schema(summary="Повне оновлення профілю", tags=["profile"]),
    patch=extend_schema(summary="Часткове оновлення профілю", tags=["profile"]),
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(tags=["auth"], summary="Логаут користувача")
    def post(self, request):
        try:
            # Підтримуємо обидва варіанти: "refresh" і "refresh_token"
            refresh_token = request.data.get("refresh") or request.data.get("refresh_token")
            if not refresh_token:
                return Response({"errors": "Refresh token is required"}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"success": True, "detail": "Logout successful"}, status=200)
        except TokenError as e:
            return Response({"errors": "Invalid or already blacklisted token"}, status=400)
        except Exception as e:
            return Response({"errors": str(e)}, status=400)


class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = HealthCheckSerializer

    @extend_schema(
        tags=["health"],
        summary="Перевірка здоров'я сервісів",
        request=None,
        responses={200: HealthCheckSerializer, 503: HealthCheckSerializer}
    )
    def get(self, request):
        results = {}
        all_healthy = True

        try:
            cache.get('health_check_test')
            results['redis'] = {'status': 'ok'}
        except RedisError:
            results['redis'] = {'status': 'error'}
            all_healthy = False

        try:
            from django.db import connection
            connection.ensure_connection()
            results['database'] = {'status': 'ok'}
        except Exception:
            results['database'] = {'status': 'error'}
            all_healthy = False

        overall_status = 'ok' if all_healthy else 'error'
        return Response({
            'status': overall_status,
            'services': results
        }, status=200 if all_healthy else 503)
