# Testing Guide for OSBot-Fast-API

## 📋 Overview

This guide covers testing strategies and utilities for OSBot-Fast-API applications, including unit tests, integration tests, and production testing patterns.

## 🧪 Testing Infrastructure

### Fast_API_Server

The primary testing utility for OSBot-Fast-API applications:

```python
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server

class Fast_API_Server(Type_Safe):
    app       : FastAPI
    port      : int         # Auto-allocated if 0
    log_level : str = "error"
    config    : Config = None
    server    : Server = None
    thread    : Thread = None
    running   : bool = False
```

**Key Features**:
- Context manager support
- Automatic port allocation
- Request helper methods
- Thread-safe operation
- Clean startup/shutdown

## 🔧 Basic Testing Setup

### Simple Test Example

```python
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server

def test_basic_api():
    # Create and setup API
    fast_api = Fast_API()
    fast_api.setup()
    
    # Test with server
    with Fast_API_Server(app=fast_api.app()) as server:
        response = server.requests_get('/config/status')
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}
```

### Testing with Routes

```python
import pytest
from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes

class Test_Routes(Fast_API_Routes):
    tag = 'test'
    
    def echo__message(self, message: str):
        return {'echo': message}
    
    def setup_routes(self):
        self.add_route_get(self.echo__message)

def test_custom_routes():
    fast_api = Fast_API()
    fast_api.setup()
    fast_api.add_routes(Test_Routes)
    
    with Fast_API_Server(app=fast_api.app()) as server:
        response = server.requests_get('/test/echo/hello')
        assert response.json() == {'echo': 'hello'}
```

## 🔐 Testing Type-Safe Conversion

### Unit Test for Type Conversion

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_fast_api.utils.type_safe.Type_Safe__To__BaseModel import type_safe__to__basemodel

class User(Type_Safe):
    name: str
    age: int
    email: str

def test_type_conversion():
    # Create Type_Safe instance
    user = User(name="Alice", age=30, email="alice@example.com")
    
    # Convert to BaseModel
    UserModel = type_safe__to__basemodel.convert_class(User)
    user_model = type_safe__to__basemodel.convert_instance(user)
    
    # Verify conversion
    assert user_model.name == "Alice"
    assert user_model.model_dump() == user.json()
```

### Integration Test with Routes

```python
class UserRequest(Type_Safe):
    username: str
    password: str

class UserResponse(Type_Safe):
    id: str
    username: str
    created: bool

class Routes_Users(Fast_API_Routes):
    tag = 'users'
    
    def register(self, user: UserRequest) -> UserResponse:
        return UserResponse(
            id="user_123",
            username=user.username,
            created=True
        )
    
    def setup_routes(self):
        self.add_route_post(self.register)

def test_type_safe_routes():
    fast_api = Fast_API()
    fast_api.setup()
    fast_api.add_routes(Routes_Users)
    
    with Fast_API_Server(app=fast_api.app()) as server:
        user_data = {
            'username': 'testuser',
            'password': 'secret123'
        }
        
        response = server.requests_post('/users/register', data=user_data)
        assert response.status_code == 200
        result = response.json()
        assert result['username'] == 'testuser'
        assert result['created'] == True
```

## 🛡️ Testing Middleware

### API Key Middleware

```python
import os

def test_api_key_middleware():
    # Setup environment
    os.environ['FAST_API__AUTH__API_KEY__NAME'] = 'X-API-Key'
    os.environ['FAST_API__AUTH__API_KEY__VALUE'] = 'test-secret-key'
    
    fast_api = Fast_API(enable_api_key=True)
    fast_api.setup()
    
    with Fast_API_Server(app=fast_api.app()) as server:
        # Without API key - should fail
        response = server.requests_get('/config/status')
        assert response.status_code == 401
        assert 'error' in response.json()
        
        # With wrong API key - should fail
        headers = {'X-API-Key': 'wrong-key'}
        response = server.requests_get('/config/status', headers=headers)
        assert response.status_code == 401
        
        # With correct API key - should succeed
        headers = {'X-API-Key': 'test-secret-key'}
        response = server.requests_get('/config/status', headers=headers)
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}
```

### CORS Middleware

```python
def test_cors_middleware():
    fast_api = Fast_API(enable_cors=True)
    fast_api.setup()
    
    with Fast_API_Server(app=fast_api.app()) as server:
        headers = {'Origin': 'http://example.com'}
        response = server.requests_get('/config/status', headers=headers)
        
        # Check CORS headers
        assert 'access-control-allow-origin' in response.headers
        assert response.headers['access-control-allow-origin'] == '*'
```

## 📊 Testing HTTP Events

### Event Tracking Test

```python
def test_http_events():
    fast_api = Fast_API()
    fast_api.http_events.max_requests_logged = 10
    fast_api.setup()
    
    # Track events
    events_captured = []
    
    def on_response(response, event):
        events_captured.append({
            'path': event.http_event_request.path,
            'status': event.http_event_response.status_code
        })
    
    fast_api.http_events.callback_on_response = on_response
    
    with Fast_API_Server(app=fast_api.app()) as server:
        # Make requests
        server.requests_get('/config/status')
        server.requests_get('/config/version')
        
        # Verify events captured
        assert len(events_captured) == 2
        assert events_captured[0]['path'] == '/config/status'
        assert events_captured[0]['status'] == 200
```

### Event Data Validation

```python
from fastapi import Request

class Routes_Debug(Fast_API_Routes):
    tag = 'debug'
    
    def event_info(self, request: Request):
        return {
            'event_id': str(request.state.request_id),
            'has_data': request.state.request_data is not None
        }
    
    def setup_routes(self):
        self.add_route_get(self.event_info)

def test_event_data_access():
    fast_api = Fast_API()
    fast_api.setup()
    fast_api.add_routes(Routes_Debug)
    
    with Fast_API_Server(app=fast_api.app()) as server:
        response = server.requests_get('/debug/event-info')
        data = response.json()
        
        # Verify event data available
        assert 'event_id' in data
        assert data['has_data'] == True
        assert len(data['event_id']) == 36  # UUID length
```

## 🚀 Performance Testing

### Load Testing Pattern

```python
import time
import concurrent.futures

def test_concurrent_requests():
    fast_api = Fast_API()
    fast_api.setup()
    
    with Fast_API_Server(app=fast_api.app()) as server:
        def make_request():
            return server.requests_get('/config/status')
        
        start_time = time.time()
        
        # Concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            responses = [f.result() for f in futures]
        
        duration = time.time() - start_time
        
        # Verify all succeeded
        assert all(r.status_code == 200 for r in responses)
        assert duration < 5.0  # Should handle 100 requests in < 5 seconds
```

### Memory Testing

```python
import tracemalloc

def test_memory_usage():
    tracemalloc.start()
    
    fast_api = Fast_API()
    fast_api.http_events.max_requests_logged = 1000
    fast_api.setup()
    
    with Fast_API_Server(app=fast_api.app()) as server:
        # Make many requests
        for i in range(100):
            server.requests_get(f'/config/status?id={i}')
        
        # Check memory
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory should be reasonable (< 50MB for 100 requests)
        assert peak / 1024 / 1024 < 50
```

## 🐛 Error Testing

### Exception Handling

```python
class Routes_Errors(Fast_API_Routes):
    tag = 'errors'
    
    def trigger_error(self):
        raise ValueError("Test error")
    
    def validation_error(self, value: int):
        if value < 0:
            raise ValueError("Value must be positive")
        return {'value': value}
    
    def setup_routes(self):
        self.add_route_get(self.trigger_error)
        self.add_route_get(self.validation_error)

def test_error_handling():
    fast_api = Fast_API()
    fast_api.setup()
    fast_api.add_routes(Routes_Errors)
    
    with Fast_API_Server(app=fast_api.app()) as server:
        # Test unhandled exception
        response = server.requests_get('/errors/trigger-error')
        assert response.status_code == 500
        assert 'error' in response.json()
        
        # Test validation error
        response = server.requests_get('/errors/validation-error/-5')
        assert response.status_code == 400
```

## 🔍 Mock Testing

### Using Mock_Obj__Fast_API__Request_Data

```python
from osbot_fast_api.utils.testing.Mock_Obj__Fast_API__Request_Data import Mock_Obj__Fast_API__Request_Data

def test_mock_request_data():
    mock = Mock_Obj__Fast_API__Request_Data()
    request_data = mock.create()
    
    # Verify mock data
    assert request_data.event_id is not None
    assert request_data.http_event_request.method == 'GET'
    assert request_data.http_event_request.path == '/an-path'
    assert request_data.http_event_response.status_code == 201
```

### Custom Mock Data

```python
def test_custom_mock():
    mock = Mock_Obj__Fast_API__Request_Data()
    mock.method = 'POST'
    mock.path = '/api/users'
    mock.res_status_code = 200
    mock.city = 'London'
    mock.country = 'UK'
    
    request_data = mock.create()
    
    assert request_data.http_event_request.method == 'POST'
    assert request_data.http_event_request.path == '/api/users'
    assert request_data.http_event_info.client_city == 'London'
```

## 📝 Test Organization

### Pytest Structure

```python
# tests/unit/test_type_safe.py
class TestTypeSafeConversion:
    def test_simple_conversion(self):
        # Unit tests for type conversion
        pass

# tests/integration/test_routes.py
class TestAPIRoutes:
    @pytest.fixture
    def fast_api(self):
        api = Fast_API()
        api.setup()
        return api
    
    def test_route_registration(self, fast_api):
        # Integration tests
        pass

# tests/qa/test_production.py
class TestProduction:
    def test_health_endpoint(self):
        # Tests against deployed service
        pass
```

## ✅ Testing Checklist

### Unit Tests
- [ ] Type_Safe class validation
- [ ] Type conversion functions
- [ ] Route path generation
- [ ] Event data structures
- [ ] Middleware logic

### Integration Tests
- [ ] Route registration
- [ ] Request/response flow
- [ ] Middleware chain
- [ ] Error handling
- [ ] Type_Safe conversion in routes

### System Tests
- [ ] Full API workflow
- [ ] Authentication flow
- [ ] Event tracking
- [ ] Performance benchmarks
- [ ] Memory usage

### Production Tests
- [ ] Health checks
- [ ] API key validation
- [ ] CORS headers
- [ ] Error responses
- [ ] Response times

## 🎯 Best Practices

1. **Use Fast_API_Server**: Always use the provided test server
2. **Test Type Conversion**: Verify Type_Safe ↔ BaseModel conversion
3. **Mock External Dependencies**: Use mocks for external services
4. **Test Error Cases**: Include negative test cases
5. **Check Event Tracking**: Verify events are properly tracked
6. **Test Middleware**: Validate middleware behavior
7. **Performance Baseline**: Establish performance benchmarks
8. **Clean Environment**: Reset environment variables after tests
9. **Async Testing**: Use pytest-asyncio for async routes
10. **Coverage Target**: Aim for >90% code coverage