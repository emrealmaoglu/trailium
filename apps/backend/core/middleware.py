import logging
import time

logger = logging.getLogger(__name__)


class PerformanceMiddleware:
    """Middleware to monitor request performance"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        # Log slow requests
        if duration > 0.5:  # 500ms threshold
            logger.warning(
                f"Slow request: {request.method} {request.path} took {duration:.3f}s"
            )

        # Add performance header
        response["X-Response-Time"] = f"{duration:.3f}s"

        return response


class RequestLoggingMiddleware:
    """Middleware to log all requests for debugging and monitoring"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        logger.info(
            f'Request: {request.method} {request.path} from {request.META.get("REMOTE_ADDR", "unknown")}'
        )

        response = self.get_response(request)

        # Log response details
        logger.info(
            f"Response: {request.method} {request.path} -> {response.status_code}"
        )

        return response


class ErrorHandlingMiddleware:
    """Middleware to handle and format errors consistently"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Handle exceptions and return consistent error responses"""
        from django.core.exceptions import PermissionDenied, ValidationError
        from django.http import Http404, JsonResponse

        if isinstance(exception, ValidationError):
            return JsonResponse(
                {
                    "error": "Validation Error",
                    "message": "The provided data is invalid",
                    "details": (
                        exception.message_dict
                        if hasattr(exception, "message_dict")
                        else str(exception)
                    ),
                    "type": "validation_error",
                },
                status=400,
            )

        elif isinstance(exception, PermissionDenied):
            return JsonResponse(
                {
                    "error": "Permission Denied",
                    "message": "You do not have permission to perform this action",
                    "type": "permission_denied",
                },
                status=403,
            )

        elif isinstance(exception, Http404):
            return JsonResponse(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found",
                    "type": "not_found",
                },
                status=404,
            )

        # Log unexpected errors
        logger.error(
            f"Unexpected error in {request.method} {request.path}: {str(exception)}",
            exc_info=True,
        )

        # Return generic error in production
        return JsonResponse(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "type": "internal_error",
            },
            status=500,
        )
