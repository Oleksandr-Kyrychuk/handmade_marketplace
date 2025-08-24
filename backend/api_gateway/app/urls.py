from django.urls import path, re_path
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
        description="Checks the availability of Redis and returns the overall status."
    )
    def get(self, request):
        results = {}
        all_healthy = True

        try:
            cache.get('health_check_test')
            results['redis'] = {'status': 'ok'}
        except redis.RedisError:
            results['redis'] = {'status': 'error'}
            all_healthy = False

        overall_status = 'ok' if all_healthy else 'error'
        return Response({
            'status': overall_status,
            'services': results
        }, status=200 if all_healthy else 503)


class ProxyView(APIView):
    serializer_class = ProxyErrorSerializer

    @extend_schema(
        request=None,
        responses={
            404: ProxyErrorSerializer,
            503: ProxyErrorSerializer,
        },
        parameters=[
            OpenApiParameter(
                name='path',
                type=str,
                location=OpenApiParameter.PATH,
                description='Path to the microservice endpoint',
                required=True
            )
        ],
        summary="Proxy view for microservices",
        description="Temporary placeholder for proxying requests to microservices (not yet available).",
        methods=['GET', 'POST', 'PUT', 'DELETE']
    )
    def get(self, request, path):
        return self.handle_request(request, path)

    def post(self, request, path):
        return self.handle_request(request, path)

    def put(self, request, path):
        return self.handle_request(request, path)

    def delete(self, request, path):
        return self.handle_request(request, path)

    def handle_request(self, request, path):
        if path.startswith('static/') or path == 'favicon.ico':
            return Response({'error': 'Not handled by proxy'}, status=404)
        return Response({'error': 'No microservices available'}, status=503)


urlpatterns = [
    path('health', HealthCheckView.as_view(), name='health'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    re_path(r'^(?P<path>.*)$', ProxyView.as_view(), name='proxy'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)