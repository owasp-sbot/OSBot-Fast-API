# OSBot-Fast-API - LLM Brief: Development Technical Debrief

## Overview

This document provides comprehensive guidance for developing applications with OSBot-Fast-API, including architecture details, component implementation, advanced features, and production deployment patterns.

## Architecture Overview

### System Architecture

```
OSBot-Fast-API Application
├── Fast_API (Core)
│   ├── Type_Safe Base
│   ├── Middleware Stack
│   ├── HTTP Events System
│   └── Route Management
├── Routes (Fast_API__Routes)
│   ├── Automatic Path Generation
│   ├── Type Conversion
│   └── OpenAPI Integration
├── Type Transformers
│   ├── Type_Safe ↔ BaseModel
│   ├── Type_Safe ↔ JSON Schema
│   └── Type_Safe ↔ OpenAPI
└── Utilities
    ├── Fast_API_Server (Testing)
    ├── Offline Documentation
    └── Shell Server (Dev)
```

### Component Interaction Flow

```python
# 1. Request arrives → Middleware Stack
# 2. Middleware processes → Route Handler
# 3. Type_Safe conversion → Business Logic
# 4. Response generation → Type conversion
# 5. Middleware post-processing → Client
```

## Core Components Development

### 1. Fast_API Class Implementation

**Purpose**: Main entry point that wraps FastAPI with enterprise features.

```python
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_utils.type_safe.Type_Safe import Type_Safe

class My_API(Fast_API):
    name           = "My API Service"
    version        = "1.0.0"
    enable_api_key = True
    enable_cors    = True
    docs_offline   = True
    
    def setup(self):
        """Setup order is critical for proper initialization"""
        self.add_global_exception_handlers()   # Error handling first
        self.setup_middlewares()                # Middleware chain
        self.setup_default_routes()             # /status, /config routes
        self.setup_static_routes()              # Static files
        self.setup_static_routes_docs()         # Offline docs
        self.setup_routes()                     # User routes last
        return self
    
    def setup_routes(self):
        """Add custom routes here"""
        self.add_routes(Routes__Users)
        self.add_routes(Routes__Products)
        return self
```

### 2. Route Development with Fast_API__Routes

**Key Concepts**:
- Each route class handles a specific domain
- Methods automatically become endpoints
- Type_Safe objects are automatically converted

```python
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe import Type_Safe
from typing import List, Optional

class Routes__Products(Fast_API__Routes):
    tag = 'products'  # Creates /products prefix
    
    def __init__(self):
        super().__init__()
        self.products_db = {}  # In-memory storage
    
    def list_products(self, 
                     category: Optional[str] = None,
                     limit: int = 10) -> List[Product]:
        """GET /products/list-products?category=x&limit=10"""
        products = self._filter_by_category(category)
        return products[:limit]
    
    def get_product__by__id(self, id: str) -> Product:
        """GET /products/get-product/by/{id}"""
        if id not in self.products_db:
            raise HTTPException(status_code=404, detail="Product not found")
        return self.products_db[id]
    
    def create_product(self, product: Product) -> ProductResponse:
        """POST /products/create-product"""
        product_id = Random_Guid()
        self.products_db[product_id] = product
        
        return ProductResponse(
            id=product_id,
            product=product,
            created=True
        )
    
    def update_product__id(self, id: str, product: Product) -> ProductResponse:
        """PUT /products/update-product/{id}"""
        if id not in self.products_db:
            raise HTTPException(status_code=404, detail="Product not found")
        
        self.products_db[id] = product
        return ProductResponse(
            id=id,
            product=product,
            updated=True
        )
    
    def delete_product__id(self, id: str) -> dict:
        """DELETE /products/delete-product/{id}"""
        if id in self.products_db:
            del self.products_db[id]
            return {"deleted": True, "id": id}
        return {"deleted": False, "id": id}
    
    def setup_routes(self):
        """Register all routes - REQUIRED method"""
        self.add_route_get(self.list_products)
        self.add_route_get(self.get_product__by__id)
        self.add_route_post(self.create_product)
        self.add_route_put(self.update_product__id)
        self.add_route_delete(self.delete_product__id)
        return self
```

### 3. Type-Safe Schema Development

**Design Principles**:
- Inherit from Type_Safe, not BaseModel
- Use Safe_* types for validation
- Support nested structures
- Automatic JSON serialization

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive
from typing import List, Optional, Dict

# Custom validated types
class Safe_Price(Type_Safe__Primitive, float):
    """Price that must be positive"""
    def __new__(cls, value):
        if value < 0:
            raise ValueError("Price cannot be negative")
        return float.__new__(cls, value)

# Domain models
class Product(Type_Safe):
    name        : Safe_Str
    description : Optional[Safe_Str] = None
    price       : Safe_Price
    category    : Safe_Str
    tags        : List[Safe_Str] = []
    metadata    : Dict[str, str] = {}
    in_stock    : bool = True

class ProductResponse(Type_Safe):
    id      : Random_Guid
    product : Product
    created : bool = False
    updated : bool = False

# Nested structures
class Order(Type_Safe):
    order_id     : Random_Guid
    customer     : Customer
    items        : List[OrderItem]
    total        : Safe_Price
    status       : Safe_Str
    
class OrderItem(Type_Safe):
    product_id : Random_Guid
    quantity   : Safe_Int
    unit_price : Safe_Price
    
    @property
    def total_price(self) -> float:
        return self.quantity * self.unit_price
```

### 4. Middleware Development

**Custom Middleware Pattern**:

```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

class Custom_Fast_API(Fast_API):
    
    def setup_middlewares(self):
        """Add custom middleware to the stack"""
        super().setup_middlewares()  # Always call parent first
        
        # Add timing middleware
        @self.app().middleware("http")
        async def add_timing_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time
            response.headers["X-Process-Time"] = str(duration)
            return response
        
        # Add custom logging middleware
        self.app().add_middleware(LoggingMiddleware)
        
        return self

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Pre-processing
        print(f"Incoming: {request.method} {request.url.path}")
        
        # Add request ID if not present
        if not hasattr(request.state, 'request_id'):
            request.state.request_id = Random_Guid()
        
        try:
            response = await call_next(request)
            print(f"Outgoing: {response.status_code}")
            return response
        except Exception as e:
            print(f"Error: {str(e)}")
            raise
```

### 5. HTTP Event System Implementation

**Event Tracking Configuration**:

```python
class Production_API(Fast_API):
    
    def setup(self):
        # Configure event tracking
        self.http_events.max_requests_logged = 100  # Circular buffer size
        self.http_events.clean_data = True          # Sanitize sensitive data
        self.http_events.trace_calls = False        # Disable in production
        
        # Add event callbacks
        self.http_events.callback_on_request = self.on_request_received
        self.http_events.callback_on_response = self.on_response_sent
        
        super().setup()
        return self
    
    def on_request_received(self, http_event):
        """Process incoming request events"""
        # Log to monitoring system
        logger.info(f"Request: {http_event.http_event_request.path}")
        
        # Track metrics
        metrics.increment('api.requests', tags=[
            f"method:{http_event.http_event_request.method}",
            f"path:{http_event.http_event_request.path}"
        ])
    
    def on_response_sent(self, response, http_event):
        """Process outgoing response events"""
        duration = http_event.http_event_request.duration
        status = http_event.http_event_response.status_code
        
        # Performance monitoring
        if duration > Decimal('1.0'):  # Log slow requests
            logger.warning(f"Slow request: {http_event.http_event_request.path} took {duration}s")
        
        # Track response metrics
        metrics.histogram('api.response_time', duration, tags=[
            f"status:{status}",
            f"path:{http_event.http_event_request.path}"
        ])
```

### 6. Type Transformation System

**Implementing Custom Transformers**:

```python
from osbot_fast_api.api.transformers.Type_Safe__To__BaseModel import Type_Safe__To__BaseModel

class Custom_Transformer(Type_Safe__To__BaseModel):
    
    def convert_field_type(self, field_type: Any) -> Any:
        """Custom field type conversion logic"""
        # Handle custom types
        if field_type == MyCustomType:
            return str  # Convert to string for API
        
        # Handle special collections
        origin = get_origin(field_type)
        if origin is frozenset:
            args = get_args(field_type)
            if args:
                inner_type = self.convert_type(args[0])
                return List[inner_type]  # Convert frozenset to list
        
        # Fall back to parent implementation
        return super().convert_field_type(field_type)

# Use custom transformer
transformer = Custom_Transformer()
BaseModelClass = transformer.convert_class(MyTypeSafeClass)
```

## Advanced Features

### 1. Offline Documentation Setup

```python
class API_With_Offline_Docs(Fast_API):
    docs_offline = True  # Enable offline documentation
    
    def setup_static_routes_docs(self):
        """Serve documentation assets locally"""
        super().setup_static_routes_docs()
        
        # Add custom documentation
        @self.app().get("/docs/custom", include_in_schema=False)
        async def custom_docs():
            return HTMLResponse("""
                <html>
                    <head><title>Custom API Docs</title></head>
                    <body>
                        <h1>Custom Documentation</h1>
                        <iframe src="/docs" width="100%" height="800px"></iframe>
                    </body>
                </html>
            """)
```

### 2. HTTP Shell Server (Development Only)

```python
from osbot_fast_api.api.Fast_API import Fast_API
import os

# Set shell authentication
os.environ['HTTP_SHELL__AUTH_KEY'] = 'dev-secret-guid'

class Dev_API(Fast_API):
    
    def setup_routes(self):
        if self.is_development():
            self.add_shell_server()  # Adds /shell-server endpoint
        super().setup_routes()
    
    def is_development(self):
        return os.getenv('ENVIRONMENT', 'dev') == 'dev'

# Access shell at: http://localhost:8000/shell-server?auth_key=dev-secret-guid
```

### 3. Dynamic Route Generation

```python
class Routes__Dynamic(Fast_API__Routes):
    tag = 'dynamic'
    
    def setup_routes(self):
        """Dynamically generate routes from configuration"""
        
        # Load route configuration
        route_config = self.load_route_config()
        
        for route in route_config:
            # Create dynamic handler
            handler = self.create_handler(route)
            
            # Add route based on method
            if route['method'] == 'GET':
                self.add_route_get(handler, path=route['path'])
            elif route['method'] == 'POST':
                self.add_route_post(handler, path=route['path'])
    
    def create_handler(self, route_config):
        """Create a dynamic route handler"""
        def handler(**kwargs):
            # Process based on configuration
            return self.process_dynamic_route(route_config, kwargs)
        
        # Set function name for path generation
        handler.__name__ = route_config['name']
        return handler
```

### 4. Client Generation from OpenAPI

```python
from osbot_fast_api.api.Fast_API__Python_Client import Fast_API__Python_Client

# Generate Python client from API
fast_api = My_API().setup()
client_generator = Fast_API__Python_Client(fast_api=fast_api)

# Generate client code
client_code = client_generator.generate()

# Save to file
with open('api_client.py', 'w') as f:
    f.write(client_code)

# Use generated client
from api_client import APIClient
client = APIClient(base_url="http://localhost:8000")
response = client.users.list_users()
```

## Production Deployment

### 1. Production Configuration

```python
class Production_API(Fast_API):
    name           = "Production Service"
    enable_api_key = True
    enable_cors    = True
    docs_offline   = True
    
    def __init__(self):
        super().__init__()
        self.configure_for_production()
    
    def configure_for_production(self):
        """Production-specific configuration"""
        # Disable debug features
        self.http_events.trace_calls = False
        self.http_events.clean_data = True
        
        # Set production limits
        self.http_events.max_requests_logged = 1000
        
        # Configure CORS for specific origins
        self.cors_origins = [
            "https://app.example.com",
            "https://admin.example.com"
        ]
    
    def setup_middlewares(self):
        super().setup_middlewares()
        
        # Add rate limiting
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        
        limiter = Limiter(key_func=get_remote_address)
        self.app().state.limiter = limiter
        self.app().add_exception_handler(429, _rate_limit_exceeded_handler)
        
        # Add security headers
        @self.app().middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            return response
```

### 2. Running with Uvicorn

```python
# server.py
from osbot_fast_api.api.Fast_API import Fast_API
import uvicorn
import os

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Create application
app_instance = Production_API().setup()
app = app_instance.app()

if __name__ == "__main__":
    # Production configuration
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=int(os.getenv("WORKERS", 4)),
        log_level=os.getenv("LOG_LEVEL", "info"),
        access_log=True,
        use_colors=False,
        reload=False
    )
```

### 3. Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment
ENV FAST_API__AUTH__API_KEY__NAME=X-API-Key
ENV FAST_API__AUTH__API_KEY__VALUE=${API_KEY}

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. AWS Lambda Deployment

```python
# lambda_function.py
import os

# Load Lambda layers if needed
if os.getenv('AWS_REGION'):
    from osbot_aws.aws.lambda_.boto3__lambda import load_dependencies
    load_dependencies(['osbot-fast-api'])

from osbot_fast_api.api.Fast_API import Fast_API
from mangum import Mangum

class Lambda_API(Fast_API):
    name = "Lambda API Service"
    enable_api_key = True
    
    def setup(self):
        # Lambda-specific configuration
        self.http_events.max_requests_logged = 10  # Limited memory
        super().setup()
        return self

# Create handler
fast_api = Lambda_API().setup()
fast_api.add_routes(Routes__API)
app = fast_api.app()
handler = Mangum(app)

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    return handler(event, context)
```

## CLI Development Interface

```python
from osbot_fast_api.cli.Fast_API__CLI import Fast_API__CLI
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server

class My_API_CLI(Fast_API__CLI):
    """Interactive CLI for API development"""
    
    def __init__(self):
        super().__init__()
        self.fast_api = My_API().setup()
        self.fast_api_server = None
    
    def on_repl_start(self):
        """Initialize when REPL starts"""
        # Start server
        self.fast_api_server = Fast_API_Server(app=self.fast_api.app())
        self.fast_api_server.start()
        
        print(f"🚀 API running at: {self.fast_api_server.url()}")
        print(f"📚 Docs at: {self.fast_api_server.url()}/docs")
        print(f"🔍 Available commands: help, routes, test, reload")
    
    def routes(self):
        """List all registered routes"""
        for route in self.fast_api.routes():
            print(f"{route['http_methods']} -> {route['http_path']}")
    
    def test(self, endpoint: str = "/config/status"):
        """Test an endpoint"""
        response = self.fast_api_server.requests_get(endpoint)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    def reload(self):
        """Reload the API"""
        self.fast_api_server.stop()
        self.fast_api = My_API().setup()
        self.fast_api_server = Fast_API_Server(app=self.fast_api.app())
        self.fast_api_server.start()
        print("✅ API reloaded")

# Run CLI
if __name__ == "__main__":
    cli = My_API_CLI().setup()
    cli.run()
```

## Performance Optimization

### 1. Caching Strategy

```python
from osbot_utils.decorators.cache.cache_on_self import cache_on_self

class Optimized_Routes(Fast_API__Routes):
    
    @cache_on_self
    def expensive_computation(self, input_data: str):
        """Cached expensive operation"""
        # This will only compute once per instance
        return self._process_data(input_data)
    
    def get_cached_data(self, key: str):
        """Use instance-level caching"""
        if not hasattr(self, '_cache'):
            self._cache = {}
        
        if key not in self._cache:
            self._cache[key] = self.expensive_computation(key)
        
        return self._cache[key]
```

### 2. Database Connection Pooling

```python
from contextlib import asynccontextmanager

class API_With_DB(Fast_API):
    
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Manage application lifecycle"""
        # Startup
        self.db_pool = await create_db_pool()
        yield
        # Shutdown
        await self.db_pool.close()
    
    def app_kwargs(self, **kwargs):
        """Add lifespan to FastAPI kwargs"""
        app_kwargs = super().app_kwargs(**kwargs)
        app_kwargs['lifespan'] = self.lifespan
        return app_kwargs
```

## Error Handling Patterns

### Global Exception Handling

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import traceback

class API_With_Error_Handling(Fast_API):
    
    def add_global_exception_handlers(self):
        """Configure comprehensive error handling"""
        
        @self.app().exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "status_code": exc.status_code,
                    "path": request.url.path
                }
            )
        
        @self.app().exception_handler(ValueError)
        async def value_error_handler(request: Request, exc: ValueError):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid value",
                    "detail": str(exc),
                    "path": request.url.path
                }
            )
        
        @self.app().exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            # Log full traceback
            logger.error(f"Unhandled exception: {traceback.format_exc()}")
            
            # Return safe error response
            if self.is_development():
                content = {
                    "error": "Internal server error",
                    "detail": str(exc),
                    "traceback": traceback.format_exc()
                }
            else:
                content = {
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred"
                }
            
            return JSONResponse(status_code=500, content=content)
```

## Security Best Practices

### 1. API Key Rotation

```python
import hashlib
import time

class Secure_API(Fast_API):
    
    def validate_api_key(self, api_key: str) -> bool:
        """Enhanced API key validation with rotation"""
        
        # Check static key
        if super().validate_api_key(api_key):
            return True
        
        # Check rotating keys (time-based)
        current_hour = int(time.time() / 3600)
        for offset in range(-1, 2):  # Previous, current, next hour
            time_key = self.generate_time_key(current_hour + offset)
            if api_key == time_key:
                return True
        
        return False
    
    def generate_time_key(self, hour: int) -> str:
        """Generate time-based API key"""
        secret = os.getenv('API_KEY_SECRET')
        data = f"{secret}:{hour}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
```

### 2. Input Validation

```python
from osbot_utils.type_safe.Type_Safe__Validator import Type_Safe__Validator

class Safe_Input(Type_Safe):
    """Input with comprehensive validation"""
    
    email : Safe_Str__Email
    age   : Safe_Int
    
    def __post_init__(self):
        """Additional validation after initialization"""
        if self.age < 0 or self.age > 150:
            raise ValueError(f"Invalid age: {self.age}")
        
        # Sanitize inputs
        self.email = self.email.lower().strip()
```

## Development Workflow

### 1. Local Development Setup

```bash
# Install dependencies
pip install osbot-fast-api[dev]

# Set environment variables
export FAST_API__AUTH__API_KEY__NAME="X-API-Key"
export FAST_API__AUTH__API_KEY__VALUE="dev-key"
export ENVIRONMENT="development"

# Run with auto-reload
uvicorn server:app --reload --log-level debug
```

### 2. Development Tools Integration

```python
# Development configuration
class Dev_Config:
    # Enable all debugging features
    TRACE_CALLS = True
    MAX_REQUESTS_LOGGED = 1000
    CLEAN_DATA = False  # Show full data in dev
    
    # Development middleware
    ENABLE_PROFILING = True
    ENABLE_SQL_LOGGING = True
    
    # Testing endpoints
    ENABLE_SHELL_SERVER = True
    ENABLE_DEBUG_ROUTES = True

# Apply configuration
def setup_dev_environment(api: Fast_API):
    if os.getenv('ENVIRONMENT') == 'development':
        api.http_events.trace_calls = Dev_Config.TRACE_CALLS
        api.http_events.max_requests_logged = Dev_Config.MAX_REQUESTS_LOGGED
        api.http_events.clean_data = Dev_Config.CLEAN_DATA
        
        if Dev_Config.ENABLE_SHELL_SERVER:
            api.add_shell_server()
```

## Summary

This technical debrief provides comprehensive guidance for developing with OSBot-Fast-API, covering:

1. **Architecture**: Understanding component interactions and data flow
2. **Core Components**: Implementing Fast_API, Routes, and Type-Safe models
3. **Advanced Features**: HTTP events, offline docs, shell server
4. **Production Deployment**: Configuration, Docker, Lambda
5. **Performance**: Caching, pooling, optimization strategies
6. **Security**: API key management, input validation
7. **Error Handling**: Global exception handlers, logging
8. **Development Workflow**: CLI tools, debugging, testing

The framework's consistent patterns, type safety, and comprehensive feature set enable rapid development of production-ready APIs while maintaining code quality and maintainability.