# 🚀 Trailium API Documentation

**Complete API reference for the Trailium social platform**

## 📋 Table of Contents

- [Authentication](#authentication)
- [Users](#users)
- [Posts](#posts)
- [Comments](#comments)
- [Todos](#todos)
- [Albums](#albums)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Pagination](#pagination)

## 🔐 Authentication

### JWT Token System

Trailium uses JWT (JSON Web Tokens) for authentication with httpOnly cookies for security.

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_premium": false,
    "is_private": false
  }
}
```

**Cookies Set:**
- `access_token`: JWT access token (1 hour expiry)
- `refresh_token`: JWT refresh token (7 days expiry)

#### Register
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

#### Refresh Token
```http
POST /api/auth/refresh/
```

**Response:**
```json
{
  "message": "Token refreshed successfully"
}
```

#### Logout
```http
POST /api/auth/logout/
```

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

## 👥 Users

### Get Users List
```http
GET /api/users/?page=1&search=john&premium=true&private=false
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `search`: Search by username or full name
- `premium`: Filter premium users (true/false)
- `private`: Filter private accounts (true/false)

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "avatar": "https://example.com/avatars/john.jpg",
      "about": "Software developer",
      "is_premium": false,
      "is_private": false,
      "created_at": "2025-01-01T00:00:00Z",
      "last_login": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### Get User Details
```http
GET /api/users/{id}/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "avatar": "https://example.com/avatars/john.jpg",
  "about": "Software developer",
  "phone": "+1234567890",
  "address": "123 Main St, City, Country",
  "company": "Tech Corp",
  "website": "https://johndoe.com",
  "is_premium": false,
  "is_private": false,
  "profile_privacy": "public",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Update User Profile
```http
PUT /api/users/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Smith",
  "about": "Full-stack developer",
  "is_private": true
}
```

### Follow/Unfollow User
```http
POST /api/users/{id}/follow/
DELETE /api/users/{id}/follow/
Authorization: Bearer <access_token>
```

## 📝 Posts

### Get Posts List
```http
GET /api/posts/?page=1&user=1&search=technology
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number
- `user`: Filter by user ID
- `search`: Search in title and body
- `ordering`: Sort order (newest, oldest, popular)

### Create Post
```http
POST /api/posts/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "title": "My First Post",
  "body": "This is the content of my post",
  "photos": [file1, file2]
}
```

**Photo Requirements:**
- Maximum 4 photos per post
- Supported formats: JPEG, PNG, GIF
- Maximum size: 10MB per photo

### Get Post Details
```http
GET /api/posts/{id}/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "title": "My First Post",
  "body": "This is the content of my post",
  "user": {
    "id": 1,
    "username": "john_doe",
    "full_name": "John Doe"
  },
  "photos": [
    {
      "id": 1,
      "url": "https://example.com/photos/photo1.jpg",
      "caption": "Beautiful sunset"
    }
  ],
  "likes_count": 15,
  "comments_count": 8,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Update Post
```http
PUT /api/posts/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Post Title",
  "body": "Updated post content"
}
```

### Delete Post
```http
DELETE /api/posts/{id}/
Authorization: Bearer <access_token>
```

### Like/Unlike Post
```http
POST /api/posts/{id}/like/
DELETE /api/posts/{id}/like/
Authorization: Bearer <access_token>
```

## 💬 Comments

### Get Post Comments
```http
GET /api/posts/{id}/comments/
Authorization: Bearer <access_token>
```

### Add Comment
```http
POST /api/posts/{id}/comments/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "body": "Great post! Thanks for sharing."
}
```

### Update Comment
```http
PUT /api/posts/{post_id}/comments/{comment_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "body": "Updated comment text"
}
```

### Delete Comment
```http
DELETE /api/posts/{post_id}/comments/{comment_id}/
Authorization: Bearer <access_token>
```

## ✅ Todos

### Get Todos List
```http
GET /api/todos/?page=1&user=1&completed=false
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number
- `user`: Filter by user ID
- `completed`: Filter by completion status
- `priority`: Filter by priority (low, medium, high)

### Create Todo
```http
POST /api/todos/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "priority": "high",
  "due_date": "2025-01-20"
}
```

### Update Todo
```http
PUT /api/todos/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated todo title",
  "completed": true
}
```

### Delete Todo
```http
DELETE /api/todos/{id}/
Authorization: Bearer <access_token>
```

## 📸 Albums

### Get Albums List
```http
GET /api/albums/?page=1&user=1
Authorization: Bearer <access_token>
```

### Create Album
```http
POST /api/albums/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "title": "Vacation Photos",
  "description": "Photos from my summer vacation",
  "photos": [file1, file2, file3]
}
```

### Get Album Details
```http
GET /api/albums/{id}/
Authorization: Bearer <access_token>
```

## ⚠️ Error Handling

### Error Response Format
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Specific field error"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_REQUIRED` | 401 | Authentication required |
| `INVALID_TOKEN` | 401 | Invalid or expired token |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `RATE_LIMITED` | 429 | Rate limit exceeded |

### Example Error Responses

#### Authentication Required
```json
{
  "error": "Authentication credentials were not provided",
  "code": "AUTH_REQUIRED"
}
```

#### Validation Error
```json
{
  "error": "Invalid input data",
  "code": "VALIDATION_ERROR",
  "details": {
    "password": "Password must be at least 8 characters long"
  }
}
```

#### Rate Limited
```json
{
  "error": "Rate limit exceeded. Try again in 60 seconds.",
  "code": "RATE_LIMITED"
}
```

## 🚦 Rate Limiting

### Rate Limits

| Endpoint Type | Anonymous | Authenticated |
|---------------|-----------|---------------|
| Authentication | 5/hour | N/A |
| General API | 100/hour | 1000/hour |
| File Uploads | 10/hour | 50/hour |
| Search | 30/hour | 200/hour |

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642233600
```

## 📄 Pagination

### Pagination Response Format
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [...]
}
```

### Pagination Parameters
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

### Example Pagination
```http
GET /api/users/?page=2&page_size=10
```

## 🔒 Security

### HTTPS Required
All production API calls must use HTTPS.

### CORS Policy
- Origin validation
- Credentials support
- Preflight request handling

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

## 📱 Mobile Considerations

### Response Optimization
- Minimal payload size
- Efficient pagination
- Conditional field inclusion

### Offline Support
- Cache-friendly responses
- ETag support
- Last-modified headers

## 🧪 Testing

### Test Endpoints
```http
GET /api/health/
GET /api/health/detailed/
```

### Mock Data
Use the `/api/seed-demo/` endpoint to populate test data.

## 📚 SDKs & Libraries

### Official SDKs
- **JavaScript/TypeScript**: `@trailium/sdk`
- **Python**: `trailium-python`
- **React**: `@trailium/react`

### Community Libraries
- **Vue.js**: `vue-trailium`
- **Flutter**: `trailium_flutter`
- **Swift**: `TrailiumKit`

---

**For more information, visit our [Developer Portal](https://developers.trailium.com)**
