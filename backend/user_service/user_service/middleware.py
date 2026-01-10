import logging
import time
import uuid

logger = logging.getLogger(__name__)

class DebugHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.error(f"Request Host: {request.get_host()}, Headers: {dict(request.headers)}")
        return self.get_response(request)

# Новий клас для логування API-запитів
api_logger = logging.getLogger('api.request')

class APILoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()

        # Додаємо унікальний request_id
        request_id = str(uuid.uuid4())[:8]
        request.META['HTTP_X_REQUEST_ID'] = request_id

        response = self.get_response(request)

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        user_id = request.user.id if request.user.is_authenticated else None
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown'))

        extra = {
            'method': request.method,
            'path': request.get_full_path(),
            'status': response.status_code,
            'duration_ms': duration_ms,
            'user_id': user_id,
            'client_ip': client_ip,
            'request_id': request_id,
        }

        # Визначаємо рівень логування залежно від статусу
        if response.status_code >= 500:
            level = logging.ERROR
        elif response.status_code >= 400:
            level = logging.WARNING
        else:
            level = logging.INFO

        api_logger.log(level, "API request", extra=extra)

        return response
    