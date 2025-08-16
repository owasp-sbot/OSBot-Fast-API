# OSBot-Fast-API Test Patterns Reference

## 🎯 Quick Reference Guide

This document provides quick reference patterns for common testing scenarios in OSBot-Fast-API.

## 📝 Test Pattern Catalog

### Pattern 1: Fast_API_Server Context Manager

**Use Case**: Testing API endpoints with automatic server lifecycle management

```python
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server

def test_with_server():
    with Fast_API_Server(app=fast_api.app()) as server:
        response = server.requests_get('/endpoint')
        assert response.status_code == 200
        assert response.json() == expected_data
```

**Variations**:

```python
# With headers
headers = {'X-API-Key': 'secret', 'Content-Type': 'application/json'}
response = server.requests_get('/protected', headers=headers)

# With POST data
data = {'name': 'Alice', 'age': 30}
response = server.requests_post('/users', data=data)

# With query parameters
params = {'filter': 'active', 'limit': 10}
response = server.requests_get('/users', params=params)

# With streaming
response = server.requests_get('/stream', stream=True)
for line in response.iter_lines():
    process(line)
```

### Pattern 2: Type_Safe Testing

**Use Case**: Testing Type_Safe class conversions and validations

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe

class User(Type_Safe):
    name: str
    age: int
    email: str

def test_type_safe():
    # Test creation
    user = User(name="Alice", age=30, email="alice@example.com")
    assert user.name == "Alice"
    
    # Test JSON serialization
    assert user.json() == {
        'name': 'Alice',
        'age': 30,
        'email': 'alice@example.com'
    }
    
    # Test from JSON
    user2 = User.from_json({'name': 'Bob', 'age': 25, 'email': 'bob@example.com'})
    assert user2.name == "Bob"
    
    # Test validation
    with pytest.raises(ValueError):
        User(name="Charlie", age="not_a_number", email="charlie@example.com")
```

### Pattern 3: Middleware Testing

**Use Case**: Testing middleware behavior and chain execution

```python
def test_api_key_middleware():
    # Setup environment
    os.environ['FAST_API__AUTH__API_KEY__NAME'] = 'X-API-Key'
    os.environ['FAST_API__AUTH__API_KEY__VALUE'] = 'test-key'
    
    fast_api = Fast_API(enable_api_key=True)
    fast_api.setup()
    
    with Fast_API_Server(app=fast_api.app()) as server:
        # Without key - should fail
        response = server.requests_get('/protected')
        assert response.status_code == 401
        
        # With correct key - should succeed
        headers = {'X-API-Key': 'test-key'}
        response = server.requests_get('/protected', headers=headers)
        assert response.status_code == 200
```

### Pattern 4: Route Testing with Path Parameters

**Use Case**: Testing dynamic route parameters

```python
class Routes_Users(Fast_API__Routes):
    tag = 'users'
    
    def get__user_id(self, user_id: str):
        return {'id': user_id}
    
    def get__user_id__posts__post_id(self, user_id: str, post_id: str):
        return {'user': user_id, 'post': post_id}
    
    def setup_routes(self):
        self.add_route_get(self.get__user_id)
        self.add_route_get(self.get__user_id__posts__post_id)

def test_path_params():
    fast_api = Fast_API().setup()
    fast_api.add_routes(Routes_Users)
    
    client = fast_api.client()
    
    # Single parameter
    response = client.get('/users/get/123')
    assert response.json() == {'id': '123'}
    
    # Multiple parameters
    response = client.get('/users/get/123/posts/456')
    assert response.json() == {'user': '123', 'post': '456'}
```

### Pattern 5: HTTP Event Testing

**Use Case**: Testing HTTP event tracking and callbacks

```python
def test_http_events():
    events_captured = []
    
    def on_request(event):
        events_captured.append({
            'type': 'request',
            'path': event.http_event_request.path,
            'method': event.http_event_request.method
        })
    
    def on_response(response, event):
        events_captured.append({
            'type': 'response',
            'status': event.http_event_response.status_code,
            'duration': float(event.http_event_request.duration)
        })
    
    fast_api = Fast_API()
    fast_api.http_events.callback_on_request = on_request
    fast_api.http_events.callback_on_response = on_response
    fast_api.setup()
    
    with Fast_API_Server(app=fast_api.app()) as server:
        server.requests_get('/config/status')
        
        assert len(events_captured) == 2
        assert events_captured[0]['type'] == 'request'
        assert events_captured[1]['type'] == 'response'
        assert events_captured[1]['duration'] < 0.1
```

### Pattern 6: Mock Testing

**Use Case**: Using mock objects for isolated testing

```python
from osbot_fast_api.utils.testing.Mock_Obj__Fast_API__Request_Data import Mock_Obj__Fast_API__Request_Data
from unittest.mock import MagicMock, patch

def test_with_mock():
    # Mock request data
    mock = Mock_Obj__Fast_API__Request_Data()
    mock.method = 'POST'
    mock.path = '/api/users'
    mock.res_status_code = 201
    
    request_data = mock.create()
    assert request_data.http_event_request.method == 'POST'
    assert request_data.http_event_response.status_code == 201
    
    # Mock external service
    with patch('external_service.api_call') as mock_api:
        mock_api.return_value = {'status': 'success'}
        
        response = client.post('/process')
        assert response.json()['status'] == 'success'
        mock_api.assert_called_once()
```

### Pattern 7: Performance Testing

**Use Case**: Testing performance constraints

```python
from osbot_utils.helpers.duration.decorators.capture_duration import capture_duration

def test_performance():
    with Fast_API_Server(app=fast_api.app()) as server:
        # Single request performance
        with capture_duration() as duration:
            response = server.requests_get('/fast-endpoint')
        assert duration.seconds < 0.010  # < 10ms
        
        # Throughput testing
        with capture_duration() as duration:
            responses = []
            for i in range(100):
                responses.append(server.requests_get(f'/item/{i}'))
        
        assert duration.seconds < 1.0  # 100 requests in < 1s
        assert all(r.status_code == 200 for r in responses)
        
        # Concurrent testing
        import concurrent.futures
        
        def make_request(i):
            return server.requests_get(f'/item/{i}')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(100)]
            responses = [f.result() for f in futures]
        
        assert all(r.status_code == 200 for r in responses)
```

### Pattern 8: Error Testing

**Use Case**: Testing error handling and edge cases

```python
def test_error_handling():
    with Fast_API_Server(app=fast_api.app()) as server:
        # Validation error
        response = server.requests_post('/user', data={'age': 'invalid'})
        assert response.status_code == 422
        error = response.json()
        assert error['detail'][0]['type'] == 'value_error'
        
        # Not found
        response = server.requests_get('/user/99999')
        assert response.status_code == 404
        assert response.json()['detail'] == 'User not found'
        
        # Server error (triggered)
        response = server.requests_get('/trigger-error')
        assert response.status_code == 500
        
        # Timeout simulation
        with pytest.raises(ReadTimeout):
            server.requests_get('/slow-endpoint', timeout=0.001)
```

### Pattern 9: State Testing

**Use Case**: Testing stateful operations

```python
class test_Stateful_Operations(TestCase):
    def setUp(self):
        """Fresh state for each test"""
        self.storage = {}
        self.fast_api = Fast_API().setup()
        self.server = Fast_API_Server(app=self.fast_api.app())
        self.server.start()
    
    def tearDown(self):
        """Clean up state"""
        self.server.stop()
        self.storage.clear()
    
    def test_crud_operations(self):
        # Create
        create_data = {'name': 'Item 1'}
        response = self.server.requests_post('/items', data=create_data)
        item_id = response.json()['id']
        
        # Read
        response = self.server.requests_get(f'/items/{item_id}')
        assert response.json()['name'] == 'Item 1'
        
        # Update
        update_data = {'name': 'Updated Item'}
        response = self.server.requests_put(f'/items/{item_id}', data=update_data)
        assert response.json()['name'] == 'Updated Item'
        
        # Delete
        response = self.server.requests_delete(f'/items/{item_id}')
        assert response.status_code == 204
        
        # Verify deletion
        response = self.server.requests_get(f'/items/{item_id}')
        assert response.status_code == 404
```

### Pattern 10: Integration Testing

**Use Case**: Testing complete workflows

```python
def test_complete_workflow():
    """Test a complete user registration and login flow"""
    
    with Fast_API_Server(app=fast_api.app()) as server:
        # Step 1: Register user
        registration_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepass123'
        }
        response = server.requests_post('/register', data=registration_data)
        assert response.status_code == 201
        user_id = response.json()['user_id']
        
        # Step 2: Verify email (simulation)
        verify_token = response.json()['verify_token']
        response = server.requests_get(f'/verify/{verify_token}')
        assert response.status_code == 200
        
        # Step 3: Login
        login_data = {
            'username': 'testuser',
            'password': 'securepass123'
        }
        response = server.requests_post('/login', data=login_data)
        assert response.status_code == 200
        auth_token = response.json()['token']
        
        # Step 4: Access protected resource
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = server.requests_get('/profile', headers=headers)
        assert response.status_code == 200
        assert response.json()['username'] == 'testuser'
        
        # Step 5: Logout
        response = server.requests_post('/logout', headers=headers)
        assert response.status_code == 200
        
        # Step 6: Verify token invalidated
        response = server.requests_get('/profile', headers=headers)
        assert response.status_code == 401
```

## 🔧 Test Utilities

### Custom Assertions

```python
def assert_valid_response(response, expected_status=200, required_fields=None):
    """Custom assertion for API responses"""
    assert response.status_code == expected_status
    
    if required_fields:
        json_data = response.json()
        for field in required_fields:
            assert field in json_data, f"Missing required field: {field}"
    
    # Check response headers
    assert 'fast-api-request-id' in response.headers
    return response.json()

# Usage
response = server.requests_get('/user/123')
user_data = assert_valid_response(response, 200, ['id', 'name', 'email'])
```

### Test Data Builders

```python
class TestDataBuilder:
    """Builder pattern for test data"""
    
    @staticmethod
    def user(**overrides):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'active': True
        }
        return {**defaults, **overrides}
    
    @staticmethod
    def product(**overrides):
        defaults = {
            'name': 'Test Product',
            'price': 99.99,
            'category': 'test',
            'in_stock': True
        }
        return {**defaults, **overrides}

# Usage
user1 = TestDataBuilder.user(username='alice', age=30)
user2 = TestDataBuilder.user(email='bob@example.com')
product = TestDataBuilder.product(price=149.99, in_stock=False)
```

### Parametrized Testing

```python
import pytest

@pytest.mark.parametrize("input_value,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    (None, None),
    ("123", "123"),
])
def test_uppercase_conversion(input_value, expected):
    response = client.post('/uppercase', json={'value': input_value})
    assert response.json()['result'] == expected

@pytest.mark.parametrize("method,path,expected_status", [
    ("GET", "/", 307),
    ("GET", "/docs", 200),
    ("GET", "/config/status", 200),
    ("POST", "/users", 201),
    ("GET", "/nonexistent", 404),
])
def test_endpoint_availability(method, path, expected_status):
    response = getattr(client, method.lower())(path)
    assert response.status_code == expected_status
```

## 📊 Test Organization Best Practices

### 1. Test Naming Convention
```python
def test__{test_type}__{component}__{scenario}():
    """
    test_type: unit, integration, edge_case, performance
    component: the component being tested
    scenario: what is being tested
    """
    pass

# Examples:
def test__unit__type_conversion__simple_types():
def test__integration__user_workflow__registration():
def test__edge_case__api_key__missing_header():
def test__performance__bulk_operations__1000_items():
```

### 2. Test Documentation
```python
def test_complex_scenario():
    """
    Test: Complex user workflow with multiple steps
    
    Setup:
        - Create test user
        - Setup mock external service
    
    Steps:
        1. User registration
        2. Email verification
        3. Profile update
        4. Data validation
    
    Expected:
        - All steps complete successfully
        - Data integrity maintained
        - Events properly tracked
    """
    pass
```

### 3. Test Fixtures
```python
@pytest.fixture
def authenticated_client():
    """Provide authenticated client for tests"""
    client = TestClient(app)
    response = client.post('/login', json={'username': 'test', 'password': 'test'})
    token = response.json()['token']
    client.headers['Authorization'] = f'Bearer {token}'
    return client

@pytest.fixture
def sample_data():
    """Provide sample test data"""
    return {
        'users': [TestDataBuilder.user() for _ in range(5)],
        'products': [TestDataBuilder.product() for _ in range(10)]
    }
```