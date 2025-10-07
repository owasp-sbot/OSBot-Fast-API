from unittest                                                import TestCase
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs


class test_Routes__Admin__Config__client(TestCase):         # Test Routes__Admin__Config via TestClient

    @classmethod
    def setUpClass(cls):
        """Setup with client"""
        cls.test_objs = setup__admin_ui_test_objs(with_parent=True)
        cls.client = cls.test_objs.admin_client

    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_get_routes(self):
        """Test GET /api/routes"""
        response = self.client.get('/admin-config/api/routes')

        assert response.status_code == 200
        routes = response.json()

        assert isinstance(routes, list)
        assert len(routes) > 0

        # Verify route structure
        for route in routes:
            required_fields = ['path', 'methods', 'name', 'tag',
                             'is_get', 'is_post', 'is_put', 'is_delete']
            for field in required_fields:
                assert field in route, f"Missing field: {field}"

        # Check for specific routes
        paths = [r['path'] for r in routes]
        assert any('/test/hello' in p for p in paths)
        assert any('/config/status' in p for p in paths)

    def test_02_get_routes_grouped(self):
        """Test GET /api/routes-grouped"""
        response = self.client.get('/admin-config/api/routes-grouped')

        assert response.status_code == 200
        grouped = response.json()

        assert isinstance(grouped, dict)

        # Each group should have routes
        for tag, routes in grouped.items():
            assert isinstance(routes, list)
            assert len(routes) > 0

            # Verify all routes in group have same tag
            for route in routes:
                assert route['tag'] == tag

        # Should have multiple groups
        assert len(grouped) > 1

        # Check specific groups exist
        if 'test' in grouped:
            test_routes = grouped['test']
            test_paths = [r['path'] for r in test_routes]
            assert any('/test/hello' in p for p in test_paths)

    def test_03_get_middlewares(self):
        """Test GET /api/middlewares"""
        response = self.client.get('/admin-config/api/middlewares')

        assert response.status_code == 200
        middlewares = response.json()

        assert isinstance(middlewares, list)
        assert len(middlewares) > 0

        # Check middleware structure
        for mw in middlewares:
            assert 'type'          in mw
            assert 'function_name' in mw

        # Check for expected middlewares
        mw_types = [m['type'] for m in middlewares]
        assert 'Middleware__Detect_Disconnect' in mw_types
        assert 'Middleware__Http_Request' in mw_types

        # If CORS is enabled
        if 'CORSMiddleware' in mw_types:
            cors_mw = next(m for m in middlewares if m['type'] == 'CORSMiddleware')
            assert cors_mw == {'type': 'CORSMiddleware', 'function_name': None}

    def test_04_get_openapi_spec(self):
        """Test GET /api/openapi-spec"""
        response = self.client.get('/admin-config/api/openapi-spec')

        assert response.status_code == 200
        spec = response.json()

        # Verify OpenAPI structure
        assert 'openapi' in spec
        assert 'info' in spec
        assert 'paths' in spec

        # Check version
        assert spec['openapi'].startswith('3.')

        # Check info
        assert spec['info']['title'  ] == 'Test Parent API'
        assert spec['info']['version'] == 'v1.0.99'

        # Check paths exist
        assert len(spec['paths']) > 0

        # Check for test endpoints in spec
        test_paths = [p for p in spec['paths'] if '/test' in p]
        assert len(test_paths) > 0

        # Verify path structure
        if '/test/hello' in spec['paths']:
            hello_path = spec['paths']['/test/hello']
            assert 'get' in hello_path
            assert 'responses' in hello_path['get']

    def test_05_routes_method_filtering(self):
        """Test that route methods are correctly identified"""
        response = self.client.get('/admin-config/api/routes')
        routes = response.json()

        # Find routes with different methods
        get_routes    = [r for r in routes if r['is_get'    ]]
        post_routes   = [r for r in routes if r['is_post'   ]]
        put_routes    = [r for r in routes if r['is_put'    ]]
        delete_routes = [r for r in routes if r['is_delete' ]]

        # Should have GET routes
        assert len(get_routes) > 0

        # Test routes should be categorized correctly
        hello_route = next((r for r in routes if r['path'] == '/test/hello'), None)
        if hello_route:
            assert hello_route['is_get'] is True
            assert hello_route['is_post'] is False

        items_route = next((r for r in routes if r['path'] == '/test/items'), None)
        if items_route:
            assert items_route['is_post'] is True

        # If we have update/delete test routes
        update_route = next((r for r in routes if '/test/update' in r['path']), None)
        if update_route:
            assert update_route['is_put'] is True

        delete_route = next((r for r in routes if '/test/delete' in r['path']), None)
        if delete_route:
            assert delete_route['is_delete'] is True

    def test_06_routes_tag_accuracy(self):
        """Test that tags are correctly extracted"""
        response = self.client.get('/admin-config/api/routes-grouped')
        grouped = response.json()

        # Check tag extraction logic
        for tag, routes in grouped.items():
            for route in routes:
                path = route['path']

                # Verify tag matches path prefix
                if path == '/':
                    assert tag == 'root'
                elif path.startswith(f'/{tag}/'):
                    pass  # Correct
                elif '/' in path[1:]:
                    # Multi-segment path
                    first_segment = path.split('/')[1]
                    assert tag == first_segment