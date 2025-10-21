import logging
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

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
# Health check for gateway
# ============================
class HealthCheckView(APIView):
    throttle_classes = []
    serializer_class = HealthCheckSerializer

    @extend_schema(
        request=None,
        responses={200: HealthCheckSerializer, 503: HealthCheckSerializer},
        summary="Health check for API Gateway",
        description="Checks Redis, microservices and cached schemas availability."
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
            logger.error(f"Redis health check failed: {str(e)}")

        # User service
        for attempt in range(max_retries):
            try:
                resp = requests.get(f'{settings.USER_SERVICE_URL}/health', timeout=20)
                results['user_service'] = {'status': 'ok' if resp.status_code == 200 else 'error'}
                break
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    results['user_service'] = {'status': 'error', 'detail': str(e)}
                    all_healthy = False
                    logger.error(f"user_service health check failed: {str(e)}")
                time.sleep(retry_delay)

        # Product service
        for attempt in range(max_retries):
            try:
                resp = requests.get(f'{settings.PRODUCT_SERVICE_URL}/health', timeout=20)
                results['product_service'] = {'status': 'ok' if resp.status_code == 200 else 'error'}
                break
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    results['product_service'] = {'status': 'error', 'detail': str(e)}
                    all_healthy = False
                    logger.error(f"product_service health check failed: {str(e)}")
                time.sleep(retry_delay)

        # Cached schemas
        user_schema = cache.get('user_service_schema')
        product_schema = cache.get('product_service_schema')
        results['user_service_schema'] = {'status': 'ok' if user_schema else 'error'}
        results['product_service_schema'] = {'status': 'ok' if product_schema else 'error'}

        overall_status = 'ok' if all_healthy else 'error'
        return Response({'status': overall_status, 'services': results}, status=200 if all_healthy else 503)


# ============================
# Merged OpenAPI schema
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

        # отримуємо схеми з кешу
        user_schema = cache.get('user_service_schema', {})
        product_schema = cache.get('product_service_schema', {})

        # merge paths
        gateway_schema['paths'].update(user_schema.get('paths', {}))
        gateway_schema['paths'].update(product_schema.get('paths', {}))

        # merge components
        for schema in [user_schema, product_schema]:
            for comp_type, comp_data in schema.get('components', {}).items():
                gateway_schema['components'].setdefault(comp_type, {}).update(comp_data)

        cache.set('merged_schema', gateway_schema, timeout=3600)
        return Response(gateway_schema)


# ============================
# Proxy view
# ============================
class ProxyView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @extend_schema(exclude=True)
    def handle_request(self, request, path):
        path = path.strip('/')

        if path.startswith('users'):
            target_url = f'{settings.USER_SERVICE_URL}/{path}'
            service_name = 'user_service'
        elif path.startswith('products') or path.startswith('moderation'):
            target_url = f'{settings.PRODUCT_SERVICE_URL}/{path}'
            service_name = 'product_service'
        else:
            logger.warning(f"No microservice for path: {path}")
            return Response({'error': f'No microservice available for path: {path}'}, status=503)

        headers = {k: v for k, v in request.headers.items() if k.lower() not in ('host', 'content-length', 'connection', 'transfer-encoding')}

        try:
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.body,
                params=request.GET,
                allow_redirects=False,
                timeout=20
            )

            content_type = resp.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                try:
                    return Response(resp.json(), status=resp.status_code)
                except ValueError:
                    logger.error(f"Invalid JSON from {target_url}")
                    return Response({'error': 'Invalid JSON response from service'}, status=resp.status_code)
            else:
                return Response({'error': resp.text or 'Unknown error from service'}, status=resp.status_code)

        except requests.Timeout:
            logger.error(f"Timeout when proxying to {service_name} at {target_url}")
            return Response({'error': f'{service_name} timed out'}, status=503)
        except requests.ConnectionError:
            logger.error(f"Connection error when proxying to {service_name} at {target_url}")
            return Response({'error': f'Failed to connect to {service_name}'}, status=503)
        except requests.RequestException as e:
            logger.error(f"Error proxying to {service_name} at {target_url}: {str(e)}")
            return Response({'error': f'Error proxying to {service_name}: {str(e)}'}, status=503)

    def get(self, request, path):
        return self.handle_request(request, path)

    def post(self, request, path):
        return self.handle_request(request, path)

    def put(self, request, path):
        return self.handle_request(request, path)

    def delete(self, request, path):
        return self.handle_request(request, path)


urlpatterns = [
    path('health', HealthCheckView.as_view(), name='health'),
    path('schema', MergedSchemaView.as_view(), name='schema'),
    path('swagger-ui', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    re_path(r'^(?P<path>.*)$', ProxyView.as_view(), name='proxy'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)