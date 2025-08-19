from unittest                                                import TestCase
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs


class test_Admin_UI__Fast_API__client(TestCase):                                    # Test Admin UI with TestClient

    @classmethod
    def setUpClass(cls):                                                            # Setup test client"""
        cls.test_objs = setup__admin_ui_test_objs(with_parent=True)
        cls.client = cls.test_objs.admin_client

    @classmethod
    def tearDownClass(cls):     # Cleanup"""
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_index_page(self):                           # Test index HTML page
        response = self.client.get('/admin-static/index')

        assert response.status_code == 200
        assert 'text/html' in response.headers['content-type']

        # Check for expected HTML content
        html = response.text
        assert '<!DOCTYPE html>'                 in html
        assert '<title>FastAPI Admin UI</title>' in html
        assert 'admin_ui.js'                     in html
        assert 'navigation.js'                   in html

    def test_02_static_css(self):                                                   # Test CSS file serving
        response = self.client.get('/admin-static/serve-css/base.css')

        assert response.status_code == 200                                          # Should return CSS
        assert 'text/css'           in response.headers['content-type']
        assert "/* Base CSS - Core" in response.text                                # todo: check this test to confirm that this matches the file in osbot_fast_api/admin_ui/static/css/base.css

    def test_03_static_js(self):                                                    # Test JavaScript file serving
        response = self.client.get('/admin-static/serve-js/admin_ui.js')

        assert response.status_code        == 200
        assert 'application/javascript'    in response.headers['content-type']
        assert "Main Admin UI Application" in response.text                         # todo: check this test to confirm that this matches the file in osbot_fast_api/admin_ui/static/js/admin_ui.js

    def test_04_api_health(self):                                                   # Test health check endpoint
        response = self.client.get('/admin-info/api/health')
        data     = response.json()

        assert response.status_code == 200
        assert data['status']       == 'Ok'
        assert 'timestamp'          in data

    def test_05_api_server_info(self):                                              # Test server info endpoint"""
        response = self.client.get('/admin-info/api/server-info')
        data     = response.json()

        assert response.status_code == 200

        assert 'server_id'          in data                                         # Check expected fields
        assert 'server_name'        in data
        assert 'server_instance_id' in data
        assert 'server_boot_time'   in data
        assert 'current_time'       in data
        assert 'uptime_ms'          in data

        assert isinstance(data['uptime_ms'], int)                                   # Verify data types
        assert data['uptime_ms'] >= 0

    def test_06_api_app_info(self):                                                 # Test app info endpoint
        response = self.client.get('/admin-info/api/app-info')

        assert response.status_code == 200
        data = response.json()

        assert data['name'          ] == 'Test Parent API'                          # Check expected fields
        assert data['version'       ] == 'v1.0.99'
        assert data['description'   ] == 'Parent API for Admin UI testing'
        assert data['base_path'     ] == '/'
        assert data['docs_offline'  ] is True
        assert data['enable_cors'   ] is True
        assert data['enable_api_key'] is False
