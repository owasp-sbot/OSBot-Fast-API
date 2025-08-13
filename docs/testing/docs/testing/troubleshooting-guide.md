# Testing Troubleshooting Guide

## 🔍 Common Testing Issues and Solutions

This guide addresses common problems encountered when testing OSBot-Fast-API applications.

## 🐛 Singleton Pattern Issues

### Problem: Tests Affecting Each Other

**Symptom**: Tests pass individually but fail when run together.

**Cause**: Shared state in singleton Fast_API instance.

**Solution**:
```python
class test_Isolated(TestCase):
    """Ensure test isolation"""
    
    def setUp(self):
        """Clear state before each test"""
        with setup__service_fast_api_test_objs() as _:
            # Clear HTTP events
            _.fast_api.http_events.requests_data.clear()
            _.fast_api.http_events.requests_order.clear()
            
            # Reset any counters or state
            if hasattr(_.fast_api, 'request_counter'):
                _.fast_api.request_counter = 0
    
    def tearDown(self):
        """Clean up after each test"""
        # Remove any test data created
        pass
```

### Problem: Singleton Not Initialized

**Symptom**: `AttributeError: 'NoneType' object has no attribute 'client'`

**Solution**:
```python
@classmethod
def setUpClass(cls):
    """Ensure singleton is initialized"""
    with setup__service_fast_api_test_objs() as _:
        # Force initialization if needed
        if not _.setup_completed:
            raise RuntimeError("Singleton setup failed")
        cls.client = _.fast_api__client
```

## 🔐 Authentication Issues

### Problem: API Key Not Working in Tests

**Symptom**: 401 errors even with correct API key.

**Cause**: Environment variables not set or headers not included.

**Solution**:
```python
from osbot_utils.utils.Env import set_env

class test_With_Auth(TestCase):
    @classmethod
    def setUpClass(cls):
        # Set environment variables BEFORE creating Fast_API
        set_env('FAST_API__AUTH__API_KEY__NAME', 'X-API-Key')
        set_env('FAST_API__AUTH__API_KEY__VALUE', 'test-key')
        
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            # Add header to client
            cls.client.headers['X-API-Key'] = 'test-key'
```

### Problem: Cookie Authentication Not Working

**Solution**:
```python
def test_cookie_auth(self):
    """Test with cookie instead of header"""
    # Remove header if present
    self.client.headers.pop('X-API-Key', None)
    
    # Use cookies parameter
    response = self.client.get('/protected', cookies={'X-API-Key': 'test-key'})
    assert response.status_code == 200
```

## 🔄 Type Conversion Issues

### Problem: Type_Safe Not Converting to BaseModel

**Symptom**: `AttributeError: 'Type_Safe' object has no attribute 'dict'`

**Cause**: FastAPI expecting Pydantic BaseModel but receiving Type_Safe.

**Solution**:
```python
def test_type_safe_endpoint(self):
    """Ensure proper type conversion"""
    from osbot_utils.type_safe.Type_Safe import Type_Safe
    
    class UserRequest(Type_Safe):
        name: str
        age: int
    
    # Convert to dict for JSON serialization
    user_data = UserRequest(name="Alice", age=30).json()
    
    # Send as JSON
    response = self.client.post('/user', json=user_data)
    assert response.status_code == 200
```

### Problem: Nested Type_Safe Objects Not Converting

**Solution**:
```python
class test_Nested_Conversion(TestCase):
    def test_nested_objects(self):
        """Handle nested Type_Safe objects"""
        
        class Address(Type_Safe):
            street: str
            city: str
        
        class User(Type_Safe):
            name: str
            address: Address
        
        # Create nested structure
        user = User(
            name="Bob",
            address=Address(street="123 Main", city="NYC")
        )
        
        # Convert to JSON-serializable dict
        user_dict = user.json()
        
        response = self.client.post('/user', json=user_dict)
        assert response.status_code == 200
```

## 🚫 Route Testing Issues

### Problem: Route Not Found (404)

**Symptom**: Valid routes returning 404.

**Diagnosis**:
```python
def test_debug_routes(self):
    """Debug available routes"""
    with setup__service_fast_api_test_objs() as _:
        # Print all registered routes
        routes = _.fast_api.routes_paths()
        print("\nAvailable routes:")
        for route in sorted(routes):
            print(f"  - {route}")
        
        # Check if your route exists
        assert '/your-route' in routes
```

### Problem: Method Not Allowed (405)

**Solution**:
```python
def test_correct_method(self):
    """Use correct HTTP method"""
    # Check route configuration
    routes = self.fast_api.routes()
    
    for route in routes:
        if route['http_path'] == '/your-endpoint':
            print(f"Allowed methods: {route['http_methods']}")
    
    # Use correct method
    if 'POST' in route['http_methods']:
        response = self.client.post('/your-endpoint', json={})
    else:
        response = self.client.get('/your-endpoint')
```

## ⚡ Performance Issues

### Problem: Tests Running Slowly

**Cause**: Creating new Fast_API instances.

**Solution**:
```python
# ❌ BAD - Slow
class test_Slow(TestCase):
    def setUp(self):
        self.fast_api = Fast_API().setup()  # Created for each test!
        self.client = self.fast_api.client()

# ✅ GOOD - Fast
class test_Fast(TestCase):
    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client  # Reuses singleton
```

### Problem: Memory Leaks in Tests

**Solution**:
```python
class test_Memory_Safe(TestCase):
    @classmethod
    def tearDownClass(cls):
        """Clean up resources"""
        # Clear large data structures
        if hasattr(cls, 'large_data'):
            del cls.large_data
        
        # Clear event history
        with setup__service_fast_api_test_objs() as _:
            _.fast_api.http_events.requests_data.clear()
        
        # Force garbage collection
        import gc
        gc.collect()
```

## 🔌 Fast_API_Server Issues

### Problem: Port Already in Use

**Symptom**: `OSError: [Errno 48] Address already in use`

**Solution**:
```python
def test_with_auto_port(self):
    """Use automatic port allocation"""
    from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server
    
    # Don't specify port - let it auto-allocate
    with Fast_API_Server(app=self.app) as server:
        assert server.port > 19999  # Auto-allocated port
        response = server.requests_get('/test')
```

### Problem: Server Not Stopping

**Solution**:
```python
class test_Server_Cleanup(TestCase):
    def test_ensure_cleanup(self):
        """Ensure server stops properly"""
        from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server
        
        server = Fast_API_Server(app=self.app)
        try:
            server.start()
            # Do tests
            response = server.requests_get('/test')
        finally:
            # Always stop in finally block
            server.stop()
            assert server.is_port_open() is False
```

## 🧪 Mock Testing Issues

### Problem: Mocks Not Being Applied

**Solution**:
```python
from unittest.mock import patch, MagicMock

class test_Mocking(TestCase):
    @patch('your_api.service.external_api.call')
    def test_with_mock(self, mock_call):
        """Ensure mock is in correct location"""
        # Configure mock
        mock_call.return_value = {'status': 'success'}
        
        # Make request that triggers the mocked call
        response = self.client.post('/process')
        
        # Verify mock was called
        mock_call.assert_called_once()
        assert response.json()['status'] == 'success'
```

## 🔍 Debugging Techniques

### Enable Detailed Logging

```python
import logging

class test_Debug(TestCase):
    @classmethod
    def setUpClass(cls):
        # Enable debug logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Enable Fast_API debug mode
        with setup__service_fast_api_test_objs() as _:
            _.fast_api.app().debug = True
            cls.client = _.fast_api__client
```

### Inspect Request/Response

```python
def test_inspect_request(self):
    """Debug request/response details"""
    response = self.client.post('/endpoint', json={'key': 'value'})
    
    print("\n=== DEBUG INFO ===")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.text}")
    
    if response.status_code >= 400:
        print(f"Error: {response.json()}")
```

### Trace HTTP Events

```python
def test_trace_events(self):
    """Use HTTP events for debugging"""
    with setup__service_fast_api_test_objs() as _:
        # Enable tracing
        _.fast_api.http_events.trace_calls = True
        
        # Make request
        response = self.client.get('/test')
        
        # Get event data
        events = list(_.fast_api.http_events.requests_data.values())
        if events:
            event = events[-1]
            print(f"Path: {event.http_event_request.path}")
            print(f"Duration: {event.http_event_request.duration}")
            print(f"Status: {event.http_event_response.status_code}")
```

## 🔧 Environment Issues

### Problem: Missing Environment Variables

**Solution**:
```python
from osbot_utils.utils.Env import load_dotenv, get_env

class test_Environment(TestCase):
    @classmethod
    def setUpClass(cls):
        # Load .env file
        load_dotenv()
        
        # Verify required variables
        required_vars = [
            'FAST_API__AUTH__API_KEY__NAME',
            'FAST_API__AUTH__API_KEY__VALUE',
            'AWS_REGION',
        ]
        
        missing = [var for var in required_vars if not get_env(var)]
        if missing:
            raise EnvironmentError(f"Missing variables: {missing}")
```

## 📊 Coverage Issues

### Problem: Low Test Coverage

**Solution**:
```python
# Run with coverage
# pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

class test_Coverage_Improvement(TestCase):
    """Techniques to improve coverage"""
    
    def test_error_branches(self):
        """Test error handling branches"""
        # Test with invalid data
        response = self.client.post('/user', json={'age': 'invalid'})
        assert response.status_code == 422
        
        # Test with missing data
        response = self.client.post('/user', json={})
        assert response.status_code == 422
    
    def test_edge_cases(self):
        """Test boundary conditions"""
        test_cases = [
            (0, 'zero'),
            (-1, 'negative'),
            (999999999, 'large'),
            (None, 'null'),
        ]
        
        for value, case in test_cases:
            with self.subTest(case=case):
                response = self.client.post('/process', json={'value': value})
                assert response.status_code in [200, 400, 422]
```

## 🎯 Quick Fixes Checklist

- [ ] Check singleton is initialized in `setUpClass`
- [ ] Verify environment variables are set
- [ ] Ensure API key is in headers/cookies
- [ ] Use `.json()` method for Type_Safe serialization
- [ ] Check route exists with `fast_api.routes_paths()`
- [ ] Use correct HTTP method for endpoint
- [ ] Clear state between tests if needed
- [ ] Use context managers for Fast_API_Server
- [ ] Check port availability for server tests
- [ ] Verify mock patch locations

## 💡 Pro Tips

1. **Use `with self.subTest():`** for parametrized test cases
2. **Print available routes** when debugging 404s
3. **Check `setup_completed`** flag in singleton
4. **Use `finally` blocks** for cleanup
5. **Enable debug logging** when stuck
6. **Check HTTP events** for request details
7. **Test both success and failure paths**
8. **Mock external dependencies**
9. **Use descriptive test names**
10. **Document known issues** in tests