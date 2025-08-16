# OSBot-Fast-API Comprehensive Testing Guide

## 📋 Overview

This guide documents the comprehensive testing philosophy, patterns, and techniques used in OSBot-Fast-API. The testing architecture validates functionality from multiple angles, ensuring robust code quality through unit, integration, and system testing.

## 🏗️ Testing Architecture

### Directory Structure

```
tests/
├── unit/                          # Isolated component testing
│   ├── api/                       # Core API components
│   │   ├── middlewares/           # Middleware unit tests
│   │   ├── routes/                # Route handler tests
│   │   └── test_Fast_API.py       # Main API wrapper tests
│   ├── utils/                     # Utility function tests
│   │   ├── type_safe/             # Type conversion tests
│   │   └── testing/               # Test utility tests
│   ├── examples/                  # Example implementation tests
│   └── fast_api__for_tests.py     # Shared test fixtures (singleton)
├── integration/                   # Component interaction testing
│   ├── api/                       # API integration tests
│   └── utils/                     # Utility integration tests
└── requirements-unit.txt          # Test dependencies
```

### Test Categories

| Category | Purpose | Location | Coverage Target |
|----------|---------|----------|-----------------|
| **Unit Tests** | Test individual components in isolation | `/tests/unit/` | 100% |
| **Integration Tests** | Test component interactions | `/tests/integration/` | Critical paths |
| **QA Tests** | Test deployed services | `/tests/qa/` | Production endpoints |
| **Performance Tests** | Benchmark performance | Embedded in tests | Key operations |

## 🎯 Core Testing Patterns

### 1. Singleton Test Fixtures

**Pattern**: Create shared test fixtures to avoid repeated initialization overhead.

**Implementation**: `/tests/unit/fast_api__for_tests.py`

```python
from osbot_utils.helpers.duration.decorators.capture_duration import capture_duration
from osbot_fast_api.api.Fast_API import Fast_API

# Singleton pattern for test performance
with capture_duration() as duration:
    fast_api        = Fast_API().setup()
    fast_api_client = fast_api.client()

# Performance assertion
if in_github_action() is False:
    assert duration.seconds < 0.1  # Ensure fast initialization
```

**Benefits**:
- ✅ Reduces test execution time by ~90%
- ✅ Shared state for read-only tests
- ✅ Consistent test environment
- ✅ Performance benchmarking built-in

### 2. Multi-Angle Testing

**Pattern**: Test each component from multiple perspectives to ensure complete coverage.

#### Angle 1: Internal State Testing
```python
def test__init__(self):
    """Test internal state and initialization"""
    assert self.fast_api.enable_cors is False
    assert type(self.fast_api.app()) is FastAPI
    assert self.fast_api.server_id is not None
```

#### Angle 2: HTTP Client Testing
```python
def test_client__endpoint(self):
    """Test through HTTP client interface"""
    response = self.client.get('/endpoint')
    assert response.status_code == 200
    assert response.json() == expected_data
```

#### Angle 3: Behavioral Testing
```python
def test_behavior__redirect(self):
    """Test behavioral patterns"""
    response = self.client.get('/', follow_redirects=False)
    assert response.status_code == 307
    assert response.headers.get('location') == '/docs'
```

#### Angle 4: Integration Testing
```python
def test_integration__full_flow(self):
    """Test complete workflow"""
    # Create resource
    create_response = self.client.post('/resource', json=data)
    resource_id = create_response.json()['id']
    
    # Retrieve resource
    get_response = self.client.get(f'/resource/{resource_id}')
    assert get_response.json()['id'] == resource_id
```

### 3. Context Manager Testing

**Pattern**: Use context managers for clean setup/teardown of test resources.

```python
class test_Fast_API_Server(TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test server once for all tests"""
        cls.fast_api_server = Fast_API_Server(app=cls.fast_api.app())
        cls.fast_api_server.start()
        assert cls.fast_api_server.is_port_open() is True

    @classmethod
    def tearDownClass(cls):
        """Clean shutdown of test server"""
        cls.fast_api_server.stop()
        assert cls.fast_api_server.is_port_open() is False

    def test_with_context_manager(self):
        """Alternative context manager pattern"""
        with Fast_API_Server() as server:
            response = server.requests_get('/ping')
            assert response.json() == 'pong'
```

### 4. Progressive Complexity Testing

**Pattern**: Build tests from simple to complex, each building on previous validations.

```python
class test_Type_Safe_Routes(TestCase):
    def test__1__simple_get(self):
        """Basic GET request"""
        assert self.client.get('/ping').json() == 'pong'
    
    def test__2__post_with_json(self):
        """POST with JSON payload"""
        data = {'key': 'value'}
        assert self.client.post('/data', json=data).json() == data
    
    def test__3__complex_type_conversion(self):
        """Complex Type_Safe conversion"""
        complex_data = {
            'user': {'name': 'Alice', 'age': 30},
            'addresses': [{'street': '123 Main', 'city': 'NYC'}]
        }
        response = self.client.post('/complex', json=complex_data)
        assert response.status_code == 200
    
    def test__4__full_workflow(self):
        """Complete multi-step workflow"""
        # Step 1: Create
        # Step 2: Update
        # Step 3: Verify
        # Step 4: Delete
```

## 🔬 Testing Techniques

### 1. Type Conversion Round-Trip Testing

**Technique**: Validate bidirectional type conversions maintain data integrity.

```python
def test__round_trip_conversion(self):
    """Test Type_Safe → BaseModel → Type_Safe conversion"""
    # Create original Type_Safe instance
    original = UserClass(name="Alice", age=30)
    
    # Convert to BaseModel
    base_model = type_safe__to__basemodel.convert_instance(original)
    
    # Convert back to Type_Safe
    recovered = basemodel__to__type_safe.convert_instance(base_model)
    
    # Verify data integrity
    assert original.json() == recovered.json()
    
    # Test nested structures
    nested_original = ComplexClass(user=original, tags=['a', 'b'])
    nested_model = type_safe__to__basemodel.convert_instance(nested_original)
    nested_recovered = basemodel__to__type_safe.convert_instance(nested_model)
    assert nested_original.json() == nested_recovered.json()
```

### 2. Edge Case Matrix Testing

**Technique**: Systematically test boundary conditions and edge cases.

```python
class test_Edge_Cases(TestCase):
    def test_empty_values(self):
        """Test empty collections and None values"""
        test_cases = [
            ({}, {}),                          # Empty dict
            ([], []),                          # Empty list
            (None, None),                      # None value
            ('', ''),                          # Empty string
            ({'key': None}, {'key': None}),   # None in dict
        ]
        
        for input_data, expected in test_cases:
            response = self.client.post('/echo', json=input_data)
            assert response.json() == expected
    
    def test_boundary_values(self):
        """Test boundary conditions"""
        test_cases = [
            (0, 'zero'),
            (-1, 'negative'),
            (sys.maxsize, 'max_int'),
            (0.0, 'zero_float'),
            (float('inf'), 'infinity'),
        ]
        
        for value, case_name in test_cases:
            with self.subTest(case=case_name):
                response = self.client.post('/process', json={'value': value})
                self.assertEqual(response.status_code, 200)
```

### 3. Error Injection Testing

**Technique**: Deliberately trigger errors to test error handling.

```python
def test_error_handling(self):
    """Test error handling at different levels"""
    
    # Validation error
    response = self.client.post('/user', json={'age': 'not_a_number'})
    assert response.status_code == 422
    assert 'validation error' in response.json()['detail'][0]['msg'].lower()
    
    # Business logic error
    response = self.client.post('/divide', json={'a': 10, 'b': 0})
    assert response.status_code == 400
    assert 'division by zero' in response.json()['detail'].lower()
    
    # Authentication error
    response = self.client.get('/protected')
    assert response.status_code == 401
    
    # Not found error
    response = self.client.get('/user/99999')
    assert response.status_code == 404
```

### 4. Middleware Chain Testing

**Technique**: Test middleware execution order and interactions.

```python
def test_middleware_chain(self):
    """Test middleware pipeline execution"""
    
    # Track middleware execution
    execution_order = []
    
    class TrackingMiddleware:
        def __init__(self, name):
            self.name = name
        
        async def __call__(self, request, call_next):
            execution_order.append(f'{self.name}_start')
            response = await call_next(request)
            execution_order.append(f'{self.name}_end')
            return response
    
    # Add middleware in order
    app.add_middleware(TrackingMiddleware('A'))
    app.add_middleware(TrackingMiddleware('B'))
    app.add_middleware(TrackingMiddleware('C'))
    
    # Make request
    response = client.get('/test')
    
    # Verify LIFO execution
    assert execution_order == [
        'C_start', 'B_start', 'A_start',
        'A_end', 'B_end', 'C_end'
    ]
```

### 5. Performance Benchmarking

**Technique**: Embed performance assertions in tests.

```python
from osbot_utils.helpers.duration.decorators.capture_duration import capture_duration

def test_performance(self):
    """Test operation performance"""
    
    # Single operation
    with capture_duration() as duration:
        response = self.client.get('/fast-endpoint')
    assert duration.seconds < 0.010  # Must respond in < 10ms
    
    # Bulk operations
    with capture_duration() as duration:
        for i in range(100):
            self.client.get(f'/item/{i}')
    assert duration.seconds < 1.0  # 100 requests in < 1 second
    
    # Type conversion performance
    large_data = {'items': [{'id': i} for i in range(1000)]}
    with capture_duration() as duration:
        response = self.client.post('/process', json=large_data)
    assert duration.seconds < 0.100  # Process 1000 items in < 100ms
```

### 6. State Isolation Testing

**Technique**: Ensure tests don't affect each other.

```python
class test_State_Isolation(TestCase):
    def setUp(self):
        """Fresh state for each test"""
        self.fast_api = Fast_API().setup()
        self.client = self.fast_api.client()
    
    def tearDown(self):
        """Clean up after each test"""
        # Clear any global state
        self.fast_api.http_events.requests_data.clear()
        self.fast_api.http_events.requests_order.clear()
    
    def test_independent_1(self):
        """Test that doesn't affect others"""
        self.client.post('/data', json={'test': 1})
        assert len(self.fast_api.http_events.requests_data) == 1
    
    def test_independent_2(self):
        """Test with clean state"""
        # Should start with empty events
        assert len(self.fast_api.http_events.requests_data) == 0
```

## 📊 Test Coverage Strategies

### 1. Path Coverage
```python
def test_all_route_paths(self):
    """Ensure all routes are tested"""
    tested_paths = set()
    
    for route in self.fast_api.routes():
        path = route['http_path']
        tested_paths.add(path)
        
        # Test each HTTP method
        for method in route['http_methods']:
            response = getattr(self.client, method.lower())(path)
            assert response.status_code in [200, 201, 204, 307, 405]
    
    # Verify coverage
    all_paths = set(self.fast_api.routes_paths())
    untested = all_paths - tested_paths
    assert not untested, f"Untested paths: {untested}"
```

### 2. Type Coverage
```python
def test_type_conversions(self):
    """Test all type conversion combinations"""
    type_combinations = [
        (Type_Safe, BaseModel),
        (BaseModel, Type_Safe),
        (Type_Safe, dataclass),
        (dataclass, Type_Safe),
        (BaseModel, dataclass),
        (dataclass, BaseModel),
    ]
    
    for source_type, target_type in type_combinations:
        with self.subTest(f"{source_type.__name__} → {target_type.__name__}"):
            # Test conversion
            pass
```

## 🚀 Writing Tests for New Projects

### Test Template Structure

```python
from unittest import TestCase
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server


class test_MyFeature(TestCase):
    """Test suite for MyFeature"""

    @classmethod
    def setUpClass(cls):
        """One-time setup for all tests"""
        cls.fast_api = Fast_API().setup()
        cls.fast_api.add_routes(MyRoutes)
        cls.server = Fast_API_Server(app=cls.fast_api.app())
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        """One-time cleanup"""
        cls.server.stop()

    def setUp(self):
        """Setup for each test"""
        self.test_data = {'key': 'value'}

    def test_unit__component(self):
        """Unit test for component"""
        component = MyComponent()
        assert component.process(self.test_data) == expected

    def test_integration__workflow(self):
        """Integration test for workflow"""
        # Step 1: Create
        create_response = self.server.requests_post('/create', data=self.test_data)
        assert create_response.status_code == 201

        # Step 2: Verify
        get_response = self.server.requests_get(f'/get/{id}')
        assert get_response.json() == self.test_data

    def test_edge_case__empty_data(self):
        """Edge case test"""
        response = self.server.requests_post('/create', data={})
        assert response.status_code == 400
```

## 🎯 Best Practices

1. **Use Singleton Fixtures**: Share expensive setup across tests
2. **Test Multiple Angles**: Unit, integration, behavioral, performance
3. **Progressive Complexity**: Build from simple to complex tests
4. **Clean State**: Ensure test isolation
5. **Performance Assertions**: Include timing constraints
6. **Edge Case Coverage**: Test boundaries and error conditions
7. **Round-Trip Testing**: Verify bidirectional conversions
8. **Mock External Dependencies**: Isolate system under test
9. **Use Subtests**: For parametrized testing
10. **Document Test Purpose**: Clear test names and docstrings

## 📈 Metrics to Track

- **Code Coverage**: Target 100% for unit tests
- **Test Execution Time**: Keep under 10 seconds for unit tests
- **Test Stability**: Zero flaky tests
- **Edge Case Coverage**: Document and test all known edge cases
- **Performance Regression**: Track response times over time