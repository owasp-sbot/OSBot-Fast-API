# LLM Prompts for OSBot-Fast-API

## 📋 Overview

This guide provides prompts for Large Language Models (like Claude, GPT-4, etc.) to effectively work with the OSBot-Fast-API package. These prompts help LLMs understand the package's patterns and generate correct code.

## 🚀 Basic Application Prompts

### Creating a FastAPI Service

```
Create a FastAPI service using OSBot-Fast-API that:
1. Uses the Fast_API class as the base, not regular FastAPI
2. Implements routes using Fast_API_Routes classes with descriptive tags
3. Each route class should extend Fast_API_Routes and implement setup_routes()
4. Use method naming convention: method_name becomes /method-name
5. For path parameters use double underscore: method__param becomes /method/{param}
6. Enable CORS and API key authentication if needed
7. Call fast_api.setup() before adding routes
8. Get the app instance with fast_api.app()
```

### Adding Type-Safe Routes

```
Add a new route to OSBot-Fast-API that:
1. Extends Fast_API_Routes with appropriate tag property
2. Uses Type_Safe classes (not Pydantic BaseModel) for request/response schemas
3. Type_Safe classes should inherit from Type_Safe, not BaseModel
4. Implements add_route_get/post/put/delete in setup_routes() method
5. Follows naming: an_endpoint() → /an-endpoint
6. For resources: users__id_profile() → /users/{id}/profile
7. Parameters are automatically converted from BaseModel to Type_Safe
8. Return Type_Safe objects, they're auto-converted to JSON
```

## 🔐 Type-Safe Schema Prompts

### Creating Type-Safe Classes

```
Create Type-Safe schemas for OSBot-Fast-API:
1. Import from osbot_utils.type_safe.Type_Safe
2. Classes must inherit from Type_Safe, not BaseModel or dataclass
3. Use standard Python type hints (str, int, float, bool)
4. For collections use: List[T], Dict[K,V], Set[T]
5. Optional fields: Optional[T] or field = None
6. Default values are supported directly in class definition
7. Type_Safe__Primitive for validated primitives (inherit from both Type_Safe__Primitive and base type)
8. No need for Field() from Pydantic, just use regular assignments
```

### Converting Between Type Systems

```
When working with OSBot-Fast-API type conversions:
1. Type_Safe classes are automatically converted to/from BaseModel at API boundaries
2. Conversion happens in Fast_API_Routes methods automatically
3. Manual conversion: type_safe__to__basemodel.convert_class(Type_Safe_Class)
4. Reverse: basemodel__to__type_safe.convert_instance(basemodel_instance)
5. Collections (List, Dict, Set) are automatically handled
6. Nested Type_Safe classes are recursively converted
7. Type_Safe__Primitive converts to its base type for Pydantic
8. Round-trip conversion maintains data integrity
```

## 🛡️ Middleware Configuration Prompts

### Setting Up Middleware

```
Configure OSBot-Fast-API middleware:
1. Enable built-in middleware via Fast_API constructor:
   - enable_cors=True for CORS support
   - enable_api_key=True for API key validation
2. For API key auth, set environment variables:
   - FAST_API__AUTH__API_KEY__NAME (header/cookie name)
   - FAST_API__AUTH__API_KEY__VALUE (secret value)
3. Middleware execution order: Detect_Disconnect → Http_Request → CORS → API_Key
4. Custom middleware: override setup_middlewares() in Fast_API subclass
5. Always call super().setup_middlewares() first in overrides
6. Access request.state for middleware-set values
```

### Custom Middleware Implementation

```
Add custom middleware to OSBot-Fast-API:
1. Subclass Fast_API and override setup_middlewares()
2. Use @self.app().middleware("http") decorator
3. Middleware signature: async def name(request: Request, call_next)
4. Pre-processing before await call_next(request)
5. Post-processing after response = await call_next(request)
6. Can modify request.state for passing data
7. Can modify response.headers for custom headers
8. Return response at the end
9. Call super().setup_middlewares() to add default middleware
```

## 📊 HTTP Events Prompts

### Event Tracking Configuration

```
Configure OSBot-Fast-API HTTP event tracking:
1. Access via fast_api.http_events
2. Set max_requests_logged (default 50) for buffer size
3. Enable clean_data=True to sanitize sensitive headers
4. Set trace_calls=True for execution tracing (debug only)
5. Events stored in circular buffer (deque)
6. Each event has unique event_id (Random_Guid)
7. Access in routes via request.state.request_data
8. Add callbacks: callback_on_request and callback_on_response
```

### Accessing Event Data

```
Access HTTP event data in OSBot-Fast-API:
1. In route handlers, use request.state for event data:
   - request.state.request_id: unique event ID
   - request.state.request_data: Full Fast_API__Http_Event object
   - request.state.http_events: Event manager reference
2. Event structure includes:
   - http_event_info: client info, timestamp, thread_id
   - http_event_request: method, path, headers, duration
   - http_event_response: status_code, content_type
   - http_event_traces: execution traces (if enabled)
3. Events automatically track duration with Decimal precision
```

## 🧪 Testing Prompts

### Writing Tests with Fast_API_Server

```
Test OSBot-Fast-API applications:
1. Use Fast_API_Server from osbot_fast_api.utils.Fast_API_Server
2. Context manager pattern: with Fast_API_Server(app=fast_api.app()) as server:
3. Use server.requests_get(path) for GET requests
4. Use server.requests_post(path, data=dict) for POST with Type_Safe objects
5. Server automatically allocates random port
6. Response has .json() and .status_code properties
7. Type_Safe objects passed as data are auto-converted
8. Test with headers: server.requests_get(path, headers={'X-API-Key': 'value'})
```

### Integration Testing

```
Write integration tests for OSBot-Fast-API:
1. Create Fast_API instance with desired configuration
2. Call fast_api.setup() before adding routes
3. Add routes with fast_api.add_routes(RouteClass)
4. Use Fast_API_Server context manager for test server
5. Test API key: include headers={'X-API-Key': 'test-key'}
6. Test Type_Safe conversion by passing dict data
7. Verify response.json() contains expected Type_Safe fields
8. Check response.status_code for expected HTTP status
9. Access response.headers for custom headers
```

## 🚀 AWS Lambda Prompts

### Lambda Handler Setup

```
Deploy OSBot-Fast-API to AWS Lambda:
1. Import Mangum: from mangum import Mangum
2. Create Fast_API instance and call setup()
3. Add all routes before creating handler
4. Get app: app = fast_api.app()
5. Create handler: handler = Mangum(app)
6. Lambda function: def lambda_handler(event, context): return handler(event, context)
7. For dependencies, check AWS_REGION environment variable
8. Use load_dependencies() for Lambda layers if needed
```

## 🔧 Advanced Features Prompts

### Route Path Generation

```
Understand OSBot-Fast-API route path generation:
1. Method name determines URL path
2. Underscores become hyphens: get_users → /get-users
3. Double underscore creates path parameters: get_user__id → /get-user/{id}
4. Multiple parameters: user__id_posts__post_id → /user/{id}/posts/{post_id}
5. Routes automatically prefixed with tag in lowercase
6. Tag 'Users' with method get_all → /users/get-all
7. Parse_function_name handles conversion automatically
```

### Static Files and Shell Server

```
Add static files and shell server to OSBot-Fast-API:
1. For static files, override path_static_folder() in Fast_API subclass
2. Return path to static directory
3. Files served at /static/* automatically
4. For shell server (dev only): fast_api.add_shell_server()
5. Adds /shell-server endpoint for remote commands
6. Shell server includes Python exec and bash commands
7. Requires authentication via auth_key
```

## 📋 Common Patterns

### Service with Full Features

```
Create a complete OSBot-Fast-API service with:
1. Type_Safe schemas for all data models
2. Fast_API_Routes classes for endpoint organization
3. Enable CORS for web clients
4. API key authentication for security
5. HTTP event tracking for monitoring
6. Custom middleware for request logging
7. Fast_API_Server for testing
8. Environment variables for configuration
9. Global exception handlers
10. Static file serving if needed
```

### Error Handling Pattern

```
Implement error handling in OSBot-Fast-API:
1. Global exception handlers added automatically
2. Return proper HTTP status codes
3. Use HTTPException from fastapi for custom errors
4. Type_Safe validation errors converted to 400 Bad Request
5. Middleware can return error responses directly
6. Event tracking captures all errors
7. Stack traces hidden in production (clean_data=True)
```

## 🎯 Best Practices Prompt

```
Follow OSBot-Fast-API best practices:
1. Always use Type_Safe classes, never raw Pydantic BaseModel
2. Organize routes in Fast_API_Routes classes by domain
3. Set meaningful tags for OpenAPI documentation
4. Enable middleware appropriate for environment
5. Use environment variables for all configuration
6. Test with Fast_API_Server, not TestClient directly
7. Monitor with HTTP events in production
8. Cache Type_Safe conversions (happens automatically)
9. Use consistent naming conventions for routes
10. Document Type_Safe schemas with docstrings
```

## ⚠️ Important Notes for LLMs

```
Critical OSBot-Fast-API implementation details:
1. NEVER use FastAPI() directly, always use Fast_API()
2. NEVER use BaseModel for schemas, always use Type_Safe
3. NEVER use @app.get(), use Fast_API_Routes methods
4. ALWAYS call setup() before adding routes
5. ALWAYS implement setup_routes() in route classes
6. ALWAYS use add_route_get/post/put/delete, not decorators
7. Type conversion is AUTOMATIC in route methods
8. Fast_API inherits from Type_Safe, not FastAPI
9. Route paths generated from method names automatically
10. Environment variables required for API key middleware
```