from pathlib import Path

# Base directory for logs
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s", "user": "%(user)s", "ip": "%(ip)s"}',
            "style": "%",
        },
        "performance": {
            "format": "{asctime} {levelname} {message} - {duration}ms - {endpoint}",
            "style": "{",
        },
        "security": {
            "format": "{asctime} {levelname} SECURITY: {message} - User: {user} - IP: {ip} - Endpoint: {endpoint}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "security_filter": {
            "()": "core.logging_config.SecurityFilter",
        },
        "performance_filter": {
            "()": "core.logging_config.PerformanceFilter",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "django.log",
            "formatter": "verbose",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "error.log",
            "formatter": "verbose",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "security_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "security.log",
            "formatter": "security",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
        },
        "performance_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "performance.log",
            "formatter": "performance",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "access_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "access.log",
            "formatter": "json",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error_file", "access_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["security_file", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["performance_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "performance": {
            "handlers": ["performance_file"],
            "level": "INFO",
            "propagate": False,
        },
        "security": {
            "handlers": ["security_file", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        "access": {
            "handlers": ["access_file"],
            "level": "INFO",
            "propagate": False,
        },
        "users": {
            "handlers": ["console", "file", "security_file"],
            "level": "INFO",
            "propagate": False,
        },
        "social": {
            "handlers": ["console", "file", "access_file"],
            "level": "INFO",
            "propagate": False,
        },
        "todos": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "core": {
            "handlers": ["console", "file", "security_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "WARNING",
    },
}


# Custom logging filters
class SecurityFilter:
    """Filter for security-related log messages"""

    def filter(self, record):
        # Check if this is a security-related message
        security_keywords = [
            "security",
            "attack",
            "xss",
            "sql injection",
            "csrf",
            "authentication",
            "authorization",
            "permission",
            "throttle",
            "suspicious",
            "malicious",
            "breach",
            "vulnerability",
        ]

        message = getattr(record, "message", "").lower()
        if any(keyword in message for keyword in security_keywords):
            return True

        # Check if this is from security logger
        if record.name == "security":
            return True

        return False


class PerformanceFilter:
    """Filter for performance-related log messages"""

    def filter(self, record):
        # Check if this is a performance-related message
        performance_keywords = [
            "slow",
            "performance",
            "duration",
            "timeout",
            "latency",
            "query",
            "cache",
            "memory",
            "cpu",
            "response time",
        ]

        message = getattr(record, "message", "").lower()
        if any(keyword in message for keyword in performance_keywords):
            return True

        # Check if this is from performance logger
        if record.name == "performance":
            return True

        return False


# Logging utilities
def log_security_event(level, message, user=None, ip=None, endpoint=None, **kwargs):
    """Log security-related events with context"""
    import logging

    logger = logging.getLogger("security")

    # Add context to log record
    extra = {
        "user": user or "anonymous",
        "ip": ip or "unknown",
        "endpoint": endpoint or "unknown",
        **kwargs,
    }

    if level == "warning":
        logger.warning(message, extra=extra)
    elif level == "error":
        logger.error(message, extra=extra)
    elif level == "critical":
        logger.critical(message, extra=extra)
    else:
        logger.info(message, extra=extra)


def log_performance_event(message, duration, endpoint=None, **kwargs):
    """Log performance-related events"""
    import logging

    logger = logging.getLogger("performance")

    extra = {"duration": duration, "endpoint": endpoint or "unknown", **kwargs}

    logger.info(message, extra=extra)


def log_access_event(user, ip, endpoint, method, status_code, duration=None, **kwargs):
    """Log access events for monitoring"""
    import logging

    logger = logging.getLogger("access")

    message = f"{method} {endpoint} - {status_code}"
    if duration:
        message += f" - {duration}ms"

    extra = {
        "user": user or "anonymous",
        "ip": ip or "unknown",
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "duration": duration,
        **kwargs,
    }

    logger.info(message, extra=extra)
