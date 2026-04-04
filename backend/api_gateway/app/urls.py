import logging

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from django.views.generic import RedirectView

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularSwaggerView

from django.core.cache import cache
import requests
import time
import redis

from .serializers import HealthCheckSerializer, EmptySerializer

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────
# Root endpoint
# ────────────────────────────────────────────────
class RootView(APIView):
    def get(self, request):
        user_schema    = cache.get('user_service_schema', {})
        product_schema = cache.get('product_service_schema', {})
        order_schema   = cache.get('order_service_schema', {})

        def extract_paths(schema):
            return list(schema.get('paths', {}).keys()) if schema else []

        return Response({
            "gateway": "Handmade Marketplace Gateway",
            "version": "1.0.0",
            "available_services": {
                "user_service":    extract_paths(user_schema),
                "product_service": extract_paths(product_schema),
                "order_service":   extract_paths(order_schema),
            },
            "docs": {
                "user_service":    "/swagger-ui?urls.primaryName=User",
                "product_service": "/swagger-ui?urls.primaryName=Product",
                "order_service":   "/swagger-ui?urls.primaryName=Order",
            },
            "endpoints": {
                "users":      "/api/users/",
                "products":   "/api/products/",
                "orders":     "/api/orders/",
                "carts":      "/api/carts/",
                "moderation": "/api/moderation/",
            }
        })


# ────────────────────────────────────────────────
# Health check
# ────────────────────────────────────────────────
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
        max_retries = 3           # зменшено до розумного значення
        retry_delay = 2

        # Redis
        try:
            cache.get('health_check_test_key')
            results['redis'] = {'status': 'ok'}
        except redis.RedisError as e:
            results['redis'] = {'status': 'error', 'detail': str(e)}
            all_healthy = False
            logger.error("Redis health check failed", exc_info=True)

        def check_service(name, url):
            nonlocal all_healthy
            for attempt in range(max_retries):
                try:
                    r = requests.get(url + '/health', timeout=10)
                    status = 'ok' if r.status_code == 200 else 'error'
                    results[name] = {'status': status}
                    if status != 'ok':
                        all_healthy = False
                    return
                except requests.RequestException as exc:
                    if attempt == max_retries - 1:
                        results[name] = {'status': 'error', 'detail': str(exc)}
                        all_healthy = False
                        logger.error(f"{name} health check failed after {max_retries} attempts", exc_info=True)
                    time.sleep(retry_delay)

        check_service('user_service',    settings.USER_SERVICE_URL)
        check_service('product_service', settings.PRODUCT_SERVICE_URL)
        check_service('order_service',   settings.ORDER_SERVICE_URL)

        results['schema_cache'] = {
            'user_service':    'ok' if cache.get('user_service_schema')    else 'missing',
            'product_service': 'ok' if cache.get('product_service_schema') else 'missing',
            'order_service':   'ok' if cache.get('order_service_schema')   else 'missing',
        }

        status_code = 200 if all_healthy else 503
        return Response(
            {'status': 'ok' if all_healthy else 'error', 'services': results},
            status=status_code
        )


# ────────────────────────────────────────────────
# Merged OpenAPI schema (без змін)
# ────────────────────────────────────────────────
class MergedSchemaView(GenericAPIView):
    serializer_class = EmptySerializer

    def get(self, request):
        if cached := cache.get('merged_schema'):
            return Response(cached)

        from drf_spectacular.generators import SchemaGenerator
        generator = SchemaGenerator()
        gateway_schema = generator.get_schema(request=request)

        external = [
            cache.get('user_service_schema', {}),
            cache.get('product_service_schema', {}),
            cache.get('order_service_schema', {}),
        ]

        # Збір тегів
        all_tags = set()
        for schema in external:
            for tag in schema.get('tags', []):
                name = tag['name'] if isinstance(tag, dict) else tag
                if name:
                    all_tags.add(name)

        existing = {t.get('name') for t in gateway_schema.get('tags', [])}
        for name in all_tags - existing:
            gateway_schema.setdefault('tags', []).append({'name': name})

        # Злиття шляхів (логіка збережена)
        service_to_tag = {'user': 'users', 'product': 'products', 'order': 'orders'}
        service_names = ['user', 'product', 'order']

        for i, schema in enumerate(external):
            svc = service_names[i]
            default_tag = service_to_tag[svc]

            for p, methods in schema.get('paths', {}).items():
                if p not in gateway_schema['paths']:
                    gateway_schema['paths'][p] = {}

                for m, op in methods.items():
                    if m not in {'get', 'post', 'put', 'patch', 'delete', 'options', 'head', 'trace'}:
                        continue

                    if m in gateway_schema['paths'][p]:
                        ex = gateway_schema['paths'][p][m]
                        ex['tags'] = list(set(ex.get('tags', []) + op.get('tags', [])))
                        if 'summary' not in ex and 'summary' in op:
                            ex['summary'] = op['summary']
                        if 'description' not in ex and 'description' in op:
                            ex['description'] = op['description']
                    else:
                        new_op = op.copy()
                        if not new_op.get('tags'):
                            # ваша логіка fallback тегів
                            fallback = default_tag
                            if svc == 'user':
                                if p.startswith('/users'):     fallback = 'users'
                                elif p.startswith(('/login','/logout','/register','/token','/password')): fallback = 'auth'
                                elif p.startswith('/profile'): fallback = 'profile'
                            elif svc == 'product':
                                if p.startswith('/products'):  fallback = 'products'
                                elif p.startswith('/moderation'): fallback = 'moderation'
                                elif p.startswith('/reviews'): fallback = 'reviews'
                            elif svc == 'order':
                                if p.startswith('/orders'):    fallback = 'orders'
                                elif p.startswith(('/carts','/cart')): fallback = 'carts'
                            new_op['tags'] = [fallback]
                        gateway_schema['paths'][p][m] = new_op

        # components
        for schema in external:
            comp = schema.get('components', {})
            gw_comp = gateway_schema.setdefault('components', {})
            for k in ('schemas', 'parameters', 'responses', 'requestBodies', 'headers', 'securitySchemes'):
                if k in comp:
                    gw_comp.setdefault(k, {}).update(comp[k])

        cache.set('merged_schema', gateway_schema, 3600)
        return Response(gateway_schema)


# ────────────────────────────────────────────────
# Proxy — тільки /api/
# ────────────────────────────────────────────────
@extend_schema(exclude=True)
class ProxyView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @extend_schema(exclude=True)
    def proxy(self, request, path: str):
        # path вже без /api/

        target = None

        # Спеціальні ендпоінти (health / schema)
        special = {
            'users/health':     f"{settings.USER_SERVICE_URL}/health",
            'users/schema':     f"{settings.USER_SERVICE_URL}/schema",
            'products/health':  f"{settings.PRODUCT_SERVICE_URL}/health",
            'products/schema':  f"{settings.PRODUCT_SERVICE_URL}/schema",
            'orders/health':    f"{settings.ORDER_SERVICE_URL}/health",
            'orders/schema':    f"{settings.ORDER_SERVICE_URL}/schema",
        }
        if path in special:
            target = special[path]

        # Основні маршрути
        elif path.startswith('users/'):
            target = f"{settings.USER_SERVICE_URL}/{path[6:]}"
        elif path == 'users':
            target = f"{settings.USER_SERVICE_URL}/users"

        elif path.startswith('products/'):
            target = f"{settings.PRODUCT_SERVICE_URL}/{path[9:] or 'products'}"
        elif path == 'products':
            target = f"{settings.PRODUCT_SERVICE_URL}/products"

        elif path.startswith('moderation/'):
            target = f"{settings.PRODUCT_SERVICE_URL}/{path}"

        elif path.startswith('orders/'):
            target = f"{settings.ORDER_SERVICE_URL}/{path}"
        elif path == 'orders':
            target = f"{settings.ORDER_SERVICE_URL}/orders"

        elif path.startswith(('carts/', 'cart/')):
            pfx = 6 if path.startswith('carts/') else 5
            target = f"{settings.ORDER_SERVICE_URL}/cart/{path[pfx:]}"
        elif path in ('carts', 'cart'):
            target = f"{settings.ORDER_SERVICE_URL}/cart"

        if not target:
            logger.warning(f"No mapping for /api/{path}")
            return Response(
                {"detail": "Not Found", "hint": "Check endpoint prefix /api/"},
                status=404
            )

        # ─── Forward request ───────────────────────────────────────
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in {'host', 'content-length'}
        }

        # Безпечні encoding'и
        if 'Accept-Encoding' in headers:
            enc = [e.strip() for e in headers['Accept-Encoding'].split(',')]
            safe = [e for e in enc if e.lower() not in {'br', 'brotli'}]
            headers['Accept-Encoding'] = ', '.join(safe or ['gzip', 'deflate'])

        try:
            upstream = requests.request(
                method=request.method,
                url=target,
                headers=headers,
                data=request.body,
                params=request.GET,
                allow_redirects=False,
                timeout=25,
            )

            ct = upstream.headers.get('Content-Type', '')

            if 'application/json' in ct:
                try:
                    data = upstream.json()
                except ValueError:
                    logger.error(f"Upstream invalid JSON → {target}")
                    return Response({"detail": "Bad gateway"}, status=502)
                response = Response(data, status=upstream.status_code)
            else:
                response = Response(upstream.content, status=upstream.status_code)

            if ct:
                response['Content-Type'] = ct

            if 'Set-Cookie' in upstream.headers:
                response['Set-Cookie'] = upstream.headers['Set-Cookie']

            for h in ('Location', 'Cache-Control', 'Vary', 'Allow'):
                if h in upstream.headers:
                    response[h] = upstream.headers[h]

            return response

        except requests.Timeout:
            return Response({"detail": "Gateway Timeout"}, status=504)
        except requests.ConnectionError:
            return Response({"detail": "Service Unavailable"}, status=503)
        except Exception as exc:
            logger.exception(f"Proxy error → {target}")
            return Response({"detail": "Proxy Error"}, status=502)

    # HTTP methods
    def get(self, request, path=''):    return self.proxy(request, path)
    def post(self, request, path=''):   return self.proxy(request, path)
    def put(self, request, path=''):    return self.proxy(request, path)
    def patch(self, request, path=''):  return self.proxy(request, path)
    def delete(self, request, path=''): return self.proxy(request, path)


# ────────────────────────────────────────────────
# URLconf
# ────────────────────────────────────────────────
urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('',                RootView.as_view(),           name='root'),
    path('health',          HealthCheckView.as_view(),    name='health'),
    path('schema',          MergedSchemaView.as_view(),   name='schema'),
    path('swagger-ui',      SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Тільки API-префікс
    re_path(r'^api/(?P<path>.*)/?$', ProxyView.as_view(), name='api-proxy'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)