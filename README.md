# OSBot-Fast-API

![Current Release](https://img.shields.io/badge/release-v0.37.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-red)
![Type-Safe](https://img.shields.io/badge/Type--Safe-✓-brightgreen)
![AWS Lambda](https://img.shields.io/badge/AWS_Lambda-Ready-orange)

A Type-Safe wrapper around FastAPI that provides strong typing, comprehensive middleware support, HTTP event tracking, and seamless AWS Lambda integration through Mangum.

## ✨ Key Features

- **🔐 Type-Safe First**: Automatic bidirectional conversion between Type_Safe classes and Pydantic BaseModels
- **🛡️ Built-in Middleware**: API key validation, CORS, disconnect detection, and HTTP event tracking
- **📊 HTTP Event System**: Comprehensive request/response tracking with configurable storage
- **🚀 AWS Lambda Ready**: Direct integration with Mangum for serverless deployment
- **🧪 Testing Utilities**: Built-in test server with Type-Safe support
- **🔄 Auto-conversion**: Seamless Type_Safe ↔ BaseModel ↔ Dataclass conversions
- **📝 Route Organization**: Clean route structure with automatic path generation

## 📦 Installation

```bash
pip install osbot-fast-api
```

## 🚀 Quick Start

### Basic Application

```python
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe import Type_Safe


# Define Type-Safe schema
class User(Type_Safe):
    username: str
    email: str
    age: int


# Create routes
class Routes_Users(Fast_API__Routes):
    tag = 'users'

    def create_user(self, user: User):
        # user is automatically converted from BaseModel to Type_Safe
        return {'created': user.username}

    def get_user__id(self, id: str):  # Becomes /users/get-user/{id}
        return {'user_id': id}

    def setup_routes(self):
        self.add_route_post(self.create_user)
        self.add_route_get(self.get_user__id)


# Setup application
fast_api = Fast_API(enable_cors=True)
fast_api.setup()
fast_api.add_routes(Routes_Users)

# Get FastAPI app instance
app = fast_api.app()
```

### With Middleware & Authentication

```python
import os

# Configure API key authentication
os.environ['FAST_API__AUTH__API_KEY__NAME'] = 'X-API-Key'
os.environ['FAST_API__AUTH__API_KEY__VALUE'] = 'your-secret-key'

# Create app with middleware
fast_api = Fast_API(
    enable_cors=True,      # Enable CORS support
    enable_api_key=True,   # Enable API key validation
    default_routes=True    # Add /status, /version routes
)

# Configure HTTP event tracking
fast_api.http_events.max_requests_logged = 100
fast_api.http_events.clean_data = True  # Sanitize sensitive headers

fast_api.setup()
```

## 🏗️ Architecture

OSBot-Fast-API extends FastAPI with a comprehensive Type-Safe layer and monitoring capabilities:

```
┌─────────────────────────────────────────────────────┐
│                   Your Application                  │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐   │
│  │ Type-Safe    │  │   Routes     │  │  Events  │   │
│  │  Schemas     │  │   Classes    │  │ Handlers │   │
│  └──────────────┘  └──────────────┘  └──────────┘   │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                  OSBot-Fast-API                     │
│                                                     │
│  ┌────────────────────────────────────────────┐     │
│  │          Type Conversion System            │     │
│  │   Type_Safe ↔ BaseModel ↔ Dataclass        │     │
│  └────────────────────────────────────────────┘     │
│                                                     │
│  ┌────────────────────────────────────────────┐     │
│  │           Middleware Pipeline              │     │
│  │  Disconnect → Events → CORS → API Key      │     │
│  └────────────────────────────────────────────┘     │
│                                                     │
│  ┌────────────────────────────────────────────┐     │
│  │         HTTP Event Tracking System         │     │
│  │   Request/Response/Traces/Monitoring       │     │
│  └────────────────────────────────────────────┘     │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                     FastAPI                         │
└─────────────────────────────────────────────────────┘
```

## 🔐 Type-Safe Integration

OSBot-Fast-API automatically converts between Type_Safe classes and Pydantic BaseModels:

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from typing import List, Optional

# Define Type-Safe schemas (not Pydantic!)
class Address(Type_Safe):
    street: str
    city: str
    country: str

class Person(Type_Safe):
    name: str
    age: int
    email: Optional[str] = None
    addresses: List[Address] = []

# Use directly in routes - automatic conversion happens
class Routes_People(Fast_API__Routes):
    tag = 'people'
    
    def create_person(self, person: Person):
        # person is Type_Safe instance, not BaseModel
        # Full type validation and conversion handled automatically
        return person  # Automatically converted back to JSON
    
    def setup_routes(self):
        self.add_route_post(self.create_person)
```

## 📊 HTTP Event Tracking

Built-in comprehensive request/response tracking:

```python
# Configure event tracking
fast_api.http_events.max_requests_logged = 100
fast_api.http_events.clean_data = True  # Sanitize sensitive data
fast_api.http_events.trace_calls = True  # Enable execution tracing (debug)

# Add event callbacks
def on_request(event):
    print(f"Request: {event.http_event_request.path}")

def on_response(response, event):
    print(f"Response: {event.http_event_response.status_code}")
    print(f"Duration: {event.http_event_request.duration}s")

fast_api.http_events.callback_on_request = on_request
fast_api.http_events.callback_on_response = on_response
```

## 🛡️ Middleware Stack

Built-in middleware pipeline (in execution order):

1. **Detect_Disconnect**: Monitor client disconnections
2. **Http_Request**: Event tracking and logging
3. **CORS**: Cross-origin resource sharing
4. **API_Key_Check**: Header/cookie API key validation

### Custom Middleware

```python
class Custom_Fast_API(Fast_API):
    def setup_middlewares(self):
        super().setup_middlewares()  # Add default middleware
        
        @self.app().middleware("http")
        async def add_process_time(request: Request, call_next):
            import time
            start = time.time()
            response = await call_next(request)
            response.headers["X-Process-Time"] = str(time.time() - start)
            return response
```

## 🧪 Testing

Built-in test server with Type-Safe support:

```python
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server

def test_api():
    fast_api = Fast_API()
    fast_api.setup()
    fast_api.add_routes(Routes_Users)
    
    with Fast_API_Server(app=fast_api.app()) as server:
        # Test with Type-Safe object
        user_data = {'username': 'alice', 'email': 'alice@example.com', 'age': 30}
        response = server.requests_post('/users/create-user', data=user_data)
        
        assert response.status_code == 200
        assert response.json()['created'] == 'alice'
```

## 🚀 AWS Lambda Deployment

```python
from mangum import Mangum
from osbot_fast_api.api.Fast_API import Fast_API

# Create and setup application
fast_api = Fast_API()
fast_api.setup()
fast_api.add_routes(Routes_Users)

# Create Lambda handler
app = fast_api.app()
handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)
```

## 📁 Project Structure

```
osbot_fast_api/
├── api/
│   ├── Fast_API.py                 # Main FastAPI wrapper
│   ├── Fast_API__Routes.py          # Route organization base class
│   ├── Fast_API__Http_Event*.py    # Event tracking components
│   └── middlewares/                # Built-in middleware
├── utils/
│   ├── type_safe/                  # Type conversion system
│   │   ├── Type_Safe__To__BaseModel.py
│   │   ├── BaseModel__To__Type_Safe.py
│   │   └── ...
│   ├── Fast_API_Server.py          # Test server
│   └── Fast_API_Utils.py           # Utilities
└── examples/                        # Usage examples
```

## 📚 Documentation

Comprehensive documentation is available in the [`/docs`](./docs) folder:

- [📖 Main Documentation](./docs/README.md)
- [🏗️ Architecture Overview](./docs/architecture/osbot-fast-api-architecture.md)
- [🔐 Type-Safe Integration](./docs/type-safe/type-safe-integration.md)
- [📊 HTTP Events System](./docs/features/http-events-system.md)
- [🛡️ Middleware Stack](./docs/features/middleware-stack.md)
- [🚀 Quick Start Guide](./docs/guides/quick-start.md)
- [🤖 LLM Prompts](./docs/guides/llm-prompts.md)
- [🧪 Testing Guide](./docs/guides/testing.md)

## 🎯 Key Benefits

### For Developers
- **Type Safety**: Catch errors at development time with Type_Safe validation
- **Less Boilerplate**: Convention over configuration approach
- **Auto-conversion**: Seamless type conversions at API boundaries
- **Built-in Testing**: Integrated test server and utilities

### For Production
- **Monitoring**: Comprehensive HTTP event tracking
- **Security**: Built-in API key validation and header sanitization
- **Performance**: Cached type conversions and efficient middleware
- **AWS Ready**: Direct Lambda integration with Mangum

### For Teams
- **Organized Code**: Clear separation with Fast_API__Routes classes
- **Consistent Patterns**: Standardized route naming and structure
- **Easy Testing**: Type-Safe test utilities
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## 🔧 Advanced Features

### Route Path Generation
- `get_users()` → `/get-users`
- `get_user__id()` → `/get-user/{id}`
- `user__id_posts__post_id()` → `/user/{id}/posts/{post_id}`

### Type-Safe Primitives
```python
from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive

class Email(Type_Safe__Primitive, str):
    def __new__(cls, value):
        if '@' not in value:
            raise ValueError("Invalid email")
        return super().__new__(cls, value)
```

### Event Access in Routes
```python
from fastapi import Request

def get_request_info(self, request: Request):
    return {
        'event_id': str(request.state.request_id),
        'thread_id': request.state.request_data.http_event_info.thread_id
    }
```

## 🤝 Contributing

Contributions are welcome! Please check the [documentation](./docs) for architecture details and patterns.

## 📄 License

This project is licensed under the Apache 2.0 License.

## 🔗 Related Projects

- [OSBot-Utils](https://github.com/owasp-sbot/OSBot-Utils) - Core Type-Safe implementation
- [OSBot-AWS](https://github.com/owasp-sbot/OSBot-AWS) - AWS utilities
- [OSBot-Fast-API-Serverless](https://github.com/owasp-sbot/OSBot-Fast-API-Serverless) - Serverless extensions

## 💡 Examples

For more examples, see:
- [Basic FastAPI application](./docs/guides/quick-start.md)
- [Type-Safe schemas](./docs/type-safe/type-safe-integration.md)
- [Testing patterns](./docs/guides/testing.md)
- [Real-world usage in MGraph-AI](./docs/type-safe/type-safe-integration.md#real-world-example-mgraph-ai-service)

---

**Built with ❤️ using Type-Safe principles for robust, maintainable APIs**