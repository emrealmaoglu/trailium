import logging


class PerformanceFilter(logging.Filter):
    """
    Filter to only log performance-related messages
    """

    def filter(self, record):
        # Only log performance messages
        return (
            "performance" in record.getMessage().lower()
            or "slow" in record.getMessage().lower()
        )


class SecurityFilter(logging.Filter):
    """
    Filter to only log security-related messages
    """

    def filter(self, record):
        # Only log security messages
        security_keywords = [
            "suspicious",
            "attack",
            "injection",
            "xss",
            "csrf",
            "sqli",
            "bot",
            "crawler",
            "admin",
            "unauthorized",
            "forbidden",
        ]
        message = record.getMessage().lower()
        return any(keyword in message for keyword in security_keywords)


class ErrorFilter(logging.Filter):
    """
    Filter to only log error messages
    """

    def filter(self, record):
        # Only log error and critical messages
        return record.levelno >= logging.ERROR
