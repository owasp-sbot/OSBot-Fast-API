from unittest                                                import TestCase
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs


class test_Routes__Admin__Docs__http(TestCase):
    """Test Routes__Admin__Docs with HTTP server"""

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

    def test_01_docs_endpoints_http(self):
        """Test docs endpoints via HTTP"""
        response = self.server.requests_get('/admin-docs/api/docs-endpoints')

        assert response.status_code == 200
        endpoints = response.json()

        # Verify we get all documentation endpoints
        assert len(endpoints) == 6

        # Check that URLs are accessible (at least the format is correct)
        for endpoint in endpoints:
            url = endpoint['url']
            assert url.startswith('/')

    def test_02_api_info_consistency(self):
        """Test API info consistency with actual routes"""
        # Get API info
        info_response = self.server.requests_get('/admin-docs/api/api-info')
        api_info = info_response.json()

        # Get actual routes
        routes_response = self.server.requests_get('/admin-config/api/routes')
        routes = routes_response.json()

        # Path count should be consistent
        # Note: api_info counts OpenAPI paths, routes counts actual routes
        assert api_info['total_paths'] > 0
        assert len(routes) > 0

        # Tags should reflect actual routes
        if len(api_info['tags']) > 0:
            tag_names = [t['name'] for t in api_info['tags']]
            route_tags = list(set(r['tag'] for r in routes))

            # Some overlap should exist
            overlap = set(tag_names) & set(route_tags)
            assert len(overlap) > 0