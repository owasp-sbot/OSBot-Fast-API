from unittest                                                   import TestCase
from osbot_fast_api.admin_ui.api.routes.Routes__Admin__Config   import Routes__Admin__Config
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs    import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs
from osbot_fast_api.api.routes.Fast_API__Routes                 import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                            import Type_Safe
from osbot_utils.utils.Objects                                  import base_types


class test_Routes__Admin__Config(TestCase):
    """Test Routes__Admin__Config class directly"""

    @classmethod
    def setUpClass(cls):
        """Setup routes instance"""
        cls.test_objs = setup__admin_ui_test_objs(with_parent=True)
        cls.routes_config = Routes__Admin__Config()
        cls.routes_config.parent_app = cls.test_objs.parent_fast_api

    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_setUpClass(self):
        """Verify class setup and inheritance"""
        with self.routes_config as _:
            assert type(_) is Routes__Admin__Config
            assert Fast_API__Routes in base_types(_)
            assert Type_Safe in base_types(_)
            assert _.tag == 'admin-config'
            assert _.parent_app is not None

    def test_02_extract_tag_from_path(self):
        """Test tag extraction from paths"""
        routes = self.routes_config

        # Test various path patterns
        assert routes._extract_tag_from_path('/'                ) == 'root'
        assert routes._extract_tag_from_path('/api/users'       ) == 'api'
        assert routes._extract_tag_from_path('/test/hello'      ) == 'test'
        assert routes._extract_tag_from_path('/admin/api/info'  ) == 'admin'
        assert routes._extract_tag_from_path(''                 ) == 'root'
        assert routes._extract_tag_from_path('/single'          ) == 'single'

    def test_03_api__routes(self):
        """Test routes listing method"""
        result = self.routes_config.api__routes()

        assert isinstance(result, list)
        assert len(result) > 0

        # Check route structure
        for route in result:
            assert 'path'       in route
            assert 'methods'    in route
            assert 'name'       in route
            assert 'tag'        in route
            assert 'is_get'     in route
            assert 'is_post'    in route
            assert 'is_put'     in route
            assert 'is_delete'  in route

        # Find a test route
        test_route = next((r for r in result if '/test/hello' in r['path']), None)
        if test_route:
            assert test_route['is_get'] is True
            assert test_route['is_post'] is False
            assert test_route['tag'] == 'test'
            assert 'GET' in test_route['methods']

    def test_04_api__routes_no_parent(self):
        """Test routes without parent app"""
        routes = Routes__Admin__Config()
        routes.parent_app = None

        result = routes.api__routes()

        assert result == []

    def test_05_api__routes_grouped(self):
        """Test grouped routes method"""
        result = self.routes_config.api__routes_grouped()

        assert isinstance(result, dict)

        # Check grouping structure
        for tag, routes in result.items():
            assert isinstance(tag, str)
            assert isinstance(routes, list)

            # All routes in group should have same tag
            for route in routes:
                assert route['tag'] == tag

        # Should have test routes
        if 'test' in result:
            test_routes = result['test']
            assert len(test_routes) > 0

            # Check test routes
            paths = [r['path'] for r in test_routes]
            assert any('/test' in p for p in paths)

    def test_06_api__middlewares(self):
        """Test middlewares listing"""
        result = self.routes_config.api__middlewares()

        assert isinstance(result, list)

        # Check middleware structure
        for middleware in result:
            assert 'type'               in middleware
            assert 'function_name'      in middleware

        # Should have at least the default middlewares
        middleware_types = [m['type'] for m in result]
        assert 'Middleware__Detect_Disconnect'  in middleware_types
        assert 'Middleware__Http_Request'       in middleware_types

    def test_07_api__middlewares_no_parent(self):
        """Test middlewares without parent app"""
        routes = Routes__Admin__Config()
        routes.parent_app = None

        result = routes.api__middlewares()

        assert result == []

    def test_08_api__openapi_spec(self):
        """Test OpenAPI spec retrieval"""
        result = self.routes_config.api__openapi_spec()

        assert isinstance(result, dict)

        # Check OpenAPI structure
        assert 'openapi' in result
        assert 'info' in result
        assert 'paths' in result

        # Check info section
        info = result['info']
        assert info['title'] == 'Test Parent API'
        assert info['version'] == 'v1.0.99'

        # Check paths
        assert len(result['paths']) > 0

        # Should have test routes in paths
        assert any('/test' in path for path in result['paths'].keys())

    def test_09_api__openapi_spec_no_parent(self):
        """Test OpenAPI spec without parent app"""
        routes = Routes__Admin__Config()
        routes.parent_app = None

        result = routes.api__openapi_spec()

        assert result == {}