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
    path('health', HealthCheckView.as_view(), name='health'),
    path('', include(router.urls)),

    # OpenAPI Schema
    path('schema', SpectacularAPIView.as_view(), name='schema'),
    path('schema.<str:format>', SpectacularAPIView.as_view(), name='schema'),
    path('swagger', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]