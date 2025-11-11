# product_service/urls.py
"""
product_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
# product_service/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from products.views import ProductViewSet, ModerationViewSet, HealthCheckView, ReviewViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'products', ProductViewSet)
router.register(r'moderation', ModerationViewSet, basename='moderation')
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('health', HealthCheckView.as_view(), name='health_check'),
    path('', include(router.urls)),

    # OpenAPI Schema
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
