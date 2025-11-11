import logging
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from drf_spectacular.views import SpectacularSwaggerView
from drf_spectacular.utils import extend_schema

from .serializers import HealthCheckSerializer, EmptySerializer
from django.core.cache import cache
import requests
import time
import redis

logger = logging.getLogger(__name__)


# ============================
# Root View — головна сторінка
# ============================
class RootView(APIView):
    def get(self, request):
        user_schema = cache.get('user_service_schema', {})
        product_schema = cache.get('product_service_schema', {})
        order_schema = cache.get('order_service_schema', {})

        def extract_paths(schema):
            return list(schema.get('paths', {}).keys()) if schema else []

        available_services = {
            "user_service": extract_paths(user_schema),
            "product_service": extract_paths(product_schema),
            "order_service": extract_paths(order_schema),
        }

        return Response({
            "gateway": "Handmade Marketplace Gateway",
            "version": "1.0.0",
            "available_services": available_services,
            "docs": {
                "user_service": "/swagger-ui?urls.primaryName=User",
                "product_service": "/swagger-ui?urls.primaryName=Product",
                "order_service": "/swagger-ui?urls.primaryName=Order"
            },
            "endpoints": {
                "users": "/users/",
                "products": "/products/",
                "orders": "/orders/",
                "carts": "/carts/",
                "moderation": "/moderation/"
            }
        })


# ============================
# Health Check — перевірка всіх сервісів
# ============================
class HealthCheckView(APIView):
    throttle_classes = []
    serializer_class = HealthCheckSerializer

    @extend_schema(
        request=None,
        responses={200: HealthCheckSerializer, 503: HealthCheckSerializer},
        summary="Health check for API Gateway",
        description="Перевіряє Redis, User Service, Product Service, Order Service та кеш схем."
    )
    def get(self, request):
        results = {}
        all_healthy = True
        max_retries = 5
        retry_delay = 10

        # Redis
        try:
            cache.get('health_check_test')
            results['redis'] = {'status': 'ok'}
        except redis.RedisError as e:
            results['redis'] = {'status': 'error', 'detail': str(e)}
            all_healthy = False
            logger.error(f"Redis health check failed: {e}")

        # User Service
        for attempt in range(max_retries):
            try:
                resp = requests.get(f'{settings.USER_SERVICE_URL}/health', timeout=20)
                results['user_service'] = {'status': 'ok' if resp.status_code == 200 else 'error'}
                break
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    results['user_service'] = {'status': 'error', 'detail': str(e)}
                    all_healthy = False
                    logger.error(f"User Service health check failed: {e}")
                time.sleep(retry_delay)

        # Product Service
        for attempt in range(max_retries):
            try:
                resp = requests.get(f'{settings.PRODUCT_SERVICE_URL}/health', timeout=20)
                results['product_service'] = {'status': 'ok' if resp.status_code == 200 else 'error'}
                break
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    results['product_service'] = {'status': 'error', 'detail': str(e)}
                    all_healthy = False
                    logger.error(f"Product Service health check failed: {e}")
                time.sleep(retry_delay)

        # Order Service
        for attempt in range(max_retries):
            try:
                resp = requests.get(f'{settings.ORDER_SERVICE_URL}/health', timeout=20)
                results['order_service'] = {'status': 'ok' if resp.status_code == 200 else 'error'}
                break
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    results['order_service'] = {'status': 'error', 'detail': str(e)}
                    all_healthy = False
                    logger.error(f"Order Service health check failed: {e}")
                time.sleep(retry_delay)

        # Кеш схем
        results['schema_cache'] = {
            'user_service': 'ok' if cache.get('user_service_schema') else 'missing',
            'product_service': 'ok' if cache.get('product_service_schema') else 'missing',
            'order_service': 'ok' if cache.get('order_service_schema') else 'missing',
        }

        overall_status = 'ok' if all_healthy else 'error'
        return Response(
            {'status': overall_status, 'services': results},
            status=200 if all_healthy else 503
        )


# ============================
# Merged OpenAPI Schema
# ============================
class MergedSchemaView(GenericAPIView):
    serializer_class = EmptySerializer

    def get(self, request):
        merged_schema = cache.get('merged_schema')
        if merged_schema:
            return Response(merged_schema)

        from drf_spectacular.generators import SchemaGenerator
        generator = SchemaGenerator()
        gateway_schema = generator.get_schema(request=request)

        # Отримуємо схеми з кешу
        user_schema = cache.get('user_service_schema', {})
        product_schema = cache.get('product_service_schema', {})
        order_schema = cache.get('order_service_schema', {})

        # Merge paths
        for schema in [user_schema, product_schema, order_schema]:
            gateway_schema['paths'].update(schema.get('paths', {}))

        # Merge components
        for schema in [user_schema, product_schema, order_schema]:
            for comp_type, comp_data in schema.get('components', {}).items():
                gateway_schema['components'].setdefault(comp_type, {}).update(comp_data)

        # Додаємо теги для Swagger UI
        gateway_schema['tags'] = [
            {"name": "User", "description": "User Service API"},
            {"name": "Product", "description": "Product Service API"},
            {"name": "Order", "description": "Order Service API"}
        ]

        cache.set('merged_schema', gateway_schema, timeout=3600)
        return Response(gateway_schema)


# ============================
# Proxy View — маршрутизація
# ============================
class ProxyView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @extend_schema(exclude=True)
    def handle_request(self, request, path):
        # === Чітка маршрутизація ===
        if path.startswith('users/') or path == 'users' or path.startswith('api/users'):
            service_name = 'user_service'
            clean_path = path.replace('users/', '', 1).replace('api/users/', 'api/users/', 1)
            target_url = f"{settings.USER_SERVICE_URL}/{clean_path or ''}"

        elif path.startswith('products/') or path == 'products' or path.startswith('api/products'):
            service_name = 'product_service'
            clean_path = path.replace('api/products/', '', 1)
            target_url = f"{settings.PRODUCT_SERVICE_URL}/api/products/{clean_path}"

        elif path.startswith('moderation/'):
            service_name = 'product_service'
            target_url = f"{settings.PRODUCT_SERVICE_URL}/{path}"

        elif path.startswith('orders/') or path == 'orders' or path.startswith('api/orders'):
            service_name = 'order_service'
            clean_path = path.replace('api/orders/', '', 1)
            target_url = f"{settings.ORDER_SERVICE_URL}/{clean_path or ''}"

        elif path.startswith('carts/') or path == 'carts' or path.startswith('api/carts'):
            service_name = 'order_service'
            clean_path = path.replace('api/carts/', '', 1)
            target_url = f"{settings.ORDER_SERVICE_URL}/{clean_path or ''}"

        else:
            logger.warning(f"No route for path: {path}")
            return Response({'error': f'No microservice for path: /{path}'}, status=404)

        # === Прокидуємо заголовки (включаючи Authorization) ===
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in ('host', 'content-length', 'connection', 'transfer-encoding')
        }
        if request.body:
            headers['Content-Length'] = str(len(request.body))

        try:
            resp = requests.request(
                method=request.method,
                url=target_url.rstrip('/') + '/',  # виправляємо подвійні слеші
                headers=headers,
                data=request.body,
                params=request.GET,
                allow_redirects=False,
                timeout=20
            )

            # Прокидуємо Content-Type
            response_headers = {}
            content_type = resp.headers.get('Content-Type')
            if content_type:
                response_headers['Content-Type'] = content_type

            if 'application/json' in content_type:
                try:
                    return Response(resp.json(), status=resp.status_code, headers=response_headers)
                except ValueError:
                    logger.error(f"Invalid JSON from {target_url}")
                    return Response({'error': 'Invalid JSON from service'}, status=502)
            else:
                return Response(resp.content, status=resp.status_code, headers=response_headers)

        except requests.Timeout:
            logger.error(f"Timeout: {service_name} -> {target_url}")
            return Response({'error': f'{service_name} timed out'}, status=504)
        except requests.ConnectionError:
            logger.error(f"Connection error: {service_name} -> {target_url}")
            return Response({'error': f'Cannot connect to {service_name}'}, status=502)
        except requests.RequestException as e:
            logger.error(f"Proxy error: {service_name} -> {target_url} | {e}")
            return Response({'error': f'Proxy error: {str(e)}'}, status=502)

    def get(self, request, path):
        return self.handle_request(request, path)

    def post(self, request, path):
        return self.handle_request(request, path)

    def put(self, request, path):
        return self.handle_request(request, path)

    def patch(self, request, path):
        return self.handle_request(request, path)

    def delete(self, request, path):
        return self.handle_request(request, path)


# ============================
# URL patterns
# ============================
urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('', RootView.as_view(), name='root'),
    path('health', HealthCheckView.as_view(), name='health'),
    path('schema/', MergedSchemaView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    re_path(r'^(?P<path>.*)/?$', ProxyView.as_view(), name='proxy'),  # дозволяє / і без /
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)