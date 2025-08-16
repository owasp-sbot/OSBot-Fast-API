# New Project Testing Template for OSBot-Fast-API

## 🚀 Quick Start Testing Setup

This template follows the OSBot testing patterns using `TestCase` and singleton test objects for efficient testing without fixtures.

## 📁 Project Test Structure

Create this directory structure for your new project:

```
your-project/
├── src/
│   └── your_api/
│       ├── __init__.py
│       ├── fast_api/
│       │   ├── Service__Fast_API.py      # Your main Fast_API service
│       │   ├── routes/                   # Route classes
│       │   └── lambda_handler.py         # Lambda handler if needed
│       └── service/                       # Business logic
├── tests/
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── Service__Fast_API__Test_Objs.py  # Singleton test objects
│   │   ├── fast_api/
│   │   │   ├── routes/
│   │   │   │   ├── test_Routes__YourDomain.py         # Direct route testing
│   │   │   │   └── test_Routes__YourDomain__client.py # Client-based testing
│   │   │   ├── test_Service__Fast_API.py
│   │   │   ├── test_Service__Fast_API__client.py
│   │   │   └── test_Service__Fast_API__http.py        # When real HTTP needed
│   │   └── service/
│   │       └── test_YourService.py       # Business logic tests
│   └── integration/
│       └── test_lambda_handler.py        # Lambda integration tests
```

## 🎯 Core Testing Pattern: Singleton Test Objects

### 1. `Service__Fast_API__Test_Objs.py` - The Foundation

This is the most important file - it creates singleton instances to avoid repeated initialization:

```python
"""
Singleton test objects for efficient test execution
Avoids recreating Fast_API instances for each test
"""
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.utils.Env import set_env
from starlette.testclient import TestClient
from fastapi import FastAPI

# Import your service
from your_api.fast_api.Service__Fast_API import Service__Fast_API

# Test environment configuration
TEST_API_KEY__NAME = 'X-API-Key'
TEST_API_KEY__VALUE = 'test-api-key-12345'

class Service__Fast_API__Test_Objs(Type_Safe):
    """Singleton container for test objects"""
    fast_api        : Service__Fast_API = None
    fast_api__app   : FastAPI           = None
    fast_api__client: TestClient        = None
    setup_completed : bool              = False
    
    # Add any other shared test resources here
    # local_stack    : Local_Stack       = None  # If using LocalStack
    # test_data      : dict              = None  # Shared test data

# Global singleton instance
service_fast_api_test_objs = Service__Fast_API__Test_Objs()

def setup__service_fast_api_test_objs():
    """
    Setup function that ensures single initialization
    This is called by all test classes in setUpClass
    """
    with service_fast_api_test_objs as _:
        if _.setup_completed is False:
            # Set up environment variables
            set_env('FAST_API__AUTH__API_KEY__NAME', TEST_API_KEY__NAME)
            set_env('FAST_API__AUTH__API_KEY__VALUE', TEST_API_KEY__VALUE)
            
            # Create Fast_API instance once
            _.fast_api = Service__Fast_API().setup()
            _.fast_api__app = _.fast_api.app()
            _.fast_api__client = _.fast_api.client()
            
            # Add any other one-time setup here
            # _.local_stack = setup_local_stack()  # If using LocalStack
            
            _.setup_completed = True
    
    return service_fast_api_test_objs

# Optional: Helper for tests that need LocalStack
def setup_local_stack():
    """Setup LocalStack for AWS service mocking"""
    from osbot_aws.testing.Temp__Random__AWS_Credentials import Temp_AWS_Credentials
    from osbot_local_stack.local_stack.Local_Stack import Local_Stack
    
    Temp_AWS_Credentials().with_localstack_credentials()
    local_stack = Local_Stack().activate()
    return local_stack
```

## 📝 Test Class Templates

### 2. Direct Route Testing (Without Client)

```python
"""
test_Routes__YourDomain.py
Direct testing of route methods without HTTP layer
"""
from unittest import TestCase
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.utils.Objects import base_classes

from your_api.fast_api.routes.Routes__YourDomain import Routes__YourDomain


class test_Routes__YourDomain(TestCase):
    """Direct route testing - no HTTP overhead"""

    @classmethod
    def setUpClass(cls):
        """Initialize route instance"""
        cls.routes = Routes__YourDomain()

    def test_setUpClass(self):
        """Verify route setup"""
        with self.routes as _:
            assert type(_) == Routes__YourDomain
            assert base_classes(_) == [Fast_API__Routes, Type_Safe, object]

    def test_direct_method_call(self):
        """Test route method directly"""
        with self.routes as _:
            # Direct method call - no HTTP, no client
            result = _.get_items()
            assert type(result) is dict
            assert 'items' in result

            # Test with parameters
            item = _.get_item__id(item_id='123')
            assert item.get('id') == '123'

    def test_business_logic(self):
        """Test complex business logic without HTTP overhead"""
        with self.routes as _:
            # Test data processing
            input_data = {'name': 'test', 'value': 42}
            processed = _.process_data(data=input_data)
            assert processed.get('status') == 'processed'
            assert processed.get('original_value') == 42
```

### 3. Client-Based Route Testing

```python
"""
test_Routes__YourDomain__client.py
Testing routes through FastAPI TestClient
"""
from unittest import TestCase
from tests.unit.Service__Fast_API__Test_Objs import (
    setup__service_fast_api_test_objs,
    TEST_API_KEY__NAME,
    TEST_API_KEY__VALUE
)

class test_Routes__YourDomain__client(TestCase):
    """Test routes through HTTP client"""
    
    @classmethod
    def setUpClass(cls):
        """Setup singleton test objects"""
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            # Add auth header for all requests
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE
    
    def test_get_endpoint(self):
        """Test GET endpoint"""
        response = self.client.get('/your-domain/items')
        assert response.status_code == 200
        assert 'items' in response.json()
    
    def test_post_endpoint(self):
        """Test POST endpoint with Type_Safe data"""
        test_data = {
            'name': 'Test Item',
            'description': 'Test Description',
            'price': 99.99
        }
        
        response = self.client.post('/your-domain/create-item', json=test_data)
        assert response.status_code == 201
        result = response.json()
        assert result.get('created') is True
        assert result.get('item_id') is not None
    
    def test_path_parameters(self):
        """Test endpoint with path parameters"""
        item_id = 'test-123'
        response = self.client.get(f'/your-domain/item/{item_id}')
        assert response.status_code == 200
        assert response.json().get('id') == item_id
    
    def test_error_handling(self):
        """Test error responses"""
        # Test 404
        response = self.client.get('/your-domain/item/nonexistent')
        assert response.status_code == 404
        
        # Test validation error
        invalid_data = {'name': 123}  # Should be string
        response = self.client.post('/your-domain/create-item', json=invalid_data)
        assert response.status_code == 422
```

### 4. Service-Level Testing

```python
"""
test_Service__Fast_API__client.py
Test the complete Fast_API service configuration
"""
from unittest import TestCase
from fastapi import FastAPI
from starlette.testclient import TestClient
from osbot_utils.utils.Env import get_env

from your_api.fast_api.Service__Fast_API import Service__Fast_API
from your_api.utils.Version import version__your_api
from tests.unit.Service__Fast_API__Test_Objs import (
    setup__service_fast_api_test_objs,
    Service__Fast_API__Test_Objs,
    TEST_API_KEY__NAME,
    TEST_API_KEY__VALUE
)

class test_Service__Fast_API__client(TestCase):
    """Test service-level functionality"""
    
    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.service_test_objs = _
            cls.fast_api = _.fast_api
            cls.client = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE
    
    def test__init__(self):
        """Verify service initialization"""
        with self.service_test_objs as _:
            assert type(_) is Service__Fast_API__Test_Objs
            assert type(_.fast_api) is Service__Fast_API
            assert type(_.fast_api__app) is FastAPI
            assert type(_.fast_api__client) is TestClient
    
    def test_authentication(self):
        """Test API key authentication"""
        path = '/info/version'
        
        # Without auth
        response_no_auth = self.client.get(path, headers={})
        assert response_no_auth.status_code == 401
        assert 'Client API key is missing' in response_no_auth.json()['message']
        
        # With auth
        headers = {TEST_API_KEY__NAME: TEST_API_KEY__VALUE}
        response_with_auth = self.client.get(path, headers=headers)
        assert response_with_auth.status_code == 200
        assert response_with_auth.json() == {'version': version__your_api}
    
    def test_routes_configuration(self):
        """Test all routes are properly configured"""
        expected_routes = [
            '/info/version',
            '/info/status',
            '/your-domain/items',
            '/your-domain/create-item',
            # Add all your expected routes
        ]
        
        actual_routes = self.fast_api.routes_paths()
        for route in expected_routes:
            assert route in actual_routes, f"Missing route: {route}"
```

### 5. HTTP Server Testing (When Real HTTP is Needed)

```python
"""
test_Service__Fast_API__http.py
Use Fast_API_Server only when you need real HTTP connections
"""
from unittest import TestCase
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server
from tests.unit.Service__Fast_API__Test_Objs import (
    setup__service_fast_api_test_objs,
    TEST_API_KEY__NAME,
    TEST_API_KEY__VALUE
)

class test_Service__Fast_API__http(TestCase):
    """Test with real HTTP server - only when necessary"""
    
    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.app = _.fast_api__app
            cls.fast_api_server = Fast_API_Server(app=cls.app)
    
    def test_real_http_connection(self):
        """Test with actual HTTP server"""
        headers = {TEST_API_KEY__NAME: TEST_API_KEY__VALUE}
        
        with self.fast_api_server as server:
            # Real HTTP requests
            response = server.requests_get('/info/version', headers=headers)
            assert response.status_code == 200
            
            # Test server URL
            assert server.url() == f'http://127.0.0.1:{server.port}/'
            
            # Test streaming response if needed
            response = server.requests_get('/stream', stream=True, headers=headers)
            for chunk in response.iter_content():
                assert chunk is not None
    
    def test_concurrent_requests(self):
        """Test concurrent HTTP requests"""
        import concurrent.futures
        
        headers = {TEST_API_KEY__NAME: TEST_API_KEY__VALUE}
        
        def make_request(i):
            with self.fast_api_server as server:
                return server.requests_get(f'/item/{i}', headers=headers)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(50)]
            responses = [f.result() for f in futures]
        
        assert all(r.status_code in [200, 404] for r in responses)
```

### 6. Lambda Handler Testing

```python
"""
test_lambda_handler.py
Test AWS Lambda integration
"""
import re
import types
import pytest
from unittest import TestCase
from osbot_utils.utils.Json import str_to_json
from tests.unit.Service__Fast_API__Test_Objs import setup_local_stack
from your_api.fast_api.lambda_handler import run

class test_lambda_handler(TestCase):
    """Test Lambda handler integration"""
    
    @classmethod
    def setUpClass(cls):
        # Only setup LocalStack if testing AWS services
        # setup_local_stack()
        cls.handler = staticmethod(run)
    
    def test_handler_type(self):
        """Verify handler is callable"""
        assert type(self.handler) is types.FunctionType
    
    def test_lambda_invocation(self):
        """Test Lambda handler with API Gateway event"""
        # API Gateway v2 event
        event = {
            'version': '2.0',
            'requestContext': {
                'http': {
                    'method': 'GET',
                    'path': '/info/version',
                    'sourceIp': '127.0.0.1'
                }
            },
            'headers': {
                'X-API-Key': 'test-key'
            }
        }
        
        response = self.handler(event=event, context=None)
        assert type(response) is dict
        assert response.get('statusCode') == 200
        
        body = str_to_json(response.get('body'))
        assert 'version' in body
    
    def test_lambda_auth_required(self):
        """Test Lambda requires authentication"""
        event = {
            'version': '2.0',
            'requestContext': {
                'http': {
                    'method': 'GET',
                    'path': '/',
                    'sourceIp': '127.0.0.1'
                }
            }
        }
        
        response = self.handler(event=event)
        assert response.get('statusCode') == 401
        
        body = str_to_json(response.get('body'))
        assert 'Client API key is missing' in body.get('message')
```

## 🎯 Testing Best Practices

### 1. Test Organization Pattern

```python
class test_YourComponent(TestCase):
    """
    Standard test class structure:
    1. setUpClass - One-time setup using singleton
    2. test_setUpClass - Verify setup
    3. test_direct_calls - Test without HTTP
    4. test_client_calls - Test with client (if needed)
    5. test_edge_cases - Error conditions
    """
    
    @classmethod
    def setUpClass(cls):
        """Always use singleton setup"""
        # For routes without client
        cls.component = YourComponent()
        
        # OR for client-based tests
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client
```

### 2. When to Use Each Testing Approach

| Test Type | Use Case | Example |
|-----------|----------|---------|
| **Direct Route Testing** | Business logic, data processing | `test_Routes__Domain.py` |
| **Client Testing** | HTTP behavior, auth, headers | `test_Routes__Domain__client.py` |
| **HTTP Server Testing** | Real ports, streaming, WebSockets | `test_Service__Fast_API__http.py` |
| **Lambda Testing** | AWS integration, event handling | `test_lambda_handler.py` |

### 3. Performance Considerations

```python
# ✅ GOOD - Use singleton pattern
@classmethod
def setUpClass(cls):
    with setup__service_fast_api_test_objs() as _:
        cls.client = _.fast_api__client

# ❌ BAD - Creating new instances per test
def setUp(self):
    self.fast_api = Fast_API().setup()  # Slow!
    self.client = self.fast_api.client()
```

### 4. Type_Safe Schema Testing

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Schema__User(Type_Safe):
    username: str
    email: str
    age: int

class test_Schema__User(TestCase):
    """Test Type_Safe schemas"""
    
    def test_creation(self):
        user = Schema__User(
            username='alice',
            email='alice@example.com',
            age=30
        )
        assert user.username == 'alice'
        assert user.json() == {
            'username': 'alice',
            'email': 'alice@example.com',
            'age': 30
        }
    
    def test_validation(self):
        """Type_Safe validates at instantiation"""
        with pytest.raises(TypeError):
            Schema__User(
                username='bob',
                email='bob@example.com',
                age='not_a_number'  # Will fail
            )
```

## 🚀 Running Tests

### Basic Commands

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/unit/fast_api/test_Service__Fast_API.py

# Run specific test class
python -m pytest tests/unit/fast_api/test_Service__Fast_API.py::test_Service__Fast_API

# Run specific test method
python -m pytest tests/unit/fast_api/test_Service__Fast_API.py::test_Service__Fast_API::test__init__

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run tests matching pattern
python -m pytest tests/ -k "client"

# Run with verbose output
python -m pytest tests/ -v
```

## 📋 Project-Specific Service__Fast_API Template

```python
"""
Service__Fast_API.py
Your main Fast_API service class
"""
from osbot_fast_api.api.Fast_API import Fast_API
from your_api.fast_api.routes.Routes__Info import Routes__Info
from your_api.fast_api.routes.Routes__YourDomain import Routes__YourDomain

class Service__Fast_API(Fast_API):
    """Main service configuration"""
    
    enable_cors = True
    enable_api_key = True
    
    def setup_routes(self):
        """Configure all routes"""
        self.add_routes(Routes__Info)
        self.add_routes(Routes__YourDomain)
        # Add more routes as needed
        return self
```

## 🎯 Testing Checklist

- [ ] Create `Service__Fast_API__Test_Objs.py` singleton
- [ ] Setup environment variables in singleton
- [ ] Test routes directly (without HTTP) where possible
- [ ] Use client tests for HTTP-specific behavior
- [ ] Only use Fast_API_Server when real HTTP needed
- [ ] Test authentication and authorization
- [ ] Test error handling and edge cases
- [ ] Verify all routes are configured
- [ ] Test Lambda handler if applicable
- [ ] Maintain test isolation (no shared state between tests)
- [ ] Use `with` statements for proper context management
- [ ] Assert setup completion in test_setUpClass methods

## 💡 Key Differences from Fixture-Based Testing

1. **No pytest fixtures** - Use `TestCase` and `setUpClass`
2. **Singleton pattern** - One Fast_API instance for all tests
3. **Direct testing** - Test route methods directly when possible
4. **Explicit setup** - Call `setup__service_fast_api_test_objs()` in each test class
5. **Context managers** - Use `with` statements for resource management
6. **Performance focus** - Avoid recreating objects unnecessarily