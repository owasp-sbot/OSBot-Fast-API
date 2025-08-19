# OSBot-Fast-API - LLM Brief: Introduction, Patterns, and Principles

## Executive Summary

OSBot-Fast-API is a sophisticated FastAPI wrapper that enforces type safety, provides comprehensive HTTP event tracking, and implements enterprise-grade middleware patterns. Built on top of FastAPI, it adds a layer of conventions, type transformations, and production-ready features while maintaining FastAPI's performance and compatibility.

**Repository**: https://github.com/owasp-sbot/OSBot-Fast-API/  
**PyPI Package**: https://pypi.org/project/osbot-fast-api/

## Core Design Philosophy

### 1. Type Safety First
Every class inherits from `Type_Safe`, ensuring runtime validation and consistent object behavior throughout the application lifecycle.

### 2. Convention Over Configuration
Function names automatically generate RESTful paths, reducing boilerplate while maintaining flexibility.

### 3. Alignment-Based Code Formatting
Systematic visual alignment patterns improve code readability and reduce cognitive load.

### 4. Transformer Pattern Architecture
Bidirectional converters between type systems (Type_Safe ↔ BaseModel ↔ Dataclass ↔ JSON) enable seamless integration.

### 5. Event-Driven Observability
Complete HTTP lifecycle monitoring with `Fast_API__Http_Event` for debugging, auditing, and performance tracking.

## Installation

```bash
pip install osbot-fast-api
```

## Core Patterns and Principles

### Pattern 1: Type_Safe Base Pattern

**Principle**: All data models and API classes inherit from `Type_Safe` for automatic validation and serialization.

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from typing import List, Optional

class Fast_API(Type_Safe):
    base_path      : Safe_Str__Fast_API__Route__Prefix = '/'
    docs_offline   : bool                              = True    # Note alignment
    enable_cors    : bool                              = False   # Consistent spacing
    enable_api_key : bool                              = False   # Visual clarity
    name           : Safe_Str__Fast_API__Name          = None
    version        : Safe_Str__Version                 = version__osbot_fast_api
```

**Why This Matters**:
- Automatic validation at instantiation
- Self-documenting through type annotations
- Prevents runtime type errors
- Enables automatic serialization/deserialization
- No need for Pydantic's Field() - just use regular assignments

### Pattern 2: Convention-Based Routing

**Principle**: Method names automatically generate RESTful endpoints using a predictable convention.

```python
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes

class Routes__Users(Fast_API__Routes):
    tag = 'users'  # Automatically creates prefix '/users'
    
    def list_users(self):                           # → /users/list-users
        return {"users": ["alice", "bob"]}
    
    def get_user__by__id(self, id: str):           # → /users/get-user/by/{id}
        return {"user_id": id}
    
    def update_user__id(self, id: str):            # → /users/update-user/{id}
        return {"updated": id}
    
    def setup_routes(self):
        self.add_route_get(self.list_users)
        self.add_route_get(self.get_user__by__id)
        self.add_route_put(self.update_user__id)
```

**Naming Rules**:
- Single underscore becomes hyphen: `get_users` → `/get-users`
- Double underscore creates path parameters: `user__id` → `/user/{id}`
- Multiple parameters: `user__id_posts__post_id` → `/user/{id}/posts/{post_id}`

### Pattern 3: Alignment-Based Formatting

**Principle**: Maintain visual clarity through consistent alignment of related code elements.

```python
# Variables aligned by equals sign
base_path      : Safe_Str__Fast_API__Route__Prefix = '/'
docs_offline   : bool                              = True
enable_cors    : bool                              = False

# Dictionary creation with aligned colons
return dict(type         = self.type        ,
           client       = self.address     ,
           path         = self.url         ,
           method       = self.method      ,
           headers      = self.req_headers )

# Method calls with aligned parameters
kwargs = dict(fast_api_name = self.name      ,
             version       = self.version    ,
             description   = self.description)
```

### Pattern 4: Safe String Types with Domain Validation

**Principle**: Use domain-specific safe string types for validation at the type level.

```python
class Safe_Str__Fast_API__Route__Prefix(Safe_Str__Fast_API__Route__Tag):
    """FastAPI route prefix with automatic formatting."""
    
    def __new__(cls, value: str = None):
        instance = super().__new__(cls, value)
        result = str(instance).lower()
        
        # Clean and normalize the path
        result = result.lstrip('/').rstrip('/')
        while '//' in result:
            result = result.replace('//', '/')
        
        if result and not result.startswith('/'):
            result = '/' + result
        return str.__new__(cls, result)
```

### Pattern 5: Type Transformation System

**Principle**: Seamless conversion between different type systems without manual intervention.

```python
# Type_Safe to BaseModel (automatic in routes)
from osbot_fast_api.api.transformers.Type_Safe__To__BaseModel import type_safe__to__basemodel

class User_Model(Type_Safe):
    user_id  : Random_Guid
    username : Safe_Str
    email    : Safe_Str__Email
    age      : Safe_Int
    tags     : List[Safe_Str]

# Automatic conversion for FastAPI
basemodel_class = type_safe__to__basemodel.convert_class(User_Model)

# Manual conversion if needed
instance = User_Model(username="Alice", email="alice@example.com", age=30)
basemodel_instance = type_safe__to__basemodel.convert_instance(instance)
```

**Available Transformers**:
- `Type_Safe__To__BaseModel`: For FastAPI integration
- `BaseModel__To__Type_Safe`: For response processing  
- `Type_Safe__To__Json`: JSON Schema generation
- `Type_Safe__To__OpenAPI`: OpenAPI spec generation
- `Type_Safe__To__LLM_Tools`: LLM function calling formats

### Pattern 6: Middleware Stack Architecture

**Principle**: Layered middleware with specific execution order for proper functionality.

```python
class Fast_API(Type_Safe):
    def setup_middlewares(self):
        # Order is critical!
        self.setup_middleware__detect_disconnect()   # 1. Connection monitoring
        self.setup_middleware__http_events()         # 2. Event tracking
        self.setup_middleware__cors()                # 3. CORS if enabled
        self.setup_middleware__api_key_check()       # 4. Authentication
        return self
```

### Pattern 7: HTTP Event Tracking

**Principle**: Complete request/response audit trail with performance metrics.

```python
class Fast_API__Http_Event(Type_Safe):
    http_event_info     : Fast_API__Http_Event__Info      # Metadata
    http_event_request  : Fast_API__Http_Event__Request   # Request details
    http_event_response : Fast_API__Http_Event__Response  # Response details
    http_event_traces   : Fast_API__Http_Event__Traces    # Execution traces
    event_id            : Random_Guid                     # Unique identifier
    
    def on_request(self, request: Request):
        self.http_event_request.headers    = dict(request.headers)
        self.http_event_request.method     = request.method
        self.http_event_request.path       = request.url.path
        self.http_event_request.start_time = Decimal(time.time())
```

### Pattern 8: Context Manager Testing

**Principle**: Use context managers for clean resource management in tests.

```python
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server

with Fast_API_Server(app=api.app()) as server:
    response = server.requests_get('/health-check')
    assert response.status_code == 200
    # Server automatically stops when context exits
```

## Quick Start Examples

### Minimal Application

```python
from osbot_fast_api.api.Fast_API import Fast_API

# Create and setup FastAPI application
fast_api = Fast_API()
fast_api.setup()

# Get the FastAPI app instance for uvicorn
app = fast_api.app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Type-Safe API with Routes

```python
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe import Type_Safe

# Define Type-Safe schemas
class User_Request(Type_Safe):
    username : Safe_Str
    email    : Safe_Str__Email
    age      : Safe_Int

class User_Response(Type_Safe):
    user_id  : Random_Guid
    username : Safe_Str
    created  : bool

# Define routes with automatic type conversion
class Routes__API(Fast_API__Routes):
    tag = 'api'
    
    def create_user(self, user: User_Request) -> User_Response:
        # Type_Safe objects automatically converted
        print(f"Creating user: {user.username}")
        
        return User_Response(
            user_id=Random_Guid(),
            username=user.username,
            created=True
        )
    
    def setup_routes(self):
        self.add_route_post(self.create_user)  # POST /api/create-user

# Setup application
fast_api = Fast_API(
    enable_cors=True,      # Enable CORS
    enable_api_key=True,   # Enable API key validation
    docs_offline=True      # Use offline documentation
)
fast_api.setup()
fast_api.add_routes(Routes__API)
app = fast_api.app()
```

## Critical Implementation Rules

### NEVER Do This:
```python
# ❌ WRONG - Don't use FastAPI directly
from fastapi import FastAPI
app = FastAPI()

# ❌ WRONG - Don't use Pydantic BaseModel
from pydantic import BaseModel
class User(BaseModel):
    name: str

# ❌ WRONG - Don't use decorators for routes
@app.get("/users")
def get_users():
    return []
```

### ALWAYS Do This:
```python
# ✅ CORRECT - Use Fast_API class
from osbot_fast_api.api.Fast_API import Fast_API
fast_api = Fast_API()

# ✅ CORRECT - Use Type_Safe for models
from osbot_utils.type_safe.Type_Safe import Type_Safe
class User(Type_Safe):
    name: Safe_Str

# ✅ CORRECT - Use Fast_API__Routes with setup_routes()
class Routes__Users(Fast_API__Routes):
    def setup_routes(self):
        self.add_route_get(self.get_users)
```

## Environment Configuration

### API Key Authentication
```bash
export FAST_API__AUTH__API_KEY__NAME="X-API-Key"
export FAST_API__AUTH__API_KEY__VALUE="your-secret-key-here"
```

### Server Identification
```bash
export FAST_API__SERVER_ID="unique-server-guid"
export FAST_API__SERVER_NAME="production-api-01"
```

## AWS Lambda Deployment

```python
from osbot_fast_api.api.Fast_API import Fast_API
from mangum import Mangum

# Create application
fast_api = Fast_API()
fast_api.setup()
fast_api.add_routes(Routes__API)

# Create Lambda handler
app = fast_api.app()
handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)
```

## Key Benefits

1. **Type Safety**: Runtime validation prevents errors before they reach production
2. **Convention-Based**: Reduces boilerplate while maintaining flexibility
3. **Production Ready**: Built-in middleware, event tracking, and error handling
4. **Testing Support**: Comprehensive testing utilities and patterns
5. **Documentation**: Automatic OpenAPI/Swagger generation with offline support
6. **Observability**: Complete HTTP event tracking for debugging and monitoring
7. **AWS Compatible**: Ready for serverless deployment with Lambda
8. **LLM Friendly**: Consistent patterns make it easy for AI assistants to generate correct code

## Best Practices Summary

1. **Always use Type_Safe classes** - Never use raw Pydantic BaseModel
2. **Organize routes in Fast_API__Routes classes** - Group by domain
3. **Follow naming conventions** - Use double underscores for path parameters
4. **Enable appropriate middleware** - Based on environment needs
5. **Use environment variables** - For all configuration
6. **Test with TestClient and Fast_API_Server** - Depending on use case
7. **Monitor with HTTP events** - In production environments
8. **Cache expensive operations** - Use `@cache_on_self` decorator
9. **Document complex logic** - With aligned inline comments
10. **Maintain alignment patterns** - For code readability

## Summary

OSBot-Fast-API provides a robust, type-safe foundation for building production APIs with FastAPI. The consistent coding patterns, comprehensive type system, and extensive middleware support enable rapid development while maintaining code quality and maintainability. The framework's convention-over-configuration approach, combined with its powerful type transformation system, makes it ideal for teams building enterprise-grade APIs that require both flexibility and safety.