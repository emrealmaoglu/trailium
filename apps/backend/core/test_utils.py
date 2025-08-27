import logging

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from factory import Faker
from factory.django import DjangoModelFactory
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

# Disable logging during tests
logging.disable(logging.CRITICAL)

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common utilities"""

    def setUp(self):
        self.client = Client()
        self.user = None
        self.admin_user = None

    def create_user(self, **kwargs):
        """Create a test user"""
        defaults = {
            "username": Faker("user_name").generate(),
            "email": Faker("email").generate(),
            "password": "TestPass123!",
            "is_active": True,
        }
        defaults.update(kwargs)

        user = User.objects.create_user(**defaults)
        if kwargs.get("is_superuser", False):
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.admin_user = user
        else:
            self.user = user

        return user

    def login_user(self, user=None):
        """Login a user"""
        if user is None:
            user = self.user or self.create_user()

        self.client.force_login(user)
        return user

    def assertResponseSuccess(self, response, expected_status=200):
        """Assert response is successful"""
        self.assertEqual(response.status_code, expected_status)

    def assertResponseError(self, response, expected_status=400):
        """Assert response is an error"""
        self.assertEqual(response.status_code, expected_status)

    def assertResponseNotFound(self, response):
        """Assert response is not found"""
        self.assertEqual(response.status_code, 404)

    def assertResponseForbidden(self, response):
        """Assert response is forbidden"""
        self.assertEqual(response.status_code, 403)

    def assertResponseUnauthorized(self, response):
        """Assert response is unauthorized"""
        self.assertEqual(response.status_code, 401)


class BaseAPITestCase(APITestCase):
    """Base API test case with authentication utilities"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = None
        self.admin_user = None

    def create_user(self, **kwargs):
        """Create a test user"""
        defaults = {
            "username": Faker("user_name").generate(),
            "email": Faker("email").generate(),
            "password": "TestPass123!",
            "is_active": True,
        }
        defaults.update(kwargs)

        user = User.objects.create_user(**defaults)
        if kwargs.get("is_superuser", False):
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.admin_user = user
        else:
            self.user = user

        return user

    def authenticate_user(self, user=None):
        """Authenticate a user with JWT tokens"""
        if user is None:
            user = self.user or self.create_user()

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return user

    def authenticate_admin(self):
        """Authenticate as admin user"""
        if not self.admin_user:
            self.admin_user = self.create_user(is_superuser=True)
        return self.authenticate_user(self.admin_user)

    def assertResponseSuccess(self, response, expected_status=200):
        """Assert API response is successful"""
        self.assertEqual(response.status_code, expected_status)

    def assertResponseError(self, response, expected_status=400):
        """Assert API response is an error"""
        self.assertEqual(response.status_code, expected_status)

    def assertResponseNotFound(self, response):
        """Assert API response is not found"""
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def assertResponseForbidden(self, response):
        """Assert API response is forbidden"""
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def assertResponseUnauthorized(self, response):
        """Assert API response is unauthorized"""
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assertResponseCreated(self, response):
        """Assert API response is created"""
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def assertResponseNoContent(self, response):
        """Assert API response has no content"""
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def assertResponseBadRequest(self, response):
        """Assert API response is bad request"""
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def assertResponseValidationError(self, response, field_name=None):
        """Assert API response has validation errors"""
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        if field_name:
            self.assertIn(field_name, response.data)

    def assertResponseRateLimited(self, response):
        """Assert API response is rate limited"""
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class UserFactory(DjangoModelFactory):
    """Factory for creating test users"""

    class Meta:
        model = User

    username = Faker("user_name")
    email = Faker("email")
    password = Faker(
        "password",
        length=12,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create user with proper password hashing"""
        password = kwargs.pop("password", "TestPass123!")
        user = super()._create(model_class, *args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class AdminUserFactory(UserFactory):
    """Factory for creating admin users"""

    is_superuser = True
    is_staff = True


class TestDataMixin:
    """Mixin for creating test data"""

    def create_test_users(self, count=5):
        """Create multiple test users"""
        users = []
        for i in range(count):
            user = UserFactory()
            users.append(user)
        return users

    def create_test_posts(self, user=None, count=3):
        """Create test posts"""
        from social.models import Post

        if user is None:
            user = self.user or self.create_user()

        posts = []
        for i in range(count):
            post = Post.objects.create(
                user=user,
                title=f"Test Post {i+1}",
                body=f"This is test post content {i+1}",
                is_published=True,
            )
            posts.append(post)

        return posts

    def create_test_comments(self, post, user=None, count=2):
        """Create test comments"""
        from social.models import Comment

        if user is None:
            user = self.user or self.create_user()

        comments = []
        for i in range(count):
            comment = Comment.objects.create(
                post=post, user=user, body=f"Test comment {i+1}"
            )
            comments.append(comment)

        return comments


class SecurityTestMixin:
    """Mixin for security testing"""

    def test_xss_protection(self, endpoint, data_field, malicious_input):
        """Test XSS protection for an endpoint"""
        # Test with malicious input
        malicious_data = {data_field: malicious_input}

        if hasattr(self, "user") and self.user:
            self.authenticate_user()

        response = self.client.post(endpoint, malicious_data, format="json")

        # Should either reject the request or sanitize the input
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            # Request was rejected - good
            self.assertIn("invalid content", response.data.get("message", "").lower())
        elif response.status_code == status.HTTP_201_CREATED:
            # Request was accepted - check if input was sanitized
            created_object = response.data
            stored_value = created_object.get(data_field, "")
            self.assertNotIn("<script>", stored_value)
            self.assertNotIn("javascript:", stored_value)

    def test_sql_injection_protection(self, endpoint, data_field, malicious_input):
        """Test SQL injection protection"""
        malicious_data = {data_field: malicious_input}

        if hasattr(self, "user") and self.user:
            self.authenticate_user()

        response = self.client.post(endpoint, malicious_data, format="json")

        # Should reject malicious input
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invalid content", response.data.get("message", "").lower())

    def test_authentication_required(self, endpoint, method="get"):
        """Test that authentication is required"""
        # Try without authentication
        if method.lower() == "get":
            response = self.client.get(endpoint)
        elif method.lower() == "post":
            response = self.client.post(endpoint, {}, format="json")
        elif method.lower() == "put":
            response = self.client.put(endpoint, {}, format="json")
        elif method.lower() == "delete":
            response = self.client.delete(endpoint)
        else:
            raise ValueError(f"Unsupported method: {method}")

        # Should require authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permission_required(self, endpoint, method="get", data=None):
        """Test that proper permissions are required"""
        # Create a regular user
        user = self.create_user()
        self.authenticate_user(user)

        # Try to access endpoint
        if method.lower() == "get":
            response = self.client.get(endpoint)
        elif method.lower() == "post":
            response = self.client.post(endpoint, data or {}, format="json")
        elif method.lower() == "put":
            response = self.client.put(endpoint, data or {}, format="json")
        elif method.lower() == "delete":
            response = self.client.delete(endpoint)
        else:
            raise ValueError(f"Unsupported method: {method}")

        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PerformanceTestMixin:
    """Mixin for performance testing"""

    def test_response_time(self, endpoint, max_time=1000):
        """Test that response time is within acceptable limits"""
        import time

        start_time = time.time()
        response = self.client.get(endpoint)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        self.assertLess(
            response_time,
            max_time,
            f"Response time {response_time:.2f}ms exceeds limit {max_time}ms",
        )

    def test_database_queries(self, endpoint, max_queries=10):
        """Test that database queries are optimized"""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as context:
            response = self.client.get(endpoint)

        query_count = len(context.captured_queries)
        self.assertLess(
            query_count,
            max_queries,
            f"Too many database queries: {query_count} (max: {max_queries})",
        )

        # Log slow queries
        for query in context.captured_queries:
            if query["time"] > 100:  # 100ms threshold
                print(
                    f"Slow query detected: {query['sql'][:100]}... ({query['time']}ms)"
                )
