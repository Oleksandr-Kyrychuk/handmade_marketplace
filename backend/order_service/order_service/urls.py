# order_service/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from orders.views import OrderViewSet, CartViewSet, HealthCheckView

router = DefaultRouter(trailing_slash=False)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('health', HealthCheckView.as_view(), name='health_check'),
    path('', include(router.urls)),

    # OpenAPI Schema
    path('schema', SpectacularAPIView.as_view(), name='schema'),
    path('schema.<str:format>', SpectacularAPIView.as_view(), name='schema'),
    path('swagger', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]