from types                                                                          import NoneType
from unittest                                                                       import TestCase
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List               import Type_Safe__List
from osbot_utils.testing.__                                                         import __
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id     import Safe_Str__Id
from osbot_utils.utils.Objects                                                      import base_classes
from osbot_fast_api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix                       import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag                          import Safe_Str__Fast_API__Route__Tag
from osbot_utils.type_safe.primitives.domains.http.enums.Enum__Http__Method                import Enum__Http__Method
from osbot_fast_api.schemas.enums.Enum__Fast_API__Route__Type                          import Enum__Fast_API__Route__Type
from osbot_fast_api.schemas.Schema__Fast_API__Route                          import Schema__Fast_API__Route


class test_Schema__Fast_API__Route(TestCase):

    def test__init__(self):                                                         # Test auto-initialization of Schema__Fast_API__Route
        with Schema__Fast_API__Route() as _:
            assert type(_)         is Schema__Fast_API__Route
            assert base_classes(_) == [Type_Safe, object]

            # Verify all fields are initialized with correct types
            assert type(_.http_path)     is Safe_Str__Fast_API__Route__Prefix
            assert type(_.method_name)   is NoneType
            assert type(_.http_methods)  is Type_Safe__List                        # Will be Type_Safe__List internally
            assert type(_.route_type)    is NoneType
            assert type(_.route_class)   is NoneType                               # Nullable field
            assert type(_.route_tags)    is NoneType
            assert type(_.is_default)    is bool
            assert type(_.is_mount)      is bool

            # Verify default values
            assert _.obj() == __(is_default    = False       ,                     # Boolean default
                                 is_mount      = False       ,
                                 method_name   = None        ,
                                 route_type    = None        ,
                                 route_class   = None        ,                     # Nullable, defaults to None
                                 route_tag     = None        ,                     # Nullable, defaults to None
                                 http_path     = '/'         ,                     # Default Safe_Str__Fast_API__Route__Prefix (which makes sure it always starts with a '/')
                                 http_methods  = []          ,
                                 body_params  = None         ,
                                 path_params  = None         ,
                                 query_params = None         ,
                                 return_type  = None         ,
                                 description  = ''           )

    def test__init__with_values(self):                                             # Test initialization with provided values
        http_path     = Safe_Str__Fast_API__Route__Prefix('/api/v1/users')
        method_name   = Safe_Str__Id('get_users')
        http_methods  = [Enum__Http__Method.GET, Enum__Http__Method.HEAD]
        route_type    = Enum__Fast_API__Route__Type.API_ROUTE
        route_class   = Safe_Str__Id('Routes__Users')
        route_tag     = Safe_Str__Fast_API__Route__Tag('users')

        with Schema__Fast_API__Route(http_path     = http_path    ,
                                     method_name   = method_name  ,
                                     http_methods  = http_methods ,
                                     route_type    = route_type   ,
                                     route_class   = route_class  ,
                                     route_tags    = [route_tag]  ,
                                     is_default    = False        ,
                                     is_mount      = False        ) as _:

            assert _.obj() == __(http_path     = '/api/v1/users'            ,
                                 method_name   = 'get_users'                ,
                                 http_methods  = [Enum__Http__Method.GET    ,
                                                  Enum__Http__Method.HEAD   ],
                                 route_type    = Enum__Fast_API__Route__Type.API_ROUTE,
                                 route_class   = 'Routes__Users'            ,
                                 route_tags    = ['users']                  ,
                                 is_default    = False                      ,
                                 is_mount      = False                      ,
                                 body_params   = None                       ,
                                 path_params   = None                       ,
                                 query_params  = None                       ,
                                 return_type   = None                       ,
                                 description   = ''                         )



    def test_type_auto_conversion(self):                                           # Test Type_Safe's automatic conversion
        with Schema__Fast_API__Route() as _:
            _.http_path = "/test/path"                                              # String to Safe_Str__Fast_API__Route__Prefix
            assert type(_.http_path) is Safe_Str__Fast_API__Route__Prefix
            assert _.http_path == '/test/path'

            _.method_name = "test_method_123!"                                      # String to Safe_Str__Id
            assert type(_.method_name) is Safe_Str__Id
            assert _.method_name == 'test_method_123_'                              # Special char replaced

            _.http_methods = ["GET", "POST"]                                        # String to Enum__HTTP__Method list
            assert all(isinstance(m, Enum__Http__Method) for m in _.http_methods)
            assert _.http_methods == [Enum__Http__Method.GET, Enum__Http__Method.POST]

            _.route_type = "websocket"                                              # String to Enum__Fast_API__Route__Type
            assert type(_.route_type) is Enum__Fast_API__Route__Type
            assert _.route_type == Enum__Fast_API__Route__Type.WEBSOCKET

    def test_websocket_route(self):                                                # Test WebSocket route configuration
        with Schema__Fast_API__Route() as _:
            _.http_path    = "/ws/chat"
            _.method_name  = "websocket_handler"
            _.http_methods = []                                                    # WebSockets don't use HTTP methods
            _.route_type   = Enum__Fast_API__Route__Type.WEBSOCKET

            assert _.obj() == __(http_path     = '/ws/chat'                       ,
                                 method_name   = 'websocket_handler'               ,
                                 http_methods  = []                                ,
                                 route_type    = Enum__Fast_API__Route__Type.WEBSOCKET      ,
                                 route_class   = None                              ,
                                 route_tag     = None                              ,
                                 is_default    = False                             ,
                                 is_mount      = False                             ,
                                 body_params  = None                               ,
                                 path_params  = None                               ,
                                 query_params = None                               ,
                                 return_type  = None                               ,
                                 description  = ''                                 )

    def test_mount_route(self):                                                    # Test mount point route configuration
        with Schema__Fast_API__Route() as _:
            _.http_path    = "/static"
            _.method_name  = "static_files"
            _.http_methods = [Enum__Http__Method.GET, Enum__Http__Method.HEAD]
            _.route_type   = Enum__Fast_API__Route__Type.STATIC
            _.is_mount     = True

            assert _.is_mount is True
            assert _.route_type == Enum__Fast_API__Route__Type.STATIC

    def test_default_route(self):                                                  # Test default FastAPI route marking
        with Schema__Fast_API__Route() as _:
            _.http_path    = "/docs"
            _.method_name  = "swagger_ui_html"
            _.http_methods = [Enum__Http__Method.GET]
            _.is_default   = True

            assert _.is_default is True
            assert _.http_path == '/docs'

    def test_route_with_class_info(self):                                          # Test route with class information
        with Schema__Fast_API__Route() as _:
            _.http_path    = "/api/users/list"
            _.method_name  = "list_users"
            _.http_methods = [Enum__Http__Method.GET]
            _.route_class  = "Routes__Users"
            _.route_tag    = "users"

            assert _.route_class == 'Routes__Users'
            assert _.route_tag == 'users'

    def test_serialization_round_trip(self):                                       # Test JSON serialization preserves all types
        with Schema__Fast_API__Route() as original:
            original.http_path     = "/api/test"
            original.method_name   = "test_endpoint"
            original.http_methods  = [Enum__Http__Method.POST, Enum__Http__Method.PUT]
            original.route_type    = Enum__Fast_API__Route__Type.API_ROUTE
            original.route_class   = "Routes__Test"
            original.is_default    = False
            original.is_mount      = False

            # Serialize to JSON
            json_data = original.json()

            # Deserialize back
            with Schema__Fast_API__Route.from_json(json_data) as restored:
                # Must be perfect round-trip
                assert restored.obj() == original.obj()

                # Verify type preservation
                assert type(restored.http_path)              is Safe_Str__Fast_API__Route__Prefix
                assert type(restored.method_name)            is Safe_Str__Id
                assert all(isinstance(m, Enum__Http__Method) for m in restored.http_methods)
                assert type(restored.route_type)             is Enum__Fast_API__Route__Type
                assert type(restored.route_class)            is Safe_Str__Id

    def test_edge_cases(self):                                                     # Test edge cases and special characters
        with Schema__Fast_API__Route() as _:
            # Path with special characters
            _.http_path = "/api/{user_id}/items/{item_id:path}"
            assert _.http_path == '/api/{user_id}/items/{item_id:path}'            # Path parameters preserved

            # Method name with numbers and underscores
            _.method_name = "get_user_123_details"
            assert _.method_name == 'get_user_123_details'

            # Empty HTTP methods list (valid for WebSocket/mount)
            _.http_methods = []
            assert _.http_methods == []

            # Route type enum handling
            _.route_type = Enum__Fast_API__Route__Type.WSGI
            assert _.route_type == Enum__Fast_API__Route__Type.WSGI

    def test_all_http_methods(self):                                               # Test with all HTTP methods
        all_methods = [
            Enum__Http__Method.GET,
            Enum__Http__Method.POST,
            Enum__Http__Method.PUT,
            Enum__Http__Method.PATCH,
            Enum__Http__Method.DELETE,
            Enum__Http__Method.HEAD,
            Enum__Http__Method.OPTIONS
        ]

        with Schema__Fast_API__Route() as _:
            _.http_path    = "/any/{path:path}"
            _.method_name  = "catch_all"
            _.http_methods = all_methods

            assert len(_.http_methods) == 7
            assert all(isinstance(m, Enum__Http__Method) for m in _.http_methods)

    def test_route_type_variations(self):                                          # Test all route type enum values
        for route_type in Enum__Fast_API__Route__Type:
            with Schema__Fast_API__Route() as _:
                _.route_type = route_type
                assert _.route_type == route_type
                assert type(_.route_type) is Enum__Fast_API__Route__Type