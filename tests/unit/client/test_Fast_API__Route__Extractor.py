import pytest
from unittest                                                                    import TestCase
from fastapi import FastAPI, APIRouter, Path
from fastapi.routing                                                             import APIWebSocketRoute
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id  import Safe_Str__Id
from osbot_utils.testing.__                                                      import __
from osbot_fast_api.client.Fast_API__Route__Extractor                            import Fast_API__Route__Extractor
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.utils.Objects import base_classes, full_type_name
from starlette.middleware.wsgi                                                   import WSGIMiddleware
from starlette.routing                                                           import Mount, Route
from starlette.staticfiles                                                       import StaticFiles
from osbot_fast_api.api.Fast_API                                                 import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes                                  import Fast_API__Routes
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Prefix                    import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.schemas.for_osbot_utils.enums.Enum__Http__Method             import Enum__Http__Method
from osbot_fast_api.schemas.routes.Schema__Fast_API__Route                       import Schema__Fast_API__Route
from osbot_fast_api.schemas.routes.Schema__Fast_API__Routes__Collection          import Schema__Fast_API__Routes__Collection
from osbot_fast_api.schemas.routes.enums.Enum__Route__Type                       import Enum__Route__Type


class test_Fast_API__Route__Extractor(TestCase):

    # todo: see if can use the Test__Fast_API__With_Routes.py class and endpoints here
    @classmethod
    def setUpClass(cls):
        cls.app = FastAPI(title="Test API")                                     # Create a test FastAPI app with various route types

        @cls.app.get("/users")                                                  # Add regular API routes
        def get_users():
            return []

        @cls.app.post("/users")
        def create_user():
            return {}

        @cls.app.get("/users/{user_id}")
        def get_user(user_id: int):
            return {}

        @cls.app.websocket("/ws")                                               # Add WebSocket route
        async def websocket_endpoint(websocket):
            pass

        router = APIRouter(prefix="/api/v1")                                    # Add a router

        @router.get("/items")
        def get_items():
            return []

        @router.put("/items/{item_id}")
        def update_item(item_id: int):
            return {}

        cls.app.include_router(router)

        cls.app.mount("/static", StaticFiles(directory="."), name="static")     # Add static files mount

    def test__init__(self):                                                         # Test extractor initialization
        with Fast_API__Route__Extractor(app=self.app) as _:
            assert type(_)         is Fast_API__Route__Extractor
            assert base_classes(_) == [Type_Safe, object]

            # Verify attributes
            assert type(_.app)             is FastAPI
            assert type(_.include_default) is bool
            assert type(_.expand_mounts)   is bool

            # Verify defaults
            assert _.app             == self.app
            assert _.include_default is False
            assert _.expand_mounts   is False

    def test_extract_routes(self):                                                  # Test main extraction method
        with Fast_API__Route__Extractor(app=self.app) as _:
            collection = _.extract_routes()
            assert type(collection) is Schema__Fast_API__Routes__Collection
            assert collection.total_routes > 0
            assert collection.has_websockets is True                                # We added a WebSocket
            assert collection.has_mounts     is True                                # We added static mount

            # Check that routes were extracted
            paths = [str(r.http_path) for r in collection.routes]

            assert paths == ['/users'                   ,
                             '/users'                   ,
                             '/users/{user_id}'         ,
                             '/ws'                      ,
                             '/api/v1/items'            ,
                             '/api/v1/items/{item_id}'  ,
                             '/static'                  ]
            assert collection.obj() == __( total_routes    = 7                                   ,
                                           has_mounts      = True                                ,
                                           has_websockets  = True                                ,
                                           routes          = [__(is_default   = False                                  ,
                                                                 is_mount     = False                                  ,
                                                                 method_name  = 'get_users'                            ,
                                                                 route_type   = 'api_route'                            ,
                                                                 route_class  = 'test_Fast_API__Route__Extractor'      ,
                                                                 route_tags   = None                                   ,
                                                                 path_params  = []                                     ,
                                                                 http_path    = '/users'                               ,
                                                                 http_methods = [Enum__Http__Method.GET               ]),

                                                                __(is_default   = False                                ,
                                                                  is_mount     = False                                 ,
                                                                  method_name  = 'create_user'                         ,
                                                                  route_type   = 'api_route'                           ,
                                                                  route_class  = 'test_Fast_API__Route__Extractor'     ,
                                                                  route_tags   = None                                  ,
                                                                  path_params  = []                                    ,
                                                                  http_path    = '/users'                              ,
                                                                  http_methods = [Enum__Http__Method.POST             ]),

                                                                __(is_default   = False                                ,
                                                                  is_mount     = False                                 ,
                                                                  method_name  = 'get_user'                            ,
                                                                  route_type   = 'api_route'                           ,
                                                                  route_class  = 'test_Fast_API__Route__Extractor'     ,
                                                                  route_tags   = None                                  ,
                                                                  path_params  = [__( required    = True               ,
                                                                                      name        = 'user_id'          ,
                                                                                      location    = 'path'             ,
                                                                                      param_type  = 'builtins.int'     )],
                                                                  http_path    = '/users/{user_id}'                    ,
                                                                  http_methods = [Enum__Http__Method.GET               ]),

                                                                __(is_default   = False                                ,
                                                                  is_mount     = False                                 ,
                                                                  method_name  = 'websocket_endpoint'                  ,
                                                                  route_type   = 'websocket'                           ,
                                                                  route_class  = None                                  ,
                                                                  route_tags   = None                                  ,
                                                                  path_params  = None                                  ,
                                                                  http_path    = '/ws'                                 ,
                                                                  http_methods = []                                    ),

                                                                __(is_default   = False                                ,
                                                                  is_mount     = False                                 ,
                                                                  method_name  = 'get_items'                           ,
                                                                  route_type   = 'api_route'                           ,
                                                                  route_class  = 'test_Fast_API__Route__Extractor'     ,
                                                                  route_tags   = None                                  ,
                                                                  path_params  = []                                    ,
                                                                  http_path    = '/api/v1/items'                       ,
                                                                  http_methods = [Enum__Http__Method.GET               ]),

                                                                __(is_default   = False                                ,
                                                                  is_mount     = False                                 ,
                                                                  method_name  = 'update_item'                         ,
                                                                  route_type   = 'api_route'                           ,
                                                                  route_class  = 'test_Fast_API__Route__Extractor'     ,
                                                                  route_tags   = None                                  ,
                                                                  path_params  = [__(required    = True                ,
                                                                                      name        = 'item_id'          ,
                                                                                      location    = 'path'             ,
                                                                                      param_type  = 'builtins.int'     )],
                                                                  http_path    = '/api/v1/items/{item_id}'             ,
                                                                  http_methods = [Enum__Http__Method.PUT               ]),

                                                                __(is_default   = False                                ,
                                                                  is_mount     = True                                  ,
                                                                  method_name  = 'static_files'                        ,
                                                                  route_type   = 'static'                              ,
                                                                  route_class  = None                                  ,
                                                                  route_tags   = None                                  ,
                                                                  path_params  = None                                  ,
                                                                  http_path    = '/static'                             ,
                                                                  http_methods = [Enum__Http__Method.GET               ,
                                                                                  Enum__Http__Method.HEAD            ] )])


    def test_extract_routes_with_default(self):                                     # Test including default FastAPI routes
        with Fast_API__Route__Extractor(app=self.app, include_default=True) as _:
            collection = _.extract_routes()

            # Should include default FastAPI routes
            paths = [str(r.http_path) for r in collection.routes]
            assert '/docs' in paths or '/openapi.json' in paths                     # Default routes

            # Check is_default flag
            default_routes = [r for r in collection.routes if r.is_default]
            assert len(default_routes) > 0

    def test_extract_routes_without_default(self):                                  # Test excluding default routes
        with Fast_API__Route__Extractor(app=self.app, include_default=False) as _:
            collection = _.extract_routes()

            # Should NOT include default FastAPI routes
            default_routes = [r for r in collection.routes if r.is_default]
            assert len(default_routes) == 0

    def test__create_api_route(self):                                               # Test API route creation
        with Fast_API__Route__Extractor(app=self.app) as _:
            def an_endpoint():
                pass
            route = Route(path     = "/test"         ,
                          name     = 'route_name'    ,
                          endpoint = an_endpoint     ,
                          methods  = {"GET", "POST"} )
            route = _.create_api_route(route, Safe_Str__Fast_API__Route__Prefix('/api'))

            assert route.obj() == __(is_default   = False                            ,
                                     is_mount     = False                            ,
                                     method_name  = 'route_name'                     ,
                                     route_type   = 'api_route'                      ,
                                     route_class  = 'test_Fast_API__Route__Extractor',
                                     route_tags   = None                             ,
                                     http_path    = '/api'                           ,
                                     http_methods = [ Enum__Http__Method.GET         ,
                                                      Enum__Http__Method.HEAD        ,
                                                      Enum__Http__Method.POST        ])
            assert type(route)              is Schema__Fast_API__Route
            assert route.http_path          == '/api'
            assert route.method_name        == 'route_name'
            assert route.route_type         == Enum__Route__Type.API_ROUTE
            assert Enum__Http__Method.GET   in route.http_methods
            assert Enum__Http__Method.POST  in route.http_methods

    def test__create_websocket_route(self):                                         # Test WebSocket route creation
        with Fast_API__Route__Extractor(app=self.app) as _:
            # Simulate a WebSocket route
            def ws_endpoint():
                pass
            route = APIWebSocketRoute(path     = "/ws/chat"     ,
                                      endpoint = ws_endpoint    ,
                                      name     = "chat_handler" )

            route = _.create_websocket_route(route, Safe_Str__Fast_API__Route__Prefix('/ws/chat'))
            assert route.obj() == __(is_default     = False         ,
                                     is_mount       = False         ,
                                     method_name    = 'chat_handler',
                                     route_type     = 'websocket'   ,
                                     route_class    = None          ,
                                     route_tags     = None          ,
                                     http_path      = '/ws/chat'    ,
                                     http_methods   =   []          )
            assert type(route) is Schema__Fast_API__Route
            assert route.http_path    == '/ws/chat'
            assert route.method_name  == 'chat_handler'
            assert route.route_type   == Enum__Route__Type.WEBSOCKET
            assert route.http_methods == []                                         # WebSockets don't have HTTP methods

    def test__extract_mount_routes_static(self):                                    # Test static files mount extraction
        with Fast_API__Route__Extractor(app=self.app) as _: # Create a static mount
            static_app = StaticFiles(directory=".")
            mount = Mount("/static", app=static_app)

            routes = _.extract_mount_routes(mount, Safe_Str__Fast_API__Route__Prefix('/static'))
            assert routes.obj() == [__( is_default   = False         ,
                                        is_mount     = True          ,
                                        method_name  = 'static_files',
                                        route_type   = 'static'      ,
                                        route_class  = None          ,
                                        route_tags   = None          ,
                                        http_path    ='/static'      ,
                                        http_methods = [Enum__Http__Method.GET,
                                                       Enum__Http__Method.HEAD])]

            assert len(routes) == 1
            route = routes[0]
            assert route.http_path    == '/static'
            assert route.method_name  == 'static_files'
            assert route.route_type   == Enum__Route__Type.STATIC
            assert route.is_mount     is True
            assert Enum__Http__Method.GET in route.http_methods
            assert Enum__Http__Method.HEAD in route.http_methods

    def test__extract_mount_routes_wsgi(self):                                      # Test WSGI mount extraction
        with Fast_API__Route__Extractor(app=self.app) as _:
            # Create a WSGI mount
            def wsgi_app(environ, start_response):
                pass

            wsgi_middleware = WSGIMiddleware(wsgi_app)
            mount = Mount("/legacy", app=wsgi_middleware)

            routes = _.extract_mount_routes(mount, Safe_Str__Fast_API__Route__Prefix('/legacy'))
            assert routes.obj() == [__( is_default   = False     ,
                                        is_mount     = True      ,
                                        method_name  = 'wsgi_app',
                                        route_type   = 'wsgi'    ,
                                        route_class  = None      ,
                                        route_tags   = None      ,
                                        http_path    ='/legacy'  ,
                                        http_methods = []        )]

            assert len(routes) == 1
            route = routes[0]
            assert route.http_path    == '/legacy'
            assert route.method_name  == 'wsgi_app'
            assert route.route_type   == Enum__Route__Type.WSGI
            assert route.is_mount     is True
            assert route.http_methods == []                                         # Unknown methods for WSGI

    def test__combine_paths(self):                                                  # Test path combination logic
        with Fast_API__Route__Extractor(app=self.app) as _:
            # Test various path combinations
            prefix = Safe_Str__Fast_API__Route__Prefix('/api/v1')

            # Normal path
            result = _._combine_paths(prefix, '/users')
            assert result == '/api/v1/users'

            # Path with trailing slash
            prefix = Safe_Str__Fast_API__Route__Prefix('/api/v1/')
            result = _._combine_paths(prefix, '/users')
            assert result == '/api/v1/users'

            # Path with leading slash
            prefix = Safe_Str__Fast_API__Route__Prefix('/api/v1')
            result = _._combine_paths(prefix, 'users')
            assert result == '/api/v1/users'

            # Empty prefix
            prefix = Safe_Str__Fast_API__Route__Prefix('')
            result = _._combine_paths(prefix, 'users')
            assert result == '/users'

            # Root path
            prefix = Safe_Str__Fast_API__Route__Prefix('/')
            result = _._combine_paths(prefix, 'users')
            assert result == '/users'

    def test__is_default_route(self):                                               # Test default route detection
        with Fast_API__Route__Extractor(app=self.app) as _:
            # These should be identified as default routes
            assert _.is_default_route('/docs') is True
            assert _.is_default_route('/redoc') is True
            assert _.is_default_route('/openapi.json') is True

            # These should NOT be default routes
            assert _.is_default_route('/api/users') is False
            assert _.is_default_route('/custom') is False

    def test__extract_route_class(self):                                            # Test Routes__* class extraction
        with Fast_API__Route__Extractor(app=self.app) as _:
            # Mock a route with Routes__ class
            class MockRoute:
                class endpoint:
                    __qualname__ = "Routes__Users.get_users"

            route_class = _.extract__route_class(MockRoute())
            assert route_class == 'Routes__Users'

            # Route without Routes__ prefix
            class MockRoute2:
                class endpoint:
                    __qualname__ = "SomeClass.method"

            route_class = _.extract__route_class(MockRoute2())
            assert route_class == 'SomeClass'

            # Route without endpoint
            class MockRoute3:
                pass

            route_class = _.extract__route_class(MockRoute3())
            assert route_class == ''

    def test_expand_mounts(self):                                                   # Test mount expansion feature
        # Create app with nested mount
        nested_app = FastAPI()

        @nested_app.get("/nested")
        def nested_endpoint():
            return {}

        main_app = FastAPI()
        main_app.mount("/sub", nested_app)

        # Without expansion
        with Fast_API__Route__Extractor(app=main_app, expand_mounts=False) as _:
            collection = _.extract_routes()
            paths = [str(r.http_path) for r in collection.routes]
            assert '/sub' in paths
            assert '/sub/nested' not in paths                                       # Not expanded

        # With expansion
        with Fast_API__Route__Extractor(app=main_app, expand_mounts=True) as _:
            collection = _.extract_routes()
            paths = [str(r.http_path) for r in collection.routes]
            assert paths == ['/sub/nested']


    def test_complex_app_extraction(self):                                          # Test with Fast_API class
        with Fast_API(name="Complex API") as fast_api:
            fast_api.setup()

            # Add custom routes
            class Routes__Test(Fast_API__Routes):
                tag = 'test'

                def test_method(self):
                    return {"result": "test"}

                def setup_routes(self):
                    self.add_route_get(self.test_method)
                    self.add_route_post(self.test_method)

            fast_api.add_routes(Routes__Test)

            # Extract routes
            with Fast_API__Route__Extractor(app=fast_api.app()) as _:
                collection = _.extract_routes()

                # Find test routes
                test_routes = [r for r in collection.routes
                              if str(r.http_path).startswith('/test')]

                assert len(test_routes) == 2

                # Check route class extraction
                routes_with_class = [(r.route_class, r.method_name) for r in collection.routes
                                    if r.route_class and str(r.route_class).startswith('Routes__')]
                assert len(routes_with_class) > 0
                assert routes_with_class == [(Safe_Str__Id('Routes__Config'    ), Safe_Str__Id('info'           )),
                                             (Safe_Str__Id('Routes__Config'    ), Safe_Str__Id('status'         )),
                                             (Safe_Str__Id('Routes__Config'    ), Safe_Str__Id('version'        )),
                                             (Safe_Str__Id('Routes__Config'    ), Safe_Str__Id('routes__json'   )),
                                             (Safe_Str__Id('Routes__Config'    ), Safe_Str__Id('routes__html'   )),
                                             (Safe_Str__Id('Routes__Config'    ), Safe_Str__Id('openapi_python' )),
                                             (Safe_Str__Id('Routes__Set_Cookie'), Safe_Str__Id('set_cookie_form')),
                                             (Safe_Str__Id('Routes__Set_Cookie'), Safe_Str__Id('set_auth_cookie')),
                                             (Safe_Str__Id('Routes__Test'      ), Safe_Str__Id('test_method'    )),
                                             (Safe_Str__Id('Routes__Test'      ), Safe_Str__Id('test_method'    ))]


    def test_http_method_sorting(self):                                             # Test that HTTP methods are sorted
        with Fast_API__Route__Extractor(app=self.app) as _:
            test_route = Route(path     = "/test"                         ,         # route with unsorted methods
                               name     = "test"                          ,
                               endpoint = None                           ,
                               methods  = {"POST", "GET", "DELETE", "PUT"})

            route = _.create_api_route(test_route, Safe_Str__Fast_API__Route__Prefix('/test'))

            method_strings = [m for m in route.http_methods]                               # Methods should be sorted
            assert method_strings == sorted(method_strings) == ["DELETE", "GET", "HEAD", "POST", "PUT"]

    def test_unknown_http_methods(self):                                                    # Test handling of unknown HTTP methods
        with Fast_API__Route__Extractor(app=self.app) as _:

            test_route = Route(path     = "/test"                          ,                # route with unknown method
                               name     = "test"                           ,
                               endpoint = None                            ,
                               methods  = {"GET", "UNKNOWN_METHOD", "POST"})

            expected_error = "'UNKNOWN_METHOD' is not a valid Enum__Http__Method"
            with pytest.raises(Exception, match=expected_error):
                _.create_api_route(test_route, Safe_Str__Fast_API__Route__Prefix('/test'))  # will fail here

    def test_route_without_name(self):                                              # Test handling routes without names
        with Fast_API__Route__Extractor(app=self.app) as _:
            test_route = Route(path     = "/test"  ,                                # route without name
                               name     = None     ,
                               endpoint = None    ,
                               methods  = {"POST"})

            route = _.create_api_route(test_route, Safe_Str__Fast_API__Route__Prefix('/test'))

            assert route.method_name == 'NoneType'                                  # this is actually the FastAPI behaviour since with both none in name and endpoint, the name value will be 'NoneType'

    def test_generic_mount(self):                                                   # Test generic mount (not static/WSGI)
        with Fast_API__Route__Extractor(app=self.app) as _:
            # Create a generic mount
            class GenericApp:
                pass

            mount = Mount("/generic", app=GenericApp())

            routes = _.extract_mount_routes(mount, Safe_Str__Fast_API__Route__Prefix('/generic'))

            assert len(routes) == 1
            route = routes[0]
            assert route.http_path    == '/generic'
            assert route.method_name  == 'mount'
            assert route.route_type   == Enum__Route__Type.MOUNT
            assert route.is_mount     is True