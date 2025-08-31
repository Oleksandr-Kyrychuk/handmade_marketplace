"""
URL configuration for user_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#backend/user_service/user_service/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import (
    HealthCheckView, RegisterView, VerifyEmailView, ResendVerificationCodeView,
    LoginView, CustomTokenRefreshView, PasswordResetRequestView,
    PasswordResetConfirmView, UserViewSet, UserProfileView, LogoutView
)
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthCheckView.as_view(), name='health'),
    path('users/register/', RegisterView.as_view(), name='register'),
    path('users/verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('users/resend-verification/', ResendVerificationCodeView.as_view(), name='resend-verification'),
    path('users/login/', LoginView.as_view(), name='login'),
    path('users/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('users/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('users/password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('users/profile/', UserProfileView.as_view(), name='profile'),
    path('users/logout/', LogoutView.as_view(), name='logout'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),  # Додано для документації
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Додано для Swagger UI
] + router.urls + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)