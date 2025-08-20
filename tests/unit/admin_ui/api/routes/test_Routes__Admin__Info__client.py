from unittest                                                import TestCase
from osbot_utils.utils.Misc                                  import timestamp_utc_now
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs


class test_Routes__Admin__Info__client(TestCase):                   # Test Routes__Admin__Info via TestClient"""

    @classmethod
    def setUpClass(cls):
        """Setup with client"""
        cls.test_objs = setup__admin_ui_test_objs(with_parent=True)
        cls.client = cls.test_objs.admin_client
        cls.start_time = timestamp_utc_now()

    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_get_server_info(self):
        """Test GET /api/server-info"""
        response = self.client.get('/admin-info/api/server-info')
        assert response.status_code == 200
        data = response.json()

        # Verify all fields present
        required_fields = [
            'server_id',
            'server_name',
            'server_instance_id',
            'server_boot_time',
            'current_time',
            'uptime_ms'
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Verify uptime is reasonable
        assert data['uptime_ms'] >= 0
        assert data['uptime_ms'] < 3600000  # Less than 1 hour for test

    def test_02_get_app_info(self):
        """Test GET /api/app-info"""
        response = self.client.get('/admin-info/api/app-info')

        assert response.status_code == 200
        data = response.json()

        # Verify response matches parent app config
        assert data['name'          ] == 'Test Parent API'
        assert data['version'       ] == 'v1.0.99'
        assert data['enable_cors'   ] is True
        assert data['enable_api_key'] is False

    def test_03_get_stats(self):
        """Test GET /api/stats"""
        response = self.client.get('/admin-info/api/stats')

        assert response.status_code == 200
        data = response.json()

        # Verify stats structure
        assert data['total_routes'] > 0

        # Check methods breakdown
        assert 'GET' in data['methods']
        assert 'POST' in data['methods']
        assert data['methods']['GET'] >= data['methods']['POST']

        # Check prefixes
        assert isinstance(data['prefixes'], dict)
        assert len(data['prefixes']) > 0

    def test_04_get_health(self):
        """Test GET /api/health"""
        response = self.client.get('/admin-info/api/health')

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'Ok'
        assert 'timestamp' in data

        # Verify timestamp format and value
        timestamp = int(data['timestamp'])
        assert timestamp > self.start_time
        assert timestamp < timestamp_utc_now() + 1000

    def test_05_health_check_performance(self):
        """Test health check is fast"""
        import time

        # Warm up
        self.client.get('/admin-info/api/health')

        # Measure time for multiple requests
        start = time.time()
        num_requests = 10

        for _ in range(num_requests):
            response = self.client.get('/admin-info/api/health')
            assert response.status_code == 200

        duration = time.time() - start
        avg_time = duration / num_requests

        # Health check should be very fast
        assert avg_time < 0.01  # Less than 10ms average

    def test_06_stats_accuracy(self):
        """Test that stats accurately reflect routes"""
        response = self.client.get('/admin-info/api/stats')
        stats = response.json()

        # Get actual routes from parent
        parent_routes = self.test_objs.parent_fast_api.routes()

        # Count methods manually
        method_count = {}
        for route in parent_routes:
            for method in route.get('http_methods', []):
                method_count[method] = method_count.get(method, 0) + 1

        # Stats should match (approximately - admin routes might be included)
        assert stats['methods']['GET'] >= method_count.get('GET', 0)
        assert stats['methods']['POST'] >= method_count.get('POST', 0)

