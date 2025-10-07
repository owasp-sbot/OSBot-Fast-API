import time
from unittest                                                import TestCase
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs


class test_Routes__Admin__Info__http(TestCase):             # Test Routes__Admin__Info with HTTP server

    @classmethod
    def setUpClass(cls):
        """Setup with HTTP server"""
        cls.test_objs = setup__admin_ui_test_objs(
            with_parent=True,
            with_server=True
        )
        cls.server = cls.test_objs.admin_server

    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_server_info_via_http(self):
        """Test server info endpoint via HTTP"""
        response = self.server.requests_get('/admin-info/api/server-info')

        assert response.status_code == 200
        data = response.json()

        # Verify server is reporting correct info
        assert 'server_id' in data
        assert 'uptime_ms' in data
        assert data['uptime_ms'] > 0

    def test_02_concurrent_stats_requests(self):
        """Test concurrent stats requests"""
        import concurrent.futures

        def get_stats():
            return self.server.requests_get('/admin-info/api/stats')

        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(get_stats) for _ in range(10)]
            results = [f.result() for f in futures]

        # All should succeed
        assert all(r.status_code == 200 for r in results)

        # All should return same stats (approximately)
        stats_list = [r.json() for r in results]
        first_total = stats_list[0]['total_routes']

        # All should have same route count
        assert all(s['total_routes'] == first_total for s in stats_list)

    def test_03_uptime_increases(self):
        """Test that uptime increases over time"""
        # Get initial uptime
        response1 = self.server.requests_get('/admin-info/api/server-info')
        uptime1 = response1.json()['uptime_ms']

        # Wait a bit
        time.sleep(0.01)

        # Get new uptime
        response2 = self.server.requests_get('/admin-info/api/server-info')
        uptime2 = response2.json()['uptime_ms']

        # Uptime should have increased
        assert uptime2 > uptime1
        assert (uptime2 - uptime1) >= 10  # At least 10ms difference