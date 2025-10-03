# Data Schemas

## Overview

FastAPI Admin UI uses Pydantic models for data validation and serialization. This document describes all the data schemas used in the Admin UI API, their properties, validation rules, and usage examples.

## Core Schemas

### Server Information

#### `Schema__Server_Info`

Represents server runtime information.

```python
class Schema__Server_Info(Type_Safe):
    server_id         : UUID                # Unique server identifier
    server_name       : Optional[str]       # Human-readable server name
    server_instance_id: str                 # Cloud instance ID (if applicable)
    server_boot_time  : int                 # Unix timestamp of server start
    current_time      : int                 # Current Unix timestamp
    uptime_ms        : int                 # Uptime in milliseconds
```

**Example:**
```json
{
  "server_id": "550e8400-e29b-41d4-a716-446655440000",
  "server_name": "api-prod-01",
  "server_instance_id": "i-1234567890",
  "server_boot_time": 1704067200000,
  "current_time": 1704153600000,
  "uptime_ms": 86400000
}
```

#### `Schema__App_Info`
FastAPI application configuration details.

```python
class Schema__App_Info(Type_Safe):
    name           : str                    # Application name
    version        : str                    # Application version
    description    : Optional[str]          # Application description
    base_path      : str = "/"             # API base path
    docs_offline   : bool = False          # Offline documentation mode
    enable_cors    : bool = False          # CORS enabled status
    enable_api_key : bool = False          # API key authentication status
```

### Cookie Management

#### `Cookie__Config`
Configuration schema for a cookie.

```python
class Cookie__Config(Type_Safe):
    name        : str                       # Cookie name
    description : str = ""                  # Cookie description
    required    : bool = False              # Is this cookie required?
    secure      : bool = True               # HTTPS only?
    http_only   : bool = True               # HTTP only (no JS access)?
    same_site   : str = "strict"            # SameSite policy
    category    : str = "general"           # Cookie category
    validator   : Optional[str] = None      # Regex validation pattern
```

**Validation Rules:**
- `name`: Must be a valid cookie name (alphanumeric, hyphens, underscores)
- `same_site`: Must be one of: `"strict"`, `"lax"`, `"none"`
- `category`: Suggested values: `"auth"`, `"llm"`, `"general"`, `"tracking"`

#### `Cookie__Value`
Schema for setting a cookie value.

```python
class Cookie__Value(Type_Safe):
    value      : str                        # Cookie value
    expires_in : Optional[int] = None       # Expiration in seconds
```

**Validation Rules:**
- `value`: Maximum 4096 characters
- `expires_in`: Must be positive integer or None (session cookie)

#### `Cookie__Template`
Template for common cookie configurations.

```python
class Cookie__Template(Type_Safe):
    id          : str                       # Template identifier
    name        : str                       # Template name
    description : str                       # Template description
    cookies     : List[Cookie__Config]      # List of cookie configs
```

**Example:**
```json
{
  "id": "openai",
  "name": "OpenAI Configuration",
  "description": "Setup for OpenAI API",
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
```

### Route Information

#### `Schema__Route_Info`
Information about an API route.

```python
class Schema__Route_Info(Type_Safe):
    path       : str                        # Route path pattern
    methods    : List[str]                  # HTTP methods
    name       : str                        # Route function name
    tag        : str                        # Route tag/category
    is_get     : bool                       # Supports GET?
    is_post    : bool                       # Supports POST?
    is_put     : bool                       # Supports PUT?
    is_delete  : bool                       # Supports DELETE?
    parameters : List[Schema__Parameter]    # Route parameters
    responses  : Dict[int, Schema__Response] # Response schemas
```

#### `Schema__Parameter`
Route parameter definition.

```python
class Schema__Parameter(Type_Safe):
    name        : str                       # Parameter name
    in_         : str                       # Location: path, query, header, cookie
    required    : bool                      # Is required?
    schema_type : str                       # Data type
    description : Optional[str]             # Parameter description
    default     : Optional[Any]             # Default value
    example     : Optional[Any]             # Example value
```

**Validation Rules:**
- `in_`: Must be one of: `"path"`, `"query"`, `"header"`, `"cookie"`
- `schema_type`: Must be valid JSON Schema type

### Statistics

#### `Schema__Stats`
Application statistics and metrics.

```python
class Schema__Stats(Type_Safe):
    total_routes      : int                 # Total number of routes
    methods          : Dict[str, int]       # Routes by HTTP method
    prefixes         : Dict[str, int]       # Routes by prefix
    middlewares_count: int                  # Number of middlewares
    has_static_files : bool                 # Static files configured?
    request_count    : Optional[int]        # Total requests (if tracked)
    error_rate       : Optional[float]      # Error rate percentage
    avg_response_time: Optional[float]      # Average response time (ms)
```

### Admin UI Configuration

#### `Admin_UI__Config`
Complete configuration for the Admin UI.

```python
class Admin_UI__Config(Type_Safe):
    enabled           : bool = True         # Enable Admin UI?
    base_path         : str = '/admin'      # URL base path
    require_auth      : bool = True         # Require authentication?
    show_dashboard    : bool = True         # Show dashboard page?
    show_cookies      : bool = True         # Show cookie manager?
    show_routes       : bool = True         # Show routes explorer?
    show_docs         : bool = True         # Show documentation?
    allow_api_testing : bool = True         # Allow API testing?
    theme             : str = "light"       # UI theme
    max_request_size  : int = 10485760      # Max request size (10MB)
```

**Validation Rules:**
- `base_path`: Must start with `/` and be a valid URL path
- `theme`: Must be one of: `"light"`, `"dark"`, `"auto"`
- `max_request_size`: Must be positive integer

## Request/Response Schemas

### API Responses

#### `Schema__Success_Response`
Standard success response.

```python
class Schema__Success_Response(Type_Safe):
    success : bool = True                   # Operation success
    message : Optional[str]                 # Success message
    data    : Optional[Dict[str, Any]]      # Response data
```

#### `Schema__Error_Response`
Standard error response.

```python
class Schema__Error_Response(Type_Safe):
    success : bool = False                  # Operation failed
    error   : str                          # Error type
    detail  : str                          # Error details
    code    : Optional[str]                # Error code
    trace   : Optional[str]                # Stack trace (debug mode)
```

### Pagination

#### `Schema__Paginated_Response`
Response with pagination information.

```python
class Schema__Paginated_Response(Type_Safe):
    items      : List[Any]                  # Page items
    total      : int                        # Total items
    page       : int                        # Current page
    page_size  : int                        # Items per page
    total_pages: int                        # Total pages
    has_next   : bool                       # Has next page?
    has_prev   : bool                       # Has previous page?
```

### WebSocket Messages

#### `Schema__WS_Message`
WebSocket message format.

```python
class Schema__WS_Message(Type_Safe):
    type      : str                         # Message type
    timestamp : int                         # Unix timestamp
    data      : Dict[str, Any]              # Message payload
    client_id : Optional[str]               # Client identifier
```

**Message Types:**
- `"server_status"`: Server status update
- `"route_access"`: Route access notification
- `"error_alert"`: Error occurrence
- `"metric_update"`: Metric update

## Validation Examples

### Cookie Validation

```python
# Valid cookie configuration
valid_cookie = Cookie__Config(
    name="api-key",
    description="API Authentication Key",
    required=True,
    category="auth",
    validator=r"^[A-Za-z0-9]{32,64}$"
)

# Invalid - will raise validation error
invalid_cookie = Cookie__Config(
    name="invalid name!",  # Invalid characters
    same_site="invalid"    # Invalid same_site value
)
```

### Route Parameter Validation

```python
# Valid parameter
valid_param = Schema__Parameter(
    name="user_id",
    in_="path",
    required=True,
    schema_type="integer",
    description="User identifier",
    example=123
)

# Invalid - will raise validation error
invalid_param = Schema__Parameter(
    name="param",
    in_="invalid_location",  # Invalid location
    schema_type="not_a_type"  # Invalid type
)
```

## Type Safety

All schemas inherit from `Type_Safe` base class, providing:

1. **Runtime validation**: Validates data on instantiation
2. **Type hints**: Full IDE support and type checking
3. **Serialization**: Automatic JSON serialization/deserialization
4. **Documentation**: Auto-generated OpenAPI documentation

### Custom Validators

```python
from osbot_utils.type_safe import Type_Safe
from pydantic import validator

class Custom_Schema(Type_Safe):
    email: str
    age: int
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v
```

## Schema Inheritance

Schemas can be extended through inheritance:

```python
class Base_Schema(Type_Safe):
    id: str
    created_at: int
    updated_at: int

class User_Schema(Base_Schema):
    username: str
    email: str
    role: str

class Admin_User_Schema(User_Schema):
    permissions: List[str]
    super_admin: bool = False
```

## OpenAPI Integration

All schemas are automatically included in the OpenAPI specification:

```python
@app.post("/api/users", response_model=User_Schema)
async def create_user(user: User_Schema):
    # Schema validation happens automatically
    return user
```

The schemas appear in the OpenAPI JSON at `/openapi.json` under the `components.schemas` section.

## Best Practices

1. **Use Type-Safe Classes**: Always inherit from `Type_Safe` for automatic validation
2. **Provide Defaults**: Include sensible defaults for optional fields
3. **Add Descriptions**: Document fields for better OpenAPI documentation
4. **Validate Early**: Use validators to catch errors at the boundary
5. **Keep Schemas Simple**: Avoid deeply nested structures when possible
6. **Version Schemas**: Use versioning for backward compatibility

## Next Steps

- [API Endpoints](#docs/endpoints) - See schemas in action
- [Testing Guide](#docs/testing-guide) - Test with schema validation
- [Authentication](#docs/authentication) - Secure schema endpoints