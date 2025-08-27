import logging
import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Comprehensive input validation for security"""

    # Common attack patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]

    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
        r"(\b(or|and)\b\s+\d+\s*[=<>])",
        r"(\b(exec|execute|xp_|sp_)\b)",
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
    ]

    @classmethod
    def validate_text_input(cls, value, field_name, max_length=1000):
        """Validate text input for security and content"""
        if not value:
            return value

        # Convert to string and strip whitespace
        value = str(value).strip()

        # Check length
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} is too long (max {max_length} characters)"
            )

        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(
                    f"Potential XSS attack detected in {field_name}: {value[:100]}"
                )
                raise ValidationError(f"{field_name} contains invalid content")

        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(
                    f"Potential SQL injection detected in {field_name}: {value[:100]}"
                )
                raise ValidationError(f"{field_name} contains invalid content")

        # Strip HTML tags
        cleaned_value = strip_tags(value)
        if cleaned_value != value:
            logger.info(f"HTML tags stripped from {field_name}")
            value = cleaned_value

        return value

    @classmethod
    def validate_username(cls, username):
        """Validate username for security and format"""
        if not username:
            raise ValidationError("Username is required")

        username = str(username).strip().lower()

        # Length validation
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        if len(username) > 30:
            raise ValidationError("Username must be no more than 30 characters long")

        # Format validation (alphanumeric + underscore only)
        if not re.match(r"^[a-z0-9_]+$", username):
            raise ValidationError(
                "Username can only contain lowercase letters, numbers, and underscores"
            )

        # Reserved usernames
        reserved = ["admin", "root", "system", "test", "demo", "guest", "anonymous"]
        if username in reserved:
            raise ValidationError("This username is not allowed")

        # Check for suspicious patterns
        if re.search(r"(admin|root|system)", username, re.IGNORECASE):
            logger.warning(f"Suspicious username pattern detected: {username}")

        return username

    @classmethod
    def validate_password(cls, password):
        """Validate password strength"""
        if not password:
            raise ValidationError("Password is required")

        password = str(password)

        # Length validation
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if len(password) > 128:
            raise ValidationError("Password must be no more than 128 characters long")

        # Complexity requirements
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "Password must contain at least one special character"
            )

        # Common password check
        common_passwords = [
            "password",
            "123456",
            "admin",
            "qwerty",
            "letmein",
            "welcome",
            "monkey",
            "dragon",
            "master",
            "football",
        ]
        if password.lower() in common_passwords:
            raise ValidationError("This password is too common")

        # Sequential patterns
        if re.search(r"(123|abc|qwe)", password.lower()):
            raise ValidationError("Password contains sequential patterns")

        return password

    @classmethod
    def validate_email(cls, email):
        """Validate email format and security"""
        if not email:
            raise ValidationError("Email is required")

        email = str(email).strip().lower()

        # Basic format validation
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Enter a valid email address")

        # Length validation
        if len(email) > 254:
            raise ValidationError("Email address is too long")

        # Check for suspicious patterns
        if re.search(r"(admin|root|test|demo)@", email):
            logger.warning(f"Suspicious email pattern detected: {email}")

        return email

    @classmethod
    def validate_file_upload(cls, file, allowed_types=None, max_size=10485760):
        """Validate file uploads for security"""
        if not file:
            raise ValidationError("File is required")

        # Check file size (default 10MB)
        if file.size > max_size:
            raise ValidationError(
                f"File size must be no more than {max_size // 1048576}MB"
            )

        # Check file type
        if allowed_types:
            content_type = getattr(file, "content_type", "")
            if content_type not in allowed_types:
                raise ValidationError(
                    f'File type not allowed. Allowed types: {", ".join(allowed_types)}'
                )

        # Check file extension
        filename = file.name.lower()
        dangerous_extensions = [
            ".exe",
            ".bat",
            ".cmd",
            ".com",
            ".pif",
            ".scr",
            ".vbs",
            ".js",
        ]
        if any(filename.endswith(ext) for ext in dangerous_extensions):
            raise ValidationError("This file type is not allowed for security reasons")

        return file

    @classmethod
    def sanitize_html(cls, html_content):
        """Sanitize HTML content for safe display"""
        if not html_content:
            return html_content

        # Remove dangerous tags and attributes
        allowed_tags = ["p", "br", "strong", "em", "u", "ol", "ul", "li", "blockquote"]
        allowed_attributes = ["class"]

        # Basic HTML sanitization (use bleach library for production)
        for pattern in cls.XSS_PATTERNS:
            html_content = re.sub(pattern, "", html_content, flags=re.IGNORECASE)

        return html_content
