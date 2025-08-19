# import time
# from unittest                                               import TestCase
#
# from osbot_utils.utils.Dev import pprint
# from osbot_utils.utils.Misc import list_set
#
# from osbot_fast_api.admin_ui.api.routes.Routes__Admin__Info import Routes__Admin__Info
# from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, \
#     cleanup_admin_ui_test_objs
# from osbot_fast_api.api.routes.Fast_API__Routes             import Fast_API__Routes
# from osbot_utils.type_safe.Type_Safe                        import Type_Safe
# from osbot_utils.utils.Objects                              import base_types
#
# class test_Routes__Admin__Info(TestCase):                   # Test Routes__Admin__Info class directly
#
#     @classmethod
#     def setUpClass(cls):                                    # Setup routes instance
#         cls.test_objs = setup__admin_ui_test_objs(with_parent=True)
#         cls.routes_info = Routes__Admin__Info()
#         cls.routes_info.parent_app = cls.test_objs.parent_fast_api
#
#     @classmethod
#     def tearDownClass(cls):                                     # Cleanup
#         cleanup_admin_ui_test_objs(cls.test_objs)
#
#     def test_01_setUpClass(self):                               # Verify class setup and inheritance
#         with self.routes_info as _:
#             assert type(_)          is Routes__Admin__Info
#             assert Fast_API__Routes in base_types(_)
#             assert Type_Safe        in base_types(_)
#             assert _.tag            == 'admin-info'
#             assert _.parent_app     is not None
#
#     def test_02_api__server_info(self):                         # Test server info method directly
#         result = self.routes_info.api__server_info()
#
#         # Check structure
#         expected_fields = [ 'server_id'         ,
#                             'server_name'       ,
#                             'server_instance_id',
#                             'server_boot_time'  ,
#                             'current_time'      ,
#                             'uptime_ms'         ]
#         assert list_set(result.keys()) == sorted(expected_fields)
#
#         assert isinstance(result['server_id'         ], str)                 # Verify data types
#         assert isinstance(result['server_instance_id'], str)
#         assert isinstance(result['server_boot_time'  ], int)
#         assert isinstance(result['current_time'      ], int)
#         assert isinstance(result['uptime_ms'         ], int)
#
#         # Verify values
#         pprint(result)
#         assert len(result['server_id']) == 36  # UUID length
#         assert len(result['server_instance_id']) == 36
#         assert result['uptime_ms'] >= 0
#         assert result['current_time'] > result['server_boot_time']
#
#     def test_03_api__app_info(self):
#         """Test app info method directly"""
#         result = self.routes_info.api__app_info()
#
#         # Check structure
#         expected_fields = [
#             'name',
#             'version',
#             'description',
#             'base_path',
#             'docs_offline',
#             'enable_cors',
#             'enable_api_key'
#         ]
#         assert list_set(result.keys()) == expected_fields
#
#         # Verify values from parent app
#         assert result['name'] == 'Test Parent API'
#         assert result['version'] == '1.0.0-test'
#         assert result['description'] == 'Parent API for Admin UI testing'
#         assert result['base_path'] == '/'
#         assert result['docs_offline'] is True
#         assert result['enable_cors'] is True
#         assert result['enable_api_key'] is False
#
#     def test_04_api__app_info_no_parent(self):
#         """Test app info without parent app"""
#         routes = Routes__Admin__Info()
#         routes.parent_app = None
#
#         result = routes.api__app_info()
#
#         assert result == {"error": "Parent app not configured"}
#
#     def test_05_api__stats(self):
#         """Test stats method directly"""
#         result = self.routes_info.api__stats()
#
#         # Check structure
#         expected_fields = [
#             'total_routes',
#             'methods',
#             'prefixes',
#             'middlewares_count',
#             'has_static_files'
#         ]
#         assert list_set(result.keys()) == expected_fields
#
#         # Verify data types
#         assert isinstance(result['total_routes'], int)
#         assert isinstance(result['methods'], dict)
#         assert isinstance(result['prefixes'], dict)
#         assert isinstance(result['middlewares_count'], int)
#         assert isinstance(result['has_static_files'], bool)
#
#         # Verify values
#         assert result['total_routes'] > 0
#         assert 'GET' in result['methods']
#         assert result['methods']['GET'] > 0
#
#         # Check test routes are counted
#         assert '/test' in result['prefixes'] or '/test/hello' in str(result['prefixes'])
#
#     def test_06_api__stats_no_parent(self):
#         """Test stats without parent app"""
#         routes = Routes__Admin__Info()
#         routes.parent_app = None
#
#         result = routes.api__stats()
#
#         assert result == {"error": "Parent app not configured"}
#
#     def test_07_api__health(self):
#         """Test health check method"""
#         result = self.routes_info.api__health()
#
#         # Check structure
#         assert list_set(result.keys()) == ['status', 'timestamp']
#
#         # Verify values
#         assert result['status'] == 'healthy'
#         assert isinstance(result['timestamp'], str)
#
#         # Timestamp should be recent
#         timestamp = int(result['timestamp'])
#         now = timestamp_utc_now_ms()
#         assert abs(now - timestamp) < 1000  # Within 1 second
#
#     def test_08_routes_registration(self):
#         """Test that routes are properly registered"""
#         routes_instance = Routes__Admin__Info()
#         routes_instance.setup()
#
#         registered_routes = routes_instance.routes_paths()
#
#         # All API methods should be registered
#         assert '/api/server-info' in registered_routes
#         assert '/api/app-info' in registered_routes
#         assert '/api/stats' in registered_routes
#         assert '/api/health' in registered_routes
#
#
# class test_Routes__Admin__Info__client(TestCase):
#     """Test Routes__Admin__Info via TestClient"""
#
#     @classmethod
#     def setUpClass(cls):
#         """Setup with client"""
#         cls.test_objs = setup__admin_ui_test_objs(with_parent=True)
#         cls.client = cls.test_objs.admin_client
#         cls.start_time = timestamp_utc_now_ms()
#
#     @classmethod
#     def tearDownClass(cls):
#         """Cleanup"""
#         cleanup_admin_ui_test_objs(cls.test_objs)
#
#     def test_01_get_server_info(self):
#         """Test GET /api/server-info"""
#         response = self.client.get('/api/server-info')
#
#         assert response.status_code == 200
#         data = response.json()
#
#         # Verify all fields present
#         required_fields = [
#             'server_id',
#             'server_name',
#             'server_instance_id',
#             'server_boot_time',
#             'current_time',
#             'uptime_ms'
#         ]
#         for field in required_fields:
#             assert field in data, f"Missing field: {field}"
#
#         # Verify uptime is reasonable
#         assert data['uptime_ms'] >= 0
#         assert data['uptime_ms'] < 3600000  # Less than 1 hour for test
#
#     def test_02_get_app_info(self):
#         """Test GET /api/app-info"""
#         response = self.client.get('/api/app-info')
#
#         assert response.status_code == 200
#         data = response.json()
#
#         # Verify response matches parent app config
#         assert data['name'] == 'Test Parent API'
#         assert data['version'] == '1.0.0-test'
#         assert data['enable_cors'] is True
#         assert data['enable_api_key'] is False
#
#     def test_03_get_stats(self):
#         """Test GET /api/stats"""
#         response = self.client.get('/api/stats')
#
#         assert response.status_code == 200
#         data = response.json()
#
#         # Verify stats structure
#         assert data['total_routes'] > 0
#
#         # Check methods breakdown
#         assert 'GET' in data['methods']
#         assert 'POST' in data['methods']
#         assert data['methods']['GET'] >= data['methods']['POST']
#
#         # Check prefixes
#         assert isinstance(data['prefixes'], dict)
#         assert len(data['prefixes']) > 0
#
#     def test_04_get_health(self):
#         """Test GET /api/health"""
#         response = self.client.get('/api/health')
#
#         assert response.status_code == 200
#         data = response.json()
#
#         assert data['status'] == 'healthy'
#         assert 'timestamp' in data
#
#         # Verify timestamp format and value
#         timestamp = int(data['timestamp'])
#         assert timestamp > self.start_time
#         assert timestamp < timestamp_utc_now_ms() + 1000
#
#     def test_05_health_check_performance(self):
#         """Test health check is fast"""
#         import time
#
#         # Warm up
#         self.client.get('/api/health')
#
#         # Measure time for multiple requests
#         start = time.time()
#         num_requests = 10
#
#         for _ in range(num_requests):
#             response = self.client.get('/api/health')
#             assert response.status_code == 200
#
#         duration = time.time() - start
#         avg_time = duration / num_requests
#
#         # Health check should be very fast
#         assert avg_time < 0.01  # Less than 10ms average
#
#     def test_06_stats_accuracy(self):
#         """Test that stats accurately reflect routes"""
#         response = self.client.get('/api/stats')
#         stats = response.json()
#
#         # Get actual routes from parent
#         parent_routes = self.test_objs.parent_fast_api.routes()
#
#         # Count methods manually
#         method_count = {}
#         for route in parent_routes:
#             for method in route.get('http_methods', []):
#                 method_count[method] = method_count.get(method, 0) + 1
#
#         # Stats should match (approximately - admin routes might be included)
#         assert stats['methods']['GET'] >= method_count.get('GET', 0)
#         assert stats['methods']['POST'] >= method_count.get('POST', 0)
#
#
# class test_Routes__Admin__Info__http(TestCase):
#     """Test Routes__Admin__Info with HTTP server"""
#
#     @classmethod
#     def setUpClass(cls):
#         """Setup with HTTP server"""
#         cls.test_objs = setup__admin_ui_test_objs(
#             with_parent=True,
#             with_server=True
#         )
#         cls.server = cls.test_objs.admin_server
#
#     @classmethod
#     def tearDownClass(cls):
#         """Cleanup"""
#         cleanup_admin_ui_test_objs(cls.test_objs)
#
#     def test_01_server_info_via_http(self):
#         """Test server info endpoint via HTTP"""
#         response = self.server.requests_get('/api/server-info')
#
#         assert response.status_code == 200
#         data = response.json()
#
#         # Verify server is reporting correct info
#         assert 'server_id' in data
#         assert 'uptime_ms' in data
#         assert data['uptime_ms'] > 0
#
#     def test_02_concurrent_stats_requests(self):
#         """Test concurrent stats requests"""
#         import concurrent.futures
#
#         def get_stats():
#             return self.server.requests_get('/api/stats')
#
#         # Make concurrent requests
#         with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#             futures = [executor.submit(get_stats) for _ in range(10)]
#             results = [f.result() for f in futures]
#
#         # All should succeed
#         assert all(r.status_code == 200 for r in results)
#
#         # All should return same stats (approximately)
#         stats_list = [r.json() for r in results]
#         first_total = stats_list[0]['total_routes']
#
#         # All should have same route count
#         assert all(s['total_routes'] == first_total for s in stats_list)
#
#     def test_03_uptime_increases(self):
#         """Test that uptime increases over time"""
#         # Get initial uptime
#         response1 = self.server.requests_get('/api/server-info')
#         uptime1 = response1.json()['uptime_ms']
#
#         # Wait a bit
#         time.sleep(0.1)
#
#         # Get new uptime
#         response2 = self.server.requests_get('/api/server-info')
#         uptime2 = response2.json()['uptime_ms']
#
#         # Uptime should have increased
#         assert uptime2 > uptime1
#         assert (uptime2 - uptime1) >= 100  # At least 100ms difference