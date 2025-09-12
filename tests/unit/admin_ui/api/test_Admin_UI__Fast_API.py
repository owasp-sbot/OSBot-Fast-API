import osbot_fast_api
from unittest                                                import TestCase
from osbot_utils.utils.Files                                 import path_combine
from osbot_fast_api.admin_ui.api.Admin_UI__Config            import Admin_UI__Config
from osbot_fast_api.admin_ui.api.Admin_UI__Fast_API          import Admin_UI__Fast_API
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs
from osbot_fast_api.api.Fast_API                             import Fast_API
from osbot_utils.type_safe.Type_Safe                         import Type_Safe
from osbot_utils.utils.Objects                               import base_types

class test_Admin_UI__Fast_API(TestCase):                                # Test Admin_UI__Fast_API class

    @classmethod
    def setUpClass(cls):                                                # Setup once for all tests
        cls.test_objs  = setup__admin_ui_test_objs(with_parent=True)
        cls.admin_ui   = cls.test_objs.admin_ui
        cls.parent_api = cls.test_objs.parent_fast_api

    @classmethod
    def tearDownClass(cls):                                             # Cleanup after all tests"""
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_setUpClass(self):                                       # Verify test setup and class structure
        with self.admin_ui as _:
            assert type(_)   is Admin_UI__Fast_API
            assert Fast_API  in base_types(_)
            assert Type_Safe in base_types(_)

            assert _.admin_config       is not None                           # Check configuration
            assert type(_.admin_config) is     Admin_UI__Config
            assert _.name               == 'Test Admin UI'
            assert _.version            == 'v1.0.99'

    def test_02_admin_config(self):                                             # Test Admin UI configuration"""
        config = self.admin_ui.admin_config

        assert config.enabled           is True                                 # Verify default config values
        assert config.base_path         == '/admin'
        assert config.require_auth      is False                                # Disabled for tests
        assert config.show_dashboard    is True
        assert config.show_cookies      is True
        assert config.show_routes       is True
        assert config.show_docs         is True
        assert config.allow_api_testing is True

    def test_03_parent_app_reference(self):                                     # Test parent app reference
        assert self.admin_ui.parent_app         is not None
        assert self.admin_ui.parent_app         is self.parent_api
        assert type(self.admin_ui.parent_app)   is Fast_API

    def test_04_routes_setup(self):                                             # Test that admin routes are properly set up
        routes      = self.admin_ui.routes()
        route_paths = [r['http_path'] for r in routes]

        assert '/admin-info/api/server-info'     in route_paths                                # Check API routes exist
        assert '/admin-info/api/app-info'        in route_paths
        assert '/admin-info/api/stats'           in route_paths
        assert '/admin-info/api/health'          in route_paths
        assert '/admin-config/api/routes'        in route_paths
        assert '/admin-cookies/api/cookies-list' in route_paths
        assert '/admin-docs/api/docs-endpoints'  in route_paths

        # Check static routes
        assert '/admin-static/index'             in route_paths  # Index page

    def test_05_static_folder_path(self):                                   # Test static folder configuration
        static_path   = self.admin_ui.path_static_folder()
        expected_path = path_combine(osbot_fast_api.path, 'admin_ui/static')

        assert static_path == expected_path                                 # Note: Folder may not exist in test environment

    def test_06_mounting_behavior(self):                                    # Test mounting Admin UI to parent app
        parent = Fast_API(name='Parent API').setup()                        # Create fresh instances for this test
        admin            = Admin_UI__Fast_API(name='Admin Mount Test')
        admin.parent_app = parent
        admin.setup()
        parent.app().mount('/admin', admin.app())                           # Create fresh instances for this test
        parent_routes = parent.routes_paths_all()                           # Verify mounting worked
        assert any('/admin' in path for path in parent_routes)

    def test_07_conditional_route_setup(self):                              # Test conditional route setup based on config
        config = Admin_UI__Config(show_dashboard=False)                     # Test with dashboard disabled
        admin  = Admin_UI__Fast_API(admin_config=config)
        admin.setup()

        routes = admin.routes()
        route_paths = [r['http_path'] for r in routes]

        assert '/admin-info/api/server-info' not in route_paths                    # Dashboard routes should not exist
        assert '/admin-info/api/app-info'    not in route_paths
        assert '/admin-info/api/stats'       not in route_paths

        assert '/admin-config/api/routes'    in route_paths                         # But other routes should still exist

    def test_08_custom_base_path(self):                                             # Test custom base path configuration
        config = Admin_UI__Config(base_path='/custom-admin')
        admin  = Admin_UI__Fast_API(admin_config=config)

        assert admin.base_path              == '/custom-admin'                      # confirm the new base_path was set
        assert admin.admin_config.base_path == '/custom-admin'




