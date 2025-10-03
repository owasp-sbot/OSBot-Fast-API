# API Endpoints

## Overview

The FastAPI Admin UI exposes a comprehensive set of API endpoints for managing and monitoring your FastAPI application. All Admin UI endpoints are prefixed with `/admin` by default (configurable via `base_path`).

## Endpoint Categories

### 1. Server Information (`/admin/admin-info/api/*`)

These endpoints provide real-time information about your server and application status.

#### `GET /admin/admin-info/api/server-info`
Returns server runtime information.

**Response:**
```json
{
  "server_id": "550e8400-e29b-41d4-a716-446655440000",
  "server_name": "production-api-01",
  "server_instance_id": "i-1234567890abcdef0",
  "server_boot_time": 1704067200000,
  "current_time": 1704153600000,
  "uptime_ms": 86400000
}
```

#### `GET /admin/admin-info/api/app-info`
Returns FastAPI application configuration.

**Response:**
```json
{
  "name": "My FastAPI App",
  "version": "1.0.0",
  "description": "Production API Server",
  "base_path": "/",
  "docs_offline": false,
  "enable_cors": true,
  "enable_api_key": true
}
```

#### `GET /admin/admin-info/api/stats`
Returns application statistics and metrics.

**Response:**
```json
{
  "total_routes": 42,
  "methods": {
    "GET": 25,
    "POST": 10,
    "PUT": 4,
    "DELETE": 3
  },
  "prefixes": {
    "/api": 30,
    "/admin": 12
  },
  "middlewares_count": 5,
  "has_static_files": true
}
```

#### `GET /admin/admin-info/api/health`
Health check endpoint for monitoring tools.

**Response:**
```json
{
  "status": "Ok",
  "timestamp": "1704153600000"
}
```

### 2. Route Configuration (`/admin/admin-config/api/*`)

Endpoints for exploring and managing API routes.

#### `GET /admin/admin-config/api/routes`
Returns all application routes with metadata.

**Response:**
```json
[
  {
    "path": "/api/users/{user_id}",
    "methods": ["GET", "PUT", "DELETE"],
    "name": "get_user",
    "tag": "users",
    "is_get": true,
    "is_post": false,
    "is_put": true,
    "is_delete": true
  }
]
```

#### `GET /admin/admin-config/api/routes-grouped`
Returns routes grouped by their prefix/tag.

**Response:**
```json
{
  "users": [
    {
      "path": "/api/users",
      "methods": ["GET", "POST"],
      "name": "list_users"
    }
  ],
  "auth": [
    {
      "path": "/api/auth/login",
      "methods": ["POST"],
      "name": "login"
    }
  ]
}
```

#### `GET /admin/admin-config/api/middlewares`
Returns information about installed middleware.

**Response:**
```json
[
  {
    "name": "CORSMiddleware",
    "class": "fastapi.middleware.cors.CORSMiddleware",
    "config": {
      "allow_origins": ["*"],
      "allow_methods": ["GET", "POST"]
    }
  }
]
```

#### `GET /admin/admin-config/api/openapi-spec`
Returns the complete OpenAPI specification.

**Response:**
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "My API",
    "version": "1.0.0"
  },
  "paths": {},
  "components": {}
}
```

### 3. Cookie Management (`/admin/admin-cookies/api/*`)

Endpoints for managing cookies and authentication tokens.

#### `GET /admin/admin-cookies/api/cookies-list`
Lists all configured cookies with their current values.

**Request Headers:**
```
Cookie: auth-token=abc123; api-key=xyz789
```

**Response:**
```json
[
  {
    "name": "auth-token",
    "description": "Authentication token",
    "category": "auth",
    "required": false,
    "has_value": true,
    "value_length": 6,
    "is_valid": true
  }
]
```

#### `GET /admin/admin-cookies/api/cookies-templates`
Returns available cookie configuration templates.

**Response:**
```json
[
  {
    "id": "openai",
    "name": "OpenAI Configuration",
    "description": "Cookies for OpenAI API integration",
    "cookies": [
      {
        "name": "openai-api-key",
        "description": "OpenAI API Key",
        "required": true,
        "category": "llm",
        "validator": "^sk-[a-zA-Z0-9]{48}$"
      }
    ]
  }
]
```

#### `GET /admin/admin-cookies/api/cookie-get/{cookie_name}`
Retrieves a specific cookie's value and configuration.

**Response:**
```json
{
  "name": "api-key",
  "value": "sk-1234567890",
  "exists": true,
  "config": {
    "description": "API Key",
    "required": true,
    "secure": true
  },
  "is_valid": true
}
```

#### `POST /admin/admin-cookies/api/cookie-set/{cookie_name}`
Sets or updates a cookie value.

**Request Body:**
```json
{
  "value": "new-api-key-value",
  "expires_in": 3600
}
```

**Response:**
```json
{
  "success": true,
  "name": "api-key",
  "value_set": true
}
```

#### `DELETE /admin/admin-cookies/api/cookie-delete/{cookie_name}`
Deletes a cookie.

**Response:**
```json
{
  "success": true,
  "name": "api-key",
  "deleted": true
}
```

#### `POST /admin/admin-cookies/api/cookies-bulk-set`
Sets multiple cookies at once.

**Request Body:**
```json
{
  "cookies_templates": [
    {
      "name": "auth-token",
      "value": "token-123"
    },
    {
      "name": "api-key",
      "value": "key-456"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {"success": true, "name": "auth-token"},
    {"success": true, "name": "api-key"}
  ]
}
```

#### `GET /admin/admin-cookies/api/generate-value`
Generates random values for cookies (UUIDs, API keys, etc.).

**Query Parameters:**
- `value_type`: Type of value to generate (`uuid`, `api_key`)

**Response:**
```json
{
  "value": "550e8400-e29b-41d4-a716-446655440000",
  "type": "uuid"
}
```

### 4. Documentation (`/admin/admin-docs/api/*`)

Endpoints for accessing documentation content.

#### `GET /admin/admin-docs/api/docs-endpoints`
Returns available documentation endpoints.

**Response:**
```json
[
  {
    "name": "Swagger UI",
    "description": "Interactive API documentation",
    "url": "/docs",
    "type": "swagger",
    "icon": "swagger"
  }
]
```

#### `GET /admin/admin-docs/api/client-examples`
Returns code examples for different programming languages.

**Response:**
```json
{
  "curl": {
    "name": "cURL",
    "description": "Command line HTTP client",
    "example": "curl -X GET http://localhost:8000/api/users"
  },
  "python": {
    "name": "Python",
    "description": "Python with requests library",
    "example": "import requests\nresponse = requests.get('http://localhost:8000/api/users')"
  }
}
```

#### `GET /admin/admin-docs/api/api-info`
Returns API metadata and OpenAPI information.

**Response:**
```json
{
  "openapi_version": "3.0.0",
  "api_title": "My API",
  "api_version": "1.0.0",
  "api_description": "Production API",
  "servers": [
    {"url": "http://localhost:8000"}
  ],
  "total_paths": 42,
  "total_schemas": 15,
  "tags": [
    {
      "name": "users",
      "count": 5,
      "description": "User management"
    }
  ]
}
```

#### `GET /admin/admin-docs/api/content/{doc_id}`
Returns documentation content for a specific document.

**Response:**
```json
{
  "markdown": "# Quick Start Guide\n\n## Installation...",
  "format": "markdown",
  "doc_id": "quickstart"
}
```

### 5. Static Resources (`/admin/admin-static/*`)

Endpoints for serving Admin UI static files.

#### `GET /admin/admin-static/index`
Returns the main Admin UI HTML page.

#### `GET /admin/admin-static/serve-css/{filename}`
Serves CSS stylesheets.

#### `GET /admin/admin-static/serve-js/{filename}`
Serves JavaScript files.

#### `GET /admin/admin-static/serve-js/components/{filename}`
Serves JavaScript component files.

## Authentication

All Admin UI endpoints respect the authentication configuration:

### With API Key Authentication

Include the API key in your request headers:

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/admin/admin-info/api/server-info
```

### With Cookie Authentication

Cookies are automatically sent by the browser:

```javascript
fetch('/admin/admin-info/api/server-info', {
  credentials: 'include'
})
```

## Rate Limiting

Admin UI endpoints may be subject to rate limiting:

- Default: 100 requests per hour per IP
- Sensitive endpoints: 10 requests per minute
- Bulk operations: 5 requests per minute

## Error Responses

All endpoints follow a consistent error response format:

### 400 Bad Request
```json
{
  "error": "Invalid request",
  "detail": "Missing required parameter: cookie_name"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "detail": "Missing or invalid API key"
}
```

### 403 Forbidden
```json
{
  "error": "Permission denied",
  "detail": "Insufficient permissions for this operation"
}
```

### 404 Not Found
```json
{
  "error": "Not found",
  "detail": "Cookie 'unknown-cookie' does not exist"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "detail": "An unexpected error occurred"
}
```

## Pagination

Some endpoints support pagination for large result sets:

**Query Parameters:**
- `limit`: Number of items per page (default: 20, max: 100)
- `offset`: Number of items to skip (default: 0)

**Response Headers:**
- `X-Total-Count`: Total number of items
- `X-Page-Count`: Total number of pages

## WebSocket Support

For real-time updates, connect to the WebSocket endpoint:

```javascript
const ws = new WebSocket('ws://localhost:8000/admin/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Server update:', data);
};
```

## Next Steps

- [Testing Guide](#docs/testing-guide) - Learn to test these endpoints
- [Authentication](#docs/authentication) - Secure your endpoints
- [Cookie Management](#docs/cookies-guide) - Manage API credentials