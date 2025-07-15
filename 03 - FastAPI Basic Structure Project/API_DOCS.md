# API Documentation

## Overview

This FastAPI application provides a RESTful API for user management with authentication and authorization. The API follows REST principles and includes comprehensive CRUD operations.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Health Check

#### GET /
- **Description**: Root endpoint
- **Auth Required**: No
- **Response**: Welcome message

#### GET /health
- **Description**: Health check endpoint
- **Auth Required**: No
- **Response**: API health status

### Authentication

#### POST /api/v1/users/register
- **Description**: Register a new user
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "password": "password123",
    "bio": "Optional bio"
  }
  ```
- **Response**: User object (without password)
- **Status Codes**: 201 Created, 409 Conflict, 422 Validation Error

#### POST /api/v1/users/login
- **Description**: Login user and get access token
- **Auth Required**: No
- **Request Body** (form-data):
  ```
  username: user@example.com (email)
  password: password123
  ```
- **Response**:
  ```json
  {
    "access_token": "jwt-token-here",
    "token_type": "bearer"
  }
  ```
- **Status Codes**: 200 OK, 401 Unauthorized

### User Management

#### GET /api/v1/users/me
- **Description**: Get current user information
- **Auth Required**: Yes
- **Response**: Current user object
- **Status Codes**: 200 OK, 401 Unauthorized

#### PUT /api/v1/users/me
- **Description**: Update current user information
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "email": "newemail@example.com",
    "username": "newusername",
    "full_name": "New Full Name",
    "bio": "Updated bio"
  }
  ```
- **Response**: Updated user object
- **Status Codes**: 200 OK, 409 Conflict, 422 Validation Error

#### GET /api/v1/users/
- **Description**: Get list of users with pagination
- **Auth Required**: Yes
- **Query Parameters**:
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Number of records to return (default: 100, max: 1000)
- **Response**:
  ```json
  {
    "users": [user_objects],
    "total": 150,
    "page": 1,
    "per_page": 100,
    "pages": 2
  }
  ```
- **Status Codes**: 200 OK, 401 Unauthorized

#### GET /api/v1/users/{user_id}
- **Description**: Get user by ID
- **Auth Required**: Yes
- **Path Parameters**: `user_id` (integer)
- **Response**: User object
- **Status Codes**: 200 OK, 404 Not Found, 401 Unauthorized

#### PUT /api/v1/users/{user_id}
- **Description**: Update user by ID (admin or self only)
- **Auth Required**: Yes (admin or own profile)
- **Path Parameters**: `user_id` (integer)
- **Request Body**: Same as update current user
- **Response**: Updated user object
- **Status Codes**: 200 OK, 403 Forbidden, 404 Not Found, 409 Conflict

#### DELETE /api/v1/users/{user_id}
- **Description**: Deactivate user by ID (admin only)
- **Auth Required**: Yes (admin only)
- **Path Parameters**: `user_id` (integer)
- **Response**: Deactivated user object
- **Status Codes**: 200 OK, 403 Forbidden, 404 Not Found

## Data Models

### User Object
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "bio": "User bio",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "error": "ERROR_TYPE",
  "message": "Human readable error message",
  "detail": "Additional error details"
}
```

## Error Codes

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists (e.g., duplicate email)
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

## Validation Rules

### User Registration
- **Email**: Must be valid email format, unique
- **Username**: 3-50 characters, alphanumeric with underscores/hyphens, unique
- **Password**: Minimum 8 characters
- **Full Name**: Optional, max 255 characters
- **Bio**: Optional text field

### User Update
- All fields optional
- Same validation rules as registration
- Cannot update to existing email/username of another user

## Rate Limiting

Currently no rate limiting is implemented, but it's recommended for production use.

## Pagination

List endpoints support pagination with:
- `skip`: Starting record (0-based)
- `limit`: Number of records (1-1000)

Response includes:
- `total`: Total number of records
- `page`: Current page number
- `per_page`: Records per page
- `pages`: Total number of pages

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Usage

### Register and Login Flow

1. **Register a new user**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/users/register" \
        -H "Content-Type: application/json" \
        -d '{
          "email": "test@example.com",
          "username": "testuser",
          "password": "testpass123"
        }'
   ```

2. **Login to get token**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/users/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test@example.com&password=testpass123"
   ```

3. **Use token for authenticated requests**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/users/me" \
        -H "Authorization: Bearer <your-token-here>"
   ```

## Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes (configurable)
- Sensitive endpoints require authentication
- Admin-only endpoints check superuser status
- Input validation prevents common attacks
- CORS is configured for cross-origin requests
