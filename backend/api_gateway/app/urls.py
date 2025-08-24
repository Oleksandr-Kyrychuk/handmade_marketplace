from django.urls import path, re_path
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_spectacular.utils import extend_schema
from django.conf import settings
from django.conf.urls.static import static
import redis
from django.core.cache import cache
from .serializers import HealthCheckSerializer, ProxyErrorSerializer

@api_view(['GET'])
@throttle_classes([])
@extend_schema(
    responses={
        200: HealthCheckSerializer,
        503: HealthCheckSerializer,
    },
    summary="Health check for API Gateway",
    description="Checks the availability of Redis and returns the overall status."
)
def health_check(request):
    """Return the health status of the API Gateway.

    Checks the availability of Redis and returns the overall status.

    Responses:
        200: All services healthy
        503: Some services unhealthy
    """
    results = {}
    all_healthy = True

    # Мікросервіси закоментовані, оскільки вони ще не розгорнуті
    # services = {
    #     'user_service': 'http://user_service:8000/health',
    #     'product_service': 'http://product_service:8000/health',
    #     'order_service': 'http://order_service:8000/health',
    #     'auction_service': 'http://auction_service:8000/health',
    # }
    # for service_name, url in services.items():
    #     try:
    #         response = requests.get(url, timeout=2)
    #         results[service_name] = {
    #             'status': 'ok' if response.status_code == 200 and response.json().get('status') == 'ok' else 'error',
    #             'code': response.status_code
    #         }
    #         if results[service_name]['status'] != 'ok':
    #             all_healthy = False
    #     except (requests.RequestException, ValueError):
    #         results[service_name] = {'status': 'error', 'code': None}
    #         all_healthy = False

    # Перевірка Redis
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


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@extend_schema(
    responses={
        404: ProxyErrorSerializer,
        503: ProxyErrorSerializer,
    },
    summary="Proxy view for microservices",
    description="Temporary placeholder for proxying requests to microservices (not yet available)."
)
def proxy_view(request, path):
    """Temporary placeholder for proxy view since microservices are not deployed."""
    if path.startswith('static/') or path == 'favicon.ico':
        return Response({'error': 'Not handled by proxy'}, status=404)

    # Закоментуємо логіку проксі, оскільки мікросервіси недоступні
    # service_map = {
    #     'auth': 'http://user_service:8000',
    #     'products': 'http://product_service:8000',
    #     'orders': 'http://order_service:8000',
    #     'auctions': 'http://auction_service:8000',
    # }
    # service = path.split('/')[0]
    # if service in service_map:
    #     target_url = f"{service_map[service]}/{path}"
    # else:
    #     return Response({'error': 'Unknown service'}, status=400)
    #
    # headers = {'Authorization': request.META.get('HTTP_AUTHORIZATION', '')}
    # response = requests.request(
    #     method=request.method,
    #     url=target_url,
    #     headers=headers,
    #     json=request.data if request.data else None,
    #     params=request.query_params,
    # )
    # return Response(response.json(), status=response.status_code)

    return Response({'error': 'No microservices available'}, status=503)


urlpatterns = [
    path('health', health_check, name='health'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    re_path(r'^(?P<path>.*)$', proxy_view),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)