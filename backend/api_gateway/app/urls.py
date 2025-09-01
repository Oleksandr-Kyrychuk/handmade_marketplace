from django.urls import path, re_path
from django.views.generic import RedirectView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.conf import settings
from django.conf.urls.static import static
import redis
from django.core.cache import cache
from .serializers import HealthCheckSerializer, ProxyErrorSerializer
import requests
import logging

logger = logging.getLogger(__name__)

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
                'http://user_service:8001/health/',
                headers={"Host": "user-service.localdomain"},
                timeout=2
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

class ProxyView(APIView):
    serializer_class = ProxyErrorSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def handle_request(self, request, path):
        if path.startswith('users/'):
            service_name = 'user_service'
            target_url = f'http://user_service:8001/{path[len("users/"):]}'
        else:
            logger.warning(f"No microservice available for path: {path}")
            return Response({'error': f'No microservices available for path: {path}'}, status=503)

        headers = {"Host": "user-service.localdomain"}  # Залишаємо .localdomain для консистентності
        logger.info(f"Proxying {request.method} request to {target_url} with headers: {headers}")

        try:
            response = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.body,
                params=request.GET,
                allow_redirects=False,
                timeout=2
            )
            logger.info(f"Received {response.status_code} from {target_url}")
            return Response(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type')
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
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('swagger/', lambda request: HttpResponseRedirect('/swagger-ui/')),  # Редирект із /swagger/ на /swagger-ui/
    re_path(r'^(?P<path>.*)$', ProxyView.as_view(), name='proxy'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)