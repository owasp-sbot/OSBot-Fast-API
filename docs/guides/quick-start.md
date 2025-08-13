# Quick Start Guide

## 📋 Installation

```bash
pip install osbot-fast-api
```

## 🚀 Basic Application

### Minimal Example

```python
from osbot_fast_api.api.Fast_API import Fast_API

# Create and setup FastAPI application
fast_api = Fast_API()
fast_api.setup()

# Get the FastAPI app instance
app = fast_api.app()

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### With Routes

```python
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes

# Define routes class
class Routes_Users(Fast_API_Routes):
    tag = 'users'  # OpenAPI tag
    
    def list_users(self):
        return {'users': ['alice', 'bob', 'charlie']}
    
    def get_user__id(self, id: str):  # {id} parameter
        return {'user_id': id, 'name': f'User {id}'}
    
    def setup_routes(self):
        self.add_route_get(self.list_users)   # GET /users/list-users
        self.add_route_get(self.get_user__id) # GET /users/get-user/{id}

# Setup application
fast_api = Fast_API()
fast_api.setup()
fast_api.add_routes(Routes_Users)
app = fast_api.app()
```

## 🔐 Type-Safe Integration

### Define Type-Safe Schemas

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from typing import Optional

class User(Type_Safe):
    username: str
    email: str
    age: int
    is_active: bool = True
    bio: Optional[str] = None

class UserResponse(Type_Safe):
    id: str
    username: str
    created: bool
```

### Use in Routes

```python
from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes

class Routes_API(Fast_API_Routes):
    tag = 'api'
    
    def create_user(self, user: User) -> UserResponse:
        # Type-Safe object automatically converted from request
        print(f"Creating user: {user.username}")
        
        # Business logic here
        user_id = "user_123"
        
        # Return Type-Safe object (auto-converted to JSON)
        return UserResponse(
            id=user_id,
            username=user.username,
            created=True
        )
    
    def update_user__id(self, id: str, user: User):
        # Path parameter and body
        return {'updated': id, 'new_data': user.json()}
    
    def setup_routes(self):
        self.add_route_post(self.create_user)    # POST /api/create-user
        self.add_route_put(self.update_user__id) # PUT /api/update-user/{id}
```

## 🛡️ Middleware Configuration

### Enable Built-in Middleware

```python
from osbot_fast_api.api.Fast_API import Fast_API
import os

# Set environment variables for API key
os.environ['FAST_API__AUTH__API_KEY__NAME'] = 'X-API-Key'
os.environ['FAST_API__AUTH__API_KEY__VALUE'] = 'secret-key-123'

# Create app with middleware
fast_api = Fast_API(
    enable_cors=True,      # Enable CORS
    enable_api_key=True,   # Enable API key validation
    default_routes=True    # Add /status, /version routes
)
fast_api.setup()
```

### Custom Middleware

```python
from fastapi import Request

class Custom_Fast_API(Fast_API):
    def setup_middlewares(self):
        super().setup_middlewares()  # Add default middleware
        
        @self.app().middleware("http")
        async def add_custom_header(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Custom-Header"] = "CustomValue"
            return response
```

## 📊 HTTP Event Tracking

### Basic Event Tracking

```python
fast_api = Fast_API()
fast_api.http_events.max_requests_logged = 100  # Store last 100 requests
fast_api.http_events.clean_data = True          # Sanitize sensitive data
fast_api.setup()
```

### Custom Event Callbacks

```python
def on_request(http_event):
    print(f"Request: {http_event.http_event_request.path}")

def on_response(response, http_event):
    print(f"Response: {http_event.http_event_response.status_code}")

fast_api.http_events.callback_on_request = on_request
fast_api.http_events.callback_on_response = on_response
```

## 🧪 Testing

### Using Fast_API_Server

```python
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server

def test_api():
    fast_api = Fast_API()
    fast_api.setup()
    fast_api.add_routes(Routes_Users)
    
    with Fast_API_Server(app=fast_api.app()) as server:
        # Test GET request
        response = server.requests_get('/users/list-users')
        assert response.status_code == 200
        assert 'alice' in response.json()['users']
        
        # Test with path parameter
        response = server.requests_get('/users/get-user/123')
        assert response.json()['user_id'] == '123'
```

### Testing with Type-Safe

```python
def test_type_safe_conversion():
    fast_api = Fast_API()
    fast_api.setup()
    fast_api.add_routes(Routes_API)
    
    with Fast_API_Server(app=fast_api.app()) as server:
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25
        }
        
        response = server.requests_post('/api/create-user', data=user_data)
        assert response.status_code == 200
        assert response.json()['created'] == True
```

## 🚀 AWS Lambda Deployment

### Lambda Handler

```python
# lambda_handler.py
from osbot_fast_api.api.Fast_API import Fast_API
from mangum import Mangum

# Create application
fast_api = Fast_API()
fast_api.setup()
fast_api.add_routes(Routes_API)

# Create Lambda handler
app = fast_api.app()
handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)
```

### With Dependencies

```python
# For AWS Lambda with dependencies
import os

if os.getenv('AWS_REGION'):
    from osbot_aws.aws.lambda_.boto3__lambda import load_dependencies
    
    LAMBDA_DEPENDENCIES = ['osbot-fast-api==v0.9.1']
    load_dependencies(LAMBDA_DEPENDENCIES)

from osbot_fast_api.api.Fast_API import Fast_API

fast_api = Fast_API().setup()
handler = Mangum(fast_api.app())
```

## 🔧 Advanced Features

### Static Files

```python
class Fast_API_With_Static(Fast_API):
    def path_static_folder(self):
        return './static'  # Serve files from ./static directory

fast_api = Fast_API_With_Static()
fast_api.setup()
```

### Shell Server (Development)

```python
fast_api = Fast_API()
fast_api.add_shell_server()  # Adds /shell-server endpoint
fast_api.setup()
```

### Route Inspection

```python
# List all routes
routes = fast_api.routes()
for route in routes:
    print(f"{route['http_methods']} -> {route['http_path']}")

# Get route paths
paths = fast_api.routes_paths()
print(paths)  # ['/users/list-users', '/users/get-user/{id}']
```

## 📝 Complete Example

```python
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes
from osbot_utils.type_safe.Type_Safe import Type_Safe
from typing import List, Optional
import os

# Environment setup
os.environ['FAST_API__AUTH__API_KEY__NAME'] = 'X-API-Key'
os.environ['FAST_API__AUTH__API_KEY__VALUE'] = 'my-secret-key'

# Define schemas
class Product(Type_Safe):
    name: str
    price: float
    description: Optional[str] = None
    tags: List[str] = []

class Order(Type_Safe):
    product_id: str
    quantity: int
    customer_email: str

class OrderResponse(Type_Safe):
    order_id: str
    total: float
    status: str

# Define routes
class Routes_Shop(Fast_API_Routes):
    tag = 'shop'
    products = {}  # In-memory storage
    
    def create_product(self, product: Product):
        product_id = f"prod_{len(self.products)}"
        self.products[product_id] = product
        return {'id': product_id, 'created': True}
    
    def get_product__id(self, id: str):
        if id in self.products:
            return self.products[id].json()
        return {'error': 'Product not found'}
    
    def list_products(self):
        return {'products': [p.json() for p in self.products.values()]}
    
    def create_order(self, order: Order) -> OrderResponse:
        # Calculate total (simplified)
        product = self.products.get(order.product_id)
        if product:
            total = product.price * order.quantity
            return OrderResponse(
                order_id=f"order_{order.product_id}",
                total=total,
                status="confirmed"
            )
        return OrderResponse(
            order_id="",
            total=0.0,
            status="failed"
        )
    
    def setup_routes(self):
        self.add_route_post(self.create_product)
        self.add_route_get(self.get_product__id)
        self.add_route_get(self.list_products)
        self.add_route_post(self.create_order)

# Custom FastAPI with monitoring
class Shop_Fast_API(Fast_API):
    def setup_middlewares(self):
        super().setup_middlewares()
        
        @self.app().middleware("http")
        async def log_requests(request, call_next):
            print(f"Incoming: {request.method} {request.url.path}")
            response = await call_next(request)
            print(f"Outgoing: {response.status_code}")
            return response

# Create and configure application
fast_api = Shop_Fast_API(
    enable_cors=True,
    enable_api_key=True,
    default_routes=True
)

# Setup HTTP events
fast_api.http_events.max_requests_logged = 100
fast_api.http_events.clean_data = True

# Add callbacks
def on_request(event):
    print(f"Event ID: {event.event_id}")

fast_api.http_events.callback_on_request = on_request

# Setup and add routes
fast_api.setup()
fast_api.add_routes(Routes_Shop)

# Get FastAPI app
app = fast_api.app()

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🎯 Best Practices

1. **Type-Safe First**: Always use Type_Safe classes for request/response schemas
2. **Route Organization**: Group related endpoints in Fast_API_Routes classes
3. **Environment Variables**: Store sensitive configuration in environment
4. **Error Handling**: Use global exception handlers for consistent errors
5. **Testing**: Use Fast_API_Server for integration tests
6. **Monitoring**: Enable HTTP events for production monitoring
7. **Documentation**: Routes automatically appear in `/docs` (Swagger UI)

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Routes not appearing | Ensure `setup_routes()` is implemented and `add_routes()` is called |
| Type conversion fails | Check Type_Safe class has proper type hints |
| API key rejected | Verify environment variables are set correctly |
| CORS errors | Enable CORS with `enable_cors=True` |
| Lambda timeout | Increase timeout and check dependencies |

### Debug Mode

```python
# Enable trace calls for debugging
fast_api.http_events.trace_calls = True
fast_api.http_events.trace_call_config.max_depth = 10

# Access debug info in routes
@app.get("/debug")
def debug(request: Request):
    return {
        "event_id": str(request.state.request_id),
        "thread_id": request.state.request_data.http_event_info.thread_id
    }
```

## 📚 Next Steps

- [Type-Safe Integration Guide](../type-safe/type-safe-integration.md)
- [HTTP Events System](../features/http-events-system.md)
- [Middleware Stack](../features/middleware-stack.md)
- [LLM Prompts](./llm-prompts.md)
- [Testing Guide](./testing.md)