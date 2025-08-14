# Advanced Testing Patterns for OSBot-Fast-API

## 📋 Overview

This document covers advanced testing patterns specific to OSBot-Fast-API's unique features and real-world scenarios.

## 🔄 Type Conversion Testing Patterns

### Testing Type_Safe ↔ BaseModel Conversions

```python
from unittest import TestCase
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_fast_api.utils.type_safe.Type_Safe__To__BaseModel import type_safe__to__basemodel
from osbot_fast_api.utils.type_safe.BaseModel__To__Type_Safe import basemodel__to__type_safe

class test_Type_Conversions(TestCase):
    """Test bidirectional type conversions"""
    
    def test_round_trip_conversion(self):
        """Test data integrity through conversion cycles"""
        
        class User(Type_Safe):
            name: str
            age: int
            tags: list[str]
        
        # Original Type_Safe
        original = User(name="Alice", age=30, tags=["admin", "user"])
        
        # Convert to BaseModel
        base_model = type_safe__to__basemodel.convert_instance(original)
        
        # Convert back to Type_Safe
        recovered = basemodel__to__type_safe.convert_instance(base_model)
        
        # Verify data integrity
        assert original.json() == recovered.json()
        assert original.name == recovered.name
        assert original.tags == recovered.tags
    
    def test_nested_conversion(self):
        """Test deeply nested structure conversions"""
        
        class Address(Type_Safe):
            street: str
            city: str
        
        class Company(Type_Safe):
            name: str
            address: Address
        
        class Person(Type_Safe):
            name: str
            company: Company
        
        # Create nested structure
        person = Person(
            name="Bob",
            company=Company(
                name="TechCorp",
                address=Address(street="123 Main", city="NYC")
            )
        )
        
        # Test conversion preserves nesting
        base_model = type_safe__to__basemodel.convert_instance(person)
        assert base_model.company.address.city == "NYC"
        
        # Test round-trip
        recovered = basemodel__to__type_safe.convert_instance(base_model)
        assert recovered.company.address.street == "123 Main"
```

### Testing Type_Safe Primitives

```python
from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid import Random_Guid
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id import Safe_Id

class test_Type_Safe_Primitives(TestCase):
    """Test custom Type_Safe primitive types"""
    
    def test_random_guid(self):
        """Test GUID validation"""
        # Valid GUID
        guid = Random_Guid("123e4567-e89b-12d3-a456-426614174000")
        assert str(guid) == "123e4567-e89b-12d3-a456-426614174000"
        
        # Invalid GUID
        with self.assertRaises(ValueError) as context:
            Random_Guid("not-a-guid")
        assert "not a Guid" in str(context.exception)
    
    def test_safe_id(self):
        """Test Safe_Id sanitization"""
        # Unsafe characters get sanitized
        safe_id = Safe_Id("Hello World!@#$")
        assert str(safe_id) == "Hello_World____"
        
        # Already safe
        safe_id = Safe_Id("valid_id_123")
        assert str(safe_id) == "valid_id_123"
    
    def test_custom_primitive(self):
        """Test custom Type_Safe primitive"""
        
        class Email(Type_Safe__Primitive, str):
            def __new__(cls, value):
                if '@' not in value or '.' not in value.split('@')[1]:
                    raise ValueError(f"Invalid email: {value}")
                return super().__new__(cls, value.lower())
        
        # Valid email
        email = Email("John.Doe@Example.COM")
        assert str(email) == "john.doe@example.com"
        
        # Invalid email
        with self.assertRaises(ValueError):
            Email("not-an-email")
```

## 🔐 Authentication & Middleware Testing

### Testing API Key Middleware

```python
from unittest import TestCase
from osbot_utils.utils.Env import set_env, get_env
from tests.unit.Service__Fast_API__Test_Objs import setup__service_fast_api_test_objs

class test_API_Authentication(TestCase):
    """Test authentication middleware"""
    
    @classmethod
    def setUpClass(cls):
        # Set up different API keys for testing
        cls.valid_key = "valid-test-key-123"
        cls.invalid_key = "invalid-key-456"
        
        set_env('FAST_API__AUTH__API_KEY__NAME', 'X-API-Key')
        set_env('FAST_API__AUTH__API_KEY__VALUE', cls.valid_key)
        
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client
    
    def test_missing_api_key(self):
        """Test request without API key"""
        response = self.client.get('/protected', headers={})
        assert response.status_code == 401
        assert 'Client API key is missing' in response.json()['message']
    
    def test_invalid_api_key(self):
        """Test request with invalid API key"""
        headers = {'X-API-Key': self.invalid_key}
        response = self.client.get('/protected', headers=headers)
        assert response.status_code == 401
        assert 'Invalid API key' in response.json()['message']
    
    def test_valid_api_key_header(self):
        """Test request with valid API key in header"""
        headers = {'X-API-Key': self.valid_key}
        response = self.client.get('/protected', headers=headers)
        assert response.status_code == 200
    
    def test_api_key_in_cookie(self):
        """Test API key in cookie"""
        cookies = {'X-API-Key': self.valid_key}
        response = self.client.get('/protected', cookies=cookies)
        assert response.status_code == 200
```

### Testing HTTP Events

```python
class test_HTTP_Events(TestCase):
    """Test HTTP event tracking system"""
    
    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.fast_api = _.fast_api
            cls.client = _.fast_api__client
            # Enable event tracking
            cls.fast_api.http_events.max_requests_logged = 100
            cls.fast_api.http_events.clean_data = True
    
    def test_event_tracking(self):
        """Test events are tracked"""
        # Clear existing events
        self.fast_api.http_events.requests_data.clear()
        
        # Make request
        response = self.client.get('/test')
        
        # Check event was tracked
        assert len(self.fast_api.http_events.requests_data) > 0
        
        # Get event data
        event_id = list(self.fast_api.http_events.requests_data.keys())[0]
        event_data = self.fast_api.http_events.requests_data[event_id]
        
        assert event_data.http_event_request.path == '/test'
        assert event_data.http_event_response.status_code == 200
    
    def test_event_callbacks(self):
        """Test event callbacks"""
        requests_received = []
        responses_sent = []
        
        def on_request(event):
            requests_received.append(event.http_event_request.path)
        
        def on_response(response, event):
            responses_sent.append(event.http_event_response.status_code)
        
        self.fast_api.http_events.callback_on_request = on_request
        self.fast_api.http_events.callback_on_response = on_response
        
        # Make requests
        self.client.get('/test1')
        self.client.get('/test2')
        
        assert '/test1' in requests_received
        assert '/test2' in requests_received
        assert 200 in responses_sent
```

## 🔄 Mock Testing Patterns

### Using Mock Request Data

```python
from osbot_fast_api.utils.testing.Mock_Obj__Fast_API__Request_Data import Mock_Obj__Fast_API__Request_Data

class test_Mock_Request_Data(TestCase):
    """Test with mock request data"""
    
    def test_create_mock_request(self):
        """Create mock HTTP event data"""
        mock = Mock_Obj__Fast_API__Request_Data()
        mock.method = 'POST'
        mock.path = '/api/users'
        mock.res_status_code = 201
        mock.city = 'London'
        mock.country = 'UK'
        mock.ip_address = '192.168.1.1'
        
        request_data = mock.create()
        
        assert request_data.http_event_request.method == 'POST'
        assert request_data.http_event_request.path == '/api/users'
        assert request_data.http_event_response.status_code == 201
        assert request_data.http_event_info.client_city == 'London'
        assert request_data.http_event_info.client_country == 'UK'
        assert request_data.http_event_info.client_ip == '192.168.1.1'
    
    def test_mock_with_traces(self):
        """Test mock with execution traces"""
        mock = Mock_Obj__Fast_API__Request_Data()
        mock.path = '/debug'
        
        request_data = mock.create()
        
        # Add trace data
        request_data.http_event_traces.traces.append({
            'function': 'process_request',
            'duration': 0.005
        })
        
        assert len(request_data.http_event_traces.traces) == 1
        assert request_data.http_event_traces.traces[0]['duration'] == 0.005
```

## 🚀 Performance Testing Patterns

### Benchmarking with capture_duration

```python
from osbot_utils.helpers.duration.decorators.capture_duration import capture_duration

class test_Performance(TestCase):
    """Performance testing patterns"""
    
    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            cls.fast_api = _.fast_api
    
    def test_initialization_performance(self):
        """Test Fast_API initialization is fast"""
        with capture_duration() as duration:
            # This should use cached instance
            with setup__service_fast_api_test_objs() as _:
                pass
        
        # Should be near instant due to singleton
        assert duration.seconds < 0.001
    
    def test_endpoint_performance(self):
        """Test endpoint response times"""
        with capture_duration() as duration:
            response = self.client.get('/health')
        
        assert response.status_code == 200
        assert duration.seconds < 0.010  # Under 10ms
    
    def test_type_conversion_performance(self):
        """Test Type_Safe conversion performance"""
        large_data = {
            'items': [{'id': i, 'name': f'item_{i}'} for i in range(1000)]
        }
        
        with capture_duration() as duration:
            response = self.client.post('/bulk-process', json=large_data)
        
        assert response.status_code == 200
        assert duration.seconds < 0.500  # Process 1000 items under 500ms
    
    def test_concurrent_performance(self):
        """Test performance under concurrent load"""
        import concurrent.futures
        
        def make_request(i):
            return self.client.get(f'/item/{i}')
        
        with capture_duration() as duration:
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(make_request, i) for i in range(100)]
                responses = [f.result() for f in futures]
        
        assert all(r.status_code in [200, 404] for r in responses)
        assert duration.seconds < 2.0  # 100 concurrent requests under 2 seconds
```

## 🔍 Edge Case Testing

### Testing Error Conditions

```python
class test_Edge_Cases(TestCase):
    """Test edge cases and error conditions"""
    
    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client
    
    def test_empty_payloads(self):
        """Test various empty payloads"""
        test_cases = [
            ({}, 'empty dict'),
            ([], 'empty list'),
            ('', 'empty string'),
            (None, 'none value'),
        ]
        
        for payload, description in test_cases:
            with self.subTest(case=description):
                response = self.client.post('/process', json=payload)
                # Should handle gracefully
                assert response.status_code in [200, 400, 422]
    
    def test_large_payloads(self):
        """Test large payload handling"""
        # 10MB of data
        large_string = 'x' * (10 * 1024 * 1024)
        response = self.client.post('/process', json={'data': large_string})
        
        # Should handle or reject gracefully
        assert response.status_code in [200, 413, 422]
    
    def test_special_characters(self):
        """Test special character handling"""
        special_chars = [
            "'; DROP TABLE users; --",  # SQL injection attempt
            "<script>alert('XSS')</script>",  # XSS attempt
            "../../etc/passwd",  # Path traversal
            "\x00\x01\x02",  # Null bytes
            "🔥💀👻",  # Unicode/emoji
        ]
        
        for chars in special_chars:
            with self.subTest(chars=chars[:20]):
                response = self.client.post('/process', json={'input': chars})
                # Should sanitize or reject
                assert response.status_code in [200, 400, 422]
    
    def test_timeout_handling(self):
        """Test timeout scenarios"""
        from requests import ReadTimeout
        import pytest
        
        # Use Fast_API_Server for real timeout testing
        from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server
        
        with Fast_API_Server(app=self.client.app) as server:
            with pytest.raises(ReadTimeout):
                server.requests_get('/slow-endpoint', timeout=0.001)
```

## 📊 Coverage Testing Patterns

### Ensuring Complete Coverage

```python
class test_Coverage_Patterns(TestCase):
    """Patterns for achieving high test coverage"""
    
    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.fast_api = _.fast_api
            cls.client = _.fast_api__client
    
    def test_all_routes_accessible(self):
        """Test all configured routes are accessible"""
        all_routes = self.fast_api.routes_paths()
        untested_routes = []
        
        for route in all_routes:
            # Skip parametrized routes
            if '{' in route:
                continue
            
            # Try GET first, then POST
            response = self.client.get(route)
            if response.status_code == 405:  # Method not allowed
                response = self.client.post(route, json={})
            
            if response.status_code == 404:
                untested_routes.append(route)
        
        assert not untested_routes, f"Untested routes: {untested_routes}"
    
    def test_all_http_methods(self):
        """Test all HTTP methods on endpoints"""
        methods = ['get', 'post', 'put', 'delete', 'patch']
        endpoint = '/test-endpoint'
        
        results = {}
        for method in methods:
            client_method = getattr(self.client, method)
            response = client_method(endpoint, json={} if method != 'get' else None)
            results[method] = response.status_code
        
        # At least one method should work
        assert any(code < 400 for code in results.values())
        
        # 405 for unsupported methods
        assert all(code in [200, 201, 204, 405, 404] for code in results.values())
```

## 🧪 Integration Testing Patterns

### Testing with External Services

```python
from osbot_local_stack.local_stack.Local_Stack import Local_Stack
from osbot_aws.testing.Temp__Random__AWS_Credentials import Temp_AWS_Credentials

class test_AWS_Integration(TestCase):
    """Test AWS service integration"""
    
    @classmethod
    def setUpClass(cls):
        # Setup LocalStack for AWS mocking
        Temp_AWS_Credentials().with_localstack_credentials()
        cls.local_stack = Local_Stack().activate()
        
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client
    
    @classmethod
    def tearDownClass(cls):
        cls.local_stack.deactivate()
    
    def test_s3_integration(self):
        """Test S3 operations"""
        # Upload file
        response = self.client.post('/upload', files={
            'file': ('test.txt', b'test content', 'text/plain')
        })
        assert response.status_code == 200
        file_id = response.json()['file_id']
        
        # Download file
        response = self.client.get(f'/download/{file_id}')
        assert response.status_code == 200
        assert response.content == b'test content'
    
    def test_lambda_integration(self):
        """Test Lambda function invocation"""
        response = self.client.post('/invoke-lambda', json={
            'function_name': 'test-function',
            'payload': {'key': 'value'}
        })
        assert response.status_code == 200
```

## 🔄 Regression Testing

### Preventing Regression Bugs

```python
class test_Regression_Cases(TestCase):
    """Test cases for known regression issues"""
    
    def test_regression__type_safe_list_conversion(self):
        """Regression: Type_Safe__List not converting properly"""
        class ItemList(Type_Safe):
            items: list[str]
        
        data = ItemList(items=['a', 'b', 'c'])
        base_model = type_safe__to__basemodel.convert_instance(data)
        
        # Should maintain list type
        assert isinstance(base_model.items, list)
        assert base_model.items == ['a', 'b', 'c']
    
    def test_regression__nested_optional_fields(self):
        """Regression: Nested optional fields causing errors"""
        class Nested(Type_Safe):
            value: str = None
        
        class Parent(Type_Safe):
            nested: Nested = None
        
        # Should handle None gracefully
        parent = Parent()
        assert parent.nested is None
        
        parent = Parent(nested=Nested(value='test'))
        assert parent.nested.value == 'test'
    
    def test_regression__special_chars_in_path_params(self):
        """Regression: Special characters in path parameters"""
        test_ids = [
            'simple-id',
            'id-with-dash',
            'id_with_underscore',
            'id.with.dots',
        ]
        
        for test_id in test_ids:
            with self.subTest(id=test_id):
                response = self.client.get(f'/item/{test_id}')
                assert response.status_code in [200, 404]
```

## 🎯 Best Practices Summary

1. **Always use singleton pattern** for Fast_API instances
2. **Test at the right level** - direct > client > HTTP server
3. **Capture performance metrics** in tests
4. **Test edge cases systematically**
5. **Maintain regression test suite**
6. **Mock external dependencies**
7. **Test all configured routes**
8. **Verify type conversions**
9. **Test middleware behavior**
10. **Include security testing**