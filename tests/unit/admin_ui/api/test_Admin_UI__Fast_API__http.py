import concurrent
from unittest                                                import TestCase
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs

class test_Admin_UI__Fast_API__http(TestCase):          # Test Admin UI with actual HTTP server

    @classmethod
    def setUpClass(cls):                                # Setup with HTTP server
        cls.test_objs = setup__admin_ui_test_objs(with_parent=True,
                                                  with_server=True)
        cls.server = cls.test_objs.admin_server

    @classmethod
    def tearDownClass(cls):                             # Stop server and cleanup
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_server_running(self):                   # Verify server is running"""
        assert self.server is not None
        assert self.server.running is True
        assert self.server.is_port_open() is True

    def test_02_http_index(self):                       # Test index page via HTTP
        response = self.server.requests_get('/admin-static/index')      # todo: replace all these paths to const_* values

        assert response.status_code == 200
        assert 'text/html'          in response.headers['content-type']
        assert '<!DOCTYPE html>'    in response.text

    def test_03_http_api_stats(self):                                           #  Test stats endpoint via HTTP
        response = self.server.requests_get('/admin-info/api/stats')
        data     = response.json()

        assert response.status_code == 200
        assert 'total_routes'       in data                                     # Verify stats structure
        assert 'methods'            in data
        assert 'prefixes'           in data
        assert 'middlewares_count'  in data
        assert 'has_static_files'   in data


        assert data['total_routes'] > 0                                         # Check actual values
        assert 'GET' in data['methods']
        assert data['methods']['GET'] > 0

    def test_04_concurrent_requests(self):                                      # Test concurrent request handling

        def make_request():
            return self.server.requests_get('/admin-info/api/health')

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:     # Make concurrent requests
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in futures]

        assert all(r.status_code == 200 for r in results)                           # All should succeed
        assert all(r.json()['status'] == 'Ok' for r in results)


