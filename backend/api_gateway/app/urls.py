import os
from django.urls import path, re_path
from django.views.generic import RedirectView
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.conf import settings
from django.conf.urls.static import static
import redis
from django.core.cache import cache
from .serializers import HealthCheckSerializer, ProxyErrorSerializer, EmptySerializer
import requests
import logging
from rest_framework import permissions

logger = logging.getLogger(__name__)

# Отримуємо USER_SERVICE_URL із змінної оточення
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user_service:8001')

class HealthCheckView(APIView):
    throttle_classes = []
    serializer_class = HealthCheckSerializer

    @extend_schema(
        request=None,
        responses={
            200: HealthCheckSerializer,
            503: HealthCheckSerializer,
        },
        summary="Health check for API Gateway",
        description="Checks the availability of Redis and microservices."
    )
    def get(self, request):
        results = {}
        all_healthy = True

        try:
            cache.get('health_check_test')
            results['redis'] = {'status': 'ok'}
        except redis.RedisError as e:
            results['redis'] = {'status': 'error', 'detail': str(e)}
            all_healthy = False
            logger.error(f"Redis health check failed: {str(e)}")

        try:
            response = requests.get(
                f'{USER_SERVICE_URL}/health/',
                timeout=20
            )
            results['user_service'] = {'status': 'ok' if response.status_code == 200 else 'error'}
        except requests.RequestException as e:
            results['user_service'] = {'status': 'error', 'detail': str(e)}
            all_healthy = False
            logger.error(f"user_service health check failed: {str(e)}")

        overall_status = 'ok' if all_healthy else 'error'
        return Response({
            'status': overall_status,
            'services': results
        }, status=200 if all_healthy else 503)

class UserServiceSchemaView(GenericAPIView):
    serializer_class = EmptySerializer
    @extend_schema(
        summary="OpenAPI schema for user_service",
        description="Returns merged OpenAPI schema with user_service"
    )
    def get(self, request):
        # Отримати кешовану схему
        merged_schema = cache.get('merged_schema')
        if merged_schema:
            return Response(merged_schema)

        # Отримати власну схему API Gateway
        from drf_spectacular.generators import SchemaGenerator
        generator = SchemaGenerator()
        gateway_schema = generator.get_schema(request=request)

        try:
            # Отримати схему user_service
            response = requests.get(
                f'{USER_SERVICE_URL}/schema/',
                timeout=20
            )
            if response.status_code == 200:
                user_schema = response.json()

                # Merge paths
                gateway_schema['paths'].update(user_schema.get('paths', {}))

                # Merge components
                for comp_type, comp_data in user_schema.get('components', {}).items():
                    gateway_schema['components'].setdefault(comp_type, {}).update(comp_data)

                # Кешування на годину
                cache.set('merged_schema', gateway_schema, timeout=3600)
                return Response(gateway_schema)
            else:
                return Response({'error': 'User service schema unavailable'}, status=503)

        except requests.RequestException as e:
            return Response({'error': f'Error fetching user service schema: {str(e)}'}, status=503)

class ProxyView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProxyErrorSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def handle_request(self, request, path):
        # Виключаємо запити до документації
        if path.startswith('users/swagger/') or path.startswith('users/schema/'):
            logger.warning(f"Documentation paths should be accessed via /users/swagger-ui/ or /users/schema/")
            return Response({'error': 'Use /users/swagger-ui/ for documentation'}, status=404)

        if path.startswith('users/'):
            service_name = 'user_service'
            sub_path = path[len("users/"):].lstrip('/')
            target_url = f'{USER_SERVICE_URL}/{sub_path}'
        else:
            logger.warning(f"No microservice available for path: {path}")
            return Response({'error': f'No microservices available for path: {path}'}, status=503)

        logger.info(f"Proxying {request.method} request to {target_url}")

        # Копіюємо заголовки, виключаючи непотрібні
        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in ('host', 'content-length', 'connection', 'transfer-encoding')
        }

        try:
            response = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,  # Передаємо заголовки
                data=request.body,  # Тіло запиту (для POST/PUT)
                params=request.GET,  # Параметри запиту
                allow_redirects=False,
                timeout=20
            )
            logger.info(f"Received {response.status_code} from {target_url}")

            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                return HttpResponse(
                    response.content,
                    status=response.status_code,
                    content_type=content_type
                )
            else:
                return Response(
                    response.content,
                    status=response.status_code,
                    content_type=content_type
                )

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
    path('health', RedirectView.as_view(url='/health/')),
    path('health/', HealthCheckView.as_view(), name='health'),
    path('schema/', UserServiceSchemaView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('swagger/', lambda request: HttpResponseRedirect('/swagger-ui/')),
    path('users/schema/', UserServiceSchemaView.as_view(), name='user-schema'),
    path('users/swagger-ui/', SpectacularSwaggerView.as_view(url_name='user-schema'), name='user-swagger-ui'),
    re_path(r'^(?P<path>.*)$', ProxyView.as_view(), name='proxy'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)