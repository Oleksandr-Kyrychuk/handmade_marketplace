import logging

logger = logging.getLogger(__name__)

class DebugHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.error(f"Request Host: {request.get_host()}, Headers: {dict(request.headers)}")
        return self.get_response(request)