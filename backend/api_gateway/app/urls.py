"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# /mnt/d/handmade_marketplace/backend/api_gateway/app/urls.py
from django.urls import path, re_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from django.conf import settings
from django.conf.urls.static import static

@api_view(['GET'])
def health_check(request):
    """Return the health status of the API Gateway."""
    return Response({"status": "ok"}, status=200)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def proxy_view(request, path):
    # Ігнорувати статичні файли та favicon
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

urlpatterns = [
    path('health', health_check, name='health'),
    re_path(r'^(?P<path>.*)$', proxy_view),
]

# Додаємо обслуговування статичних файлів для dev
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)