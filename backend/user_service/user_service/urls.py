# user_service/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.views import (
    HealthCheckView, RegisterView, VerifyEmailView, ResendVerificationCodeView,
    LoginView, CustomTokenRefreshView, PasswordResetRequestView,
    PasswordResetConfirmView, UserViewSet, UserProfileView, LogoutView
)

router = DefaultRouter(trailing_slash=False)
router.register(r'users-list', UserViewSet, basename='users')

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('health', HealthCheckView.as_view(), name='health'),
                  path('register/', RegisterView.as_view(), name='register'),
                  path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
                  path('resend-verification/', ResendVerificationCodeView.as_view(), name='resend-verification'),
                  path('login/', LoginView.as_view(), name='login'),
                  path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
                  path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
                  path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(),
                       name='password-reset-confirm'),
                  path('profile/', UserProfileView.as_view(), name='profile'),
                  path('logout/', LogoutView.as_view(), name='logout'),

                  # OpenAPI Schema
                  path('schema/', SpectacularAPIView.as_view(), name='schema'),
                  path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
              ] + router.urls