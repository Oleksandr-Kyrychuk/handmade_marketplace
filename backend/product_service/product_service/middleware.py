import requests
from django.conf import settings
import logging
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                response = requests.post(
                    f"{settings.USER_SERVICE_URL}/api/token/verify/",
                    json={'token': token},
                    timeout=5
                )
                if response.status_code == 200:
                    user_data = response.json()
                    request.user = type('User', (), {
                        'id': user_data.get('user_id'),
                        'roles': user_data.get('roles', []),
                        'is_authenticated': True
                    })
                else:
                    logger.warning(f"Invalid token: {response.status_code}")
                    request.user = AnonymousUser()
            except requests.RequestException as e:
                logger.error(f"Error verifying token: {str(e)}")
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        return self.get_response(request)
