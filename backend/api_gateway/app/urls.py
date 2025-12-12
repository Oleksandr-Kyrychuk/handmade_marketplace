import logging
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_spectacular.utils import extend_schema
from .serializers import HealthCheckSerializer, EmptySerializer
from django.core.cache import cache
import requests
import time
import redis

logger = logging.getLogger(__name__)

# ============================
# Root View
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
# Health Check
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
# Merged OpenAPI Schema — ВИПРАВЛЕНО
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

        external_schemas = [
            cache.get('user_service_schema', {}),
            cache.get('product_service_schema', {}),
            cache.get('order_service_schema', {}),
        ]

        # === 1. Збираємо всі теги один раз (правильно) ===
        all_tags = set()
        for schema in external_schemas:
            for tag in schema.get('tags', []):
                if isinstance(tag, dict):
                    all_tags.add(tag.get('name'))
                elif isinstance(tag, str):
                    all_tags.add(tag)

        existing_gateway_tags = {t.get('name') for t in gateway_schema.get('tags', [])}
        for tag_name in all_tags:
            if tag_name and tag_name not in existing_gateway_tags:
                gateway_schema.setdefault('tags', []).append({'name': tag_name})

        # === 2. Злиття paths з гарантією тегів ===
        service_to_tag = {
            'user': 'users',
            'product': 'products',
            'order': 'orders',
        }

        service_names = ['user', 'product', 'order']

        for i, schema in enumerate(external_schemas):
            service_key = service_names[i]
            default_tag = service_to_tag[service_key]

            for path, methods in schema.get('paths', {}).items():
                if path not in gateway_schema['paths']:
                    gateway_schema['paths'][path] = {}

                for method, operation in methods.items():
                    if method not in ('get', 'post', 'put', 'patch', 'delete', 'options', 'head', 'trace'):
                        continue

                    if method in gateway_schema['paths'][path]:
                        # Конфлікт — зливаємо теги + summary/description
                        existing_op = gateway_schema['paths'][path][method]
                        new_tags = operation.get('tags', [])
                        existing_tags = existing_op.get('tags', [])
                        combined = existing_tags + [t for t in new_tags if t not in existing_tags]
                        existing_op['tags'] = combined

                        if 'summary' not in existing_op and 'summary' in operation:
                            existing_op['summary'] = operation.get('summary')
                        if 'description' not in existing_op and 'description' in operation:
                            existing_op['description'] = operation.get('description')
                    else:
                        # Нова операція — копіюємо + гарантуємо тег
                        new_op = operation.copy()
                        if not new_op.get('tags'):
                            fallback = default_tag

                            if service_key == 'user':
                                if path.startswith('/users'): fallback = 'users'
                                elif any(path.startswith(p) for p in ['/login', '/logout', '/register', '/token', '/password']): fallback = 'auth'
                                elif path.startswith('/profile'): fallback = 'profile'
                            elif service_key == 'product':
                                if path.startswith('/products'): fallback = 'products'
                                elif path.startswith('/moderation'): fallback = 'moderation'
                                elif path.startswith('/reviews'): fallback = 'reviews'
                            elif service_key == 'order':
                                if path.startswith('/orders'): fallback = 'orders'
                                elif path.startswith('/carts') or path.startswith('/cart'): fallback = 'carts'

                            new_op['tags'] = [fallback]

                        gateway_schema['paths'][path][method] = new_op

            # Злиття components (schemas, responses тощо)
            for comp_type in ('schemas', 'parameters', 'responses', 'requestBodies', 'headers', 'securitySchemes'):
                if comp_type in schema.get('components', {}):
                    gateway_schema['components'].setdefault(comp_type, {}).update(
                        schema['components'][comp_type]
                    )

        # Кешуємо на 1 годину
        cache.set('merged_schema', gateway_schema, timeout=3600)
        return Response(gateway_schema)


# ============================
# Proxy View (без змін)
# ============================
@extend_schema(exclude=True)
class ProxyView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @extend_schema(exclude=True)
    def handle_request(self, request, path):
        target_url = None

        # === СПЕЦІАЛЬНІ ШЛЯХИ ===
        if path in (
            'users/health', 'users/schema/', 'products/health', 'products/schema/',
            'orders/health', 'orders/schema/'
        ):
            mapping = {
                'users/health': f"{settings.USER_SERVICE_URL}/health",
                'users/schema/': f"{settings.USER_SERVICE_URL}/schema/",
                'products/health': f"{settings.PRODUCT_SERVICE_URL}/health",
                'products/schema/': f"{settings.PRODUCT_SERVICE_URL}/schema/",
                'orders/health': f"{settings.ORDER_SERVICE_URL}/health",
                'orders/schema/': f"{settings.ORDER_SERVICE_URL}/schema/",
            }
            target_url = mapping.get(path)

        # === ЗВИЧАЙНІ ШЛЯХИ ===
        if path.startswith('users/'):
            inner_path = path[len('users/'):]
            target_url = f"{settings.USER_SERVICE_URL}/{inner_path}"
        elif path == 'users':
            target_url = settings.USER_SERVICE_URL
        elif path.startswith('products/'):
            inner_path = path[len('products/'):] or 'products'
            target_url = f"{settings.PRODUCT_SERVICE_URL}/{inner_path}"
        elif path == 'products':
            target_url = f"{settings.PRODUCT_SERVICE_URL}/products"
        elif path.startswith('moderation/'):
            inner_path = path[len('moderation/'):]
            target_url = f"{settings.PRODUCT_SERVICE_URL}/moderation/{inner_path}"
        elif path.startswith('orders/'):
            inner_path = path[len('orders/'):] or 'orders'
            target_url = f"{settings.ORDER_SERVICE_URL}/orders/{inner_path}"
        elif path == 'orders':
            target_url = f"{settings.ORDER_SERVICE_URL}/orders"
        elif path.startswith('carts/'):
            inner_path = path[len('carts/'):]
            target_url = f"{settings.ORDER_SERVICE_URL}/cart/{inner_path}"
        elif path == 'carts':
            target_url = f"{settings.ORDER_SERVICE_URL}/cart"

        if not target_url:
            logger.warning(f"No route for path: {path}")
            return Response({"error": "Not found"}, status=404)

        headers = {k: v for k, v in request.headers.items() if k.lower() not in ('host', 'content-length')}

        if 'Accept-Encoding' in headers:
            encodings = [enc.strip() for enc in headers['Accept-Encoding'].split(',')]
            safe_encodings = [enc for enc in encodings if enc.lower() not in {'br', 'brotli'}]
            if safe_encodings:
                headers['Accept-Encoding'] = ', '.join(safe_encodings)
            else:
                headers['Accept-Encoding'] = 'gzip, deflate'

        try:
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.body,
                params=request.GET,
                allow_redirects=False,
                timeout=30,
            )

            response_headers = {}
            content_type = resp.headers.get('Content-Type', '')
            if content_type:
                response_headers['Content-Type'] = content_type

            if 'application/json' in content_type:
                try:
                    return Response(resp.json(), status=resp.status_code, headers=response_headers)
                except ValueError:
                    logger.error(f"Invalid JSON from {target_url}: {resp.text[:200]}")
                    return Response({'error': 'Invalid JSON from upstream'}, status=502)
            else:
                return Response(resp.content, status=resp.status_code, headers=response_headers)

        except requests.Timeout:
            return Response({'error': 'Gateway timeout'}, status=504)
        except requests.ConnectionError:
            return Response({'error': 'Service unavailable'}, status=502)
        except requests.RequestException:
            return Response({'error': 'Proxy error'}, status=502)

    def get(self, request, path): return self.handle_request(request, path)
    def post(self, request, path): return self.handle_request(request, path)
    def put(self, request, path): return self.handle_request(request, path)
    def patch(self, request, path): return self.handle_request(request, path)
    def delete(self, request, path): return self.handle_request(request, path)


# ============================
# URL patterns
# ============================
urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('', RootView.as_view(), name='root'),
    path('health', HealthCheckView.as_view(), name='health'),
    path('schema', MergedSchemaView.as_view(), name='schema'),
    path('swagger-ui', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    re_path(r'^(?P<path>.*)/?$', ProxyView.as_view(), name='proxy'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)