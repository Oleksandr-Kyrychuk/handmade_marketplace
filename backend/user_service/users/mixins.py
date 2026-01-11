# users/mixins.py
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

class UnifiedResponseMixin:
    """
    Міксин для уніфікації відповідей API.
    Обгортає відповіді в формат:
    {
        "success": bool,
        "data": any | null,
        "errors": array<object> | null,
        "message": string | null
    }
    Де errors: [{"field": str|null, "message": str, "code": str|None}]
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
        except APIException as exc:
            response = self.handle_exception(exc)
        if isinstance(response, Response):
            response = self.unify_response(response)
        return response

    def unify_response(self, response):
        if "success" in response.data:
            return response

        success = response.status_code < 400
        original_data = dict(response.data) if response.data else {}  # Копіюємо, щоб не мутувати оригінал

        if success:
            message = original_data.pop("detail", None) or original_data.pop("message", None)
            data = original_data if original_data else None  # null, якщо немає даних
        else:
            message = None
            data = None
            errors = self.format_errors(original_data)

        unified_data = {
            "success": success,
            "data": data,
            "errors": errors if not success else None,
            "message": message
        }

        response.data = unified_data
        return response

    def format_errors(self, error_data):
        errors = []
        if isinstance(error_data, dict):
            for field, value in error_data.items():
                if isinstance(value, list):
                    for item in value:
                        msg = str(item)
                        code = getattr(item, 'code', 'validation_error') if hasattr(item, 'code') else 'validation_error'
                        errors.append({
                            "field": field if field != "non_field_errors" else None,
                            "message": msg,
                            "code": code
                        })
                else:
                    msg = str(value)
                    code = getattr(value, 'code', 'error') if hasattr(value, 'code') else 'error'
                    errors.append({
                        "field": field if field != "non_field_errors" else None,
                        "message": msg,
                        "code": code
                    })
        elif isinstance(error_data, (list, tuple)):
            for item in error_data:
                msg = str(item)
                code = getattr(item, 'code', None) if hasattr(item, 'code') else None
                errors.append({"field": None, "message": msg, "code": code})
        else:
            msg = str(error_data)
            code = getattr(error_data, 'code', None) if hasattr(error_data, 'code') else None
            errors.append({"field": None, "message": msg, "code": code})

        return errors or [{"field": None, "message": "Unknown error", "code": "unknown"}]

    def handle_exception(self, exc):
        response = exception_handler(exc, self.get_exception_handler_context())
        if response is None:
            response = Response({"detail": str(exc)}, status=500)
        return response

    def get_exception_handler_context(self):
        return {'view': self, 'args': (), 'kwargs': {}, 'request': self.request}
