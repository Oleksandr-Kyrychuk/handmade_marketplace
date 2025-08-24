from django.urls import path, re_path
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static
import redis
from django.core.cache import cache


@api_view(['GET'])
@throttle_classes([])  # 🚀 вимикає throttling тільки тут
def health_check(request):
    """Return the health status of the API Gateway and dependent services."""
    services = {
        # 'user_service': 'http://user_service:8000/health',
        # 'product_service': 'http://product_service:8000/health',
        # 'order_service': 'http://order_service:8000/health',
        # 'auction_service': 'http://auction_service:8000/health',
    }
    results = {}
    all_healthy = True

    # Check each service
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            results[service_name] = {
                'status': 'ok' if response.status_code == 200 and response.json().get('status') == 'ok' else 'error',
                'code': response.status_code
            }
            if results[service_name]['status'] != 'ok':
                all_healthy = False
        except (requests.RequestException, ValueError):
            results[service_name] = {'status': 'error', 'code': None}
            all_healthy = False

    # Check Redis
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
def proxy_view(request, path):
    if path.startswith('static/') or path == 'favicon.ico':
        return Response({'error': 'Not handled by proxy'}, status=404)

    service_map = {
        'auth': 'http://user_service:8000',
        'products': 'http://product_service:8000',
        'orders': 'http://order_service:8000',
        'auctions': 'http://auction_service:8000',
    }
    service = path.split('/')[0]
    if service in service_map:
        target_url = f"{service_map[service]}/{path}"
    else:
        return Response({'error': 'Unknown service'}, status=400)

    headers = {'Authorization': request.META.get('HTTP_AUTHORIZATION', '')}
    response = requests.request(
        method=request.method,
        url=target_url,
        headers=headers,
        json=request.data if request.data else None,
        params=request.query_params,
    )
    return Response(response.json(), status=response.status_code)

@api_view(['GET'])
@throttle_classes([])
def combined_schema(request):
    """Combine OpenAPI schemas from all microservices into one."""
    # Список мікросервісів і їх schema URLs (адаптуйте під ваші сервіси)
    microservices = {
        'user_service': 'http://user_service:8000/openapi.json',
        'product_service': 'http://product_service:8000/openapi.json',
        'order_service': 'http://order_service:8000/openapi.json',
        'auction_service': 'http://auction_service:8000/openapi.json',
        # Додайте інші сервіси за потребою
    }

    combined = {
        'openapi': '3.0.3',
        'info': {
            'title': 'Handmade Marketplace Combined API',
            'version': '1.0.0',
            'description': 'Combined API documentation from all microservices',
        },
        'paths': {},
        'components': {'schemas': {}, 'responses': {}, 'parameters': {}, 'securitySchemes': {}},
        'servers': [{'url': '/'}],  # Базовий сервер
    }

    for service_name, schema_url in microservices.items():
        try:
            response = requests.get(schema_url, timeout=5)
            if response.status_code == 200:
                schema = response.json()
                # Об'єднуємо paths з префіксом сервісу (наприклад, /users/)
                for path, methods in schema.get('paths', {}).items():
                    combined['paths'][f'/{service_name}{path}'] = methods
                # Об'єднуємо components, додаючи префікс до імен (щоб уникнути конфліктів)
                for component_type, items in schema.get('components', {}).items():
                    for name, definition in items.items():
                        combined['components'][component_type][f'{service_name}_{name}'] = definition
        except requests.RequestException:
            # Якщо сервіс недоступний, пропускаємо (логування для продакшену)
            pass

    return Response(combined)

urlpatterns = [
    path('health', health_check, name='health'),
    path('schema/', combined_schema, name='combined-schema'),  # Об'єднана схема
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='combined-schema'), name='swagger-ui'),  # Swagger UI з об'єднаною схемою
    re_path(r'^(?P<path>.*)$', proxy_view),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
