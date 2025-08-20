import time
from unittest                                                   import TestCase
from fastapi                                                    import FastAPI
from osbot_utils.utils.Misc                                     import list_set, timestamp_utc_now, is_guid
from osbot_fast_api.admin_ui.api.routes.Routes__Admin__Info     import Routes__Admin__Info
from osbot_fast_api.admin_ui.api.testing.Admin_UI__Test_Objs    import setup__admin_ui_test_objs, cleanup_admin_ui_test_objs
from osbot_fast_api.api.routes.Fast_API__Routes                 import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                            import Type_Safe
from osbot_utils.utils.Objects                                  import base_types

class test_Routes__Admin__Info(TestCase):                   # Test Routes__Admin__Info class directly

    @classmethod
    def setUpClass(cls):                                    # Setup routes instance
        cls.test_objs  = setup__admin_ui_test_objs(with_parent=True)
        cls.routes_info = Routes__Admin__Info(parent_app=cls.test_objs.parent_fast_api)

    @classmethod
    def tearDownClass(cls):                                     # Cleanup
        cleanup_admin_ui_test_objs(cls.test_objs)

    def test_01_setUpClass(self):                               # Verify class setup and inheritance
        with self.routes_info as _:
            assert type(_)          is Routes__Admin__Info
            assert Fast_API__Routes in base_types(_)
            assert Type_Safe        in base_types(_)
            assert _.tag            == 'admin-info'
            assert _.parent_app     is not None

    def test_02_api__server_info(self):                         # Test server info method directly
        result = self.routes_info.api__server_info()

        # Check structure
        expected_fields = [ 'server_id'         ,
                            'server_name'       ,
                            'server_instance_id',
                            'server_boot_time'  ,
                            'current_time'      ,
                            'uptime_ms'         ]
        assert list_set(result.keys()) == sorted(expected_fields)


        assert isinstance(result['server_id'         ], str)                 # Verify data types
        assert isinstance(result['server_instance_id'], str)
        assert isinstance(result['server_boot_time'  ], int)
        assert isinstance(result['current_time'      ], int)
        assert isinstance(result['uptime_ms'         ], int)

        # Verify values
        assert result['server_id']                   == ''                  # we didn't set the FAST_API__SERVER_ID env var , so this should be empty
        assert is_guid(result['server_instance_id']) is True
        assert result['uptime_ms']                   >= 0
        assert result['current_time'] > result['server_boot_time']

    def test_03_api__app_info(self):                                        # Test app info method directly"""
        result = self.routes_info.api__app_info()

        expected_fields = [ 'name'          ,                               # Check structure
                            'version'       ,
                            'description'   ,
                            'base_path'     ,
                            'docs_offline'  ,
                            'enable_cors'   ,
                            'enable_api_key']
        assert list_set(result.keys()) == sorted(expected_fields)

        assert result['name'          ] == 'Test Parent API'                # Verify values from parent app
        assert result['version'       ] == 'v1.0.99'
        assert result['description'   ] == 'Parent API for Admin UI testing'
        assert result['base_path'     ] == '/'
        assert result['docs_offline'  ] is True
        assert result['enable_cors'   ] is True
        assert result['enable_api_key'] is False

    def test_04_api__app_info_no_parent(self):                              # Test app info without parent app
        routes = Routes__Admin__Info()
        routes.parent_app = None

        result = routes.api__app_info()

        assert result == {"error": "Parent app not configured"}

    def test_05_api__stats(self):                                           # Test stats method directly
        result = self.routes_info.api__stats()

        # Check structure
        expected_fields = [ 'total_routes'      ,
                            'methods'           ,
                            'prefixes'          ,
                            'middlewares_count' ,
                            'has_static_files'  ]
        assert list_set(result.keys()) == sorted(expected_fields)

        # Verify data types
        assert isinstance(result['total_routes'     ], int)
        assert isinstance(result['methods'          ], dict)
        assert isinstance(result['prefixes'         ], dict)
        assert isinstance(result['middlewares_count'], int)
        assert isinstance(result['has_static_files' ], bool)

        # Verify values
        assert result['total_routes'] > 0
        assert 'GET' in result['methods']
        assert result['methods']['GET'] > 0

        # Check test routes are counted
        assert '/test' in result['prefixes'] or '/test/hello' in str(result['prefixes'])

    def test_06_api__stats_no_parent(self):                         # Test stats without parent app
        routes = Routes__Admin__Info()
        routes.parent_app = None

        result = routes.api__stats()

        assert result == {"error": "Parent app not configured"}

    def test_07_api__health(self):                                  # Test health check method
        result = self.routes_info.api__health()

        # Check structure
        assert list_set(result.keys()) == ['status', 'timestamp']

        # Verify values
        assert result['status'] == 'Ok'
        assert isinstance(result['timestamp'], str)

        # Timestamp should be recent
        timestamp = int(result['timestamp'])
        now = timestamp_utc_now()
        assert abs(now - timestamp) < 1000  # Within 1 second

    def test_08_routes_registration(self):                 # Test that routes are properly registered
        routes_instance   = Routes__Admin__Info(app=FastAPI()).setup()
        registered_routes = routes_instance.routes_paths()

        assert '/api/server-info' in registered_routes      # All API methods should be registered
        assert '/api/app-info'    in registered_routes
        assert '/api/stats'       in registered_routes
        assert '/api/health'      in registered_routes



