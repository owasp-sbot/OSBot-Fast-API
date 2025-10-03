import re

import pytest
from unittest                                                                    import TestCase
from fastapi                                                                     import FastAPI, APIRouter, Path
from fastapi.routing                                                             import APIWebSocketRoute
from osbot_fast_api.api.decorators.route_path                                    import route_path
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id  import Safe_Str__Id
from osbot_utils.testing.__                                                      import __
from osbot_fast_api.client.Fast_API__Route__Extractor                            import Fast_API__Route__Extractor
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.utils.Objects                                                   import base_classes, full_type_name
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
                                           routes          = [__(is_default    = False                                ,
                                                                 is_mount      = False                                ,
                                                                 method_name   = 'get_users'                          ,
                                                                 route_type    = 'api_route'                          ,
                                                                 route_class   = 'test_Fast_API__Route__Extractor'    ,
                                                                 route_tags    = []                                   ,
                                                                 description   = ''                                   ,
                                                                 path_params   = []                                   ,
                                                                 query_params  = []                                   ,
                                                                 body_params   = []                                   ,
                                                                 return_type   = None                                 ,
                                                                 http_path     = '/users'                             ,
                                                                 http_methods  = [Enum__Http__Method.GET              ]),

                                                                __(is_default    = False                               ,
                                                                  is_mount      = False                                ,
                                                                  method_name   = 'create_user'                        ,
                                                                  route_type    = 'api_route'                          ,
                                                                  route_class   = 'test_Fast_API__Route__Extractor'    ,
                                                                  route_tags    = []                                   ,
                                                                  description   = ''                                   ,
                                                                  path_params   = []                                   ,
                                                                  query_params  = []                                   ,
                                                                  body_params   = []                                   ,
                                                                  return_type   = None                                 ,
                                                                  http_path     = '/users'                             ,
                                                                  http_methods  = [Enum__Http__Method.POST             ]),

                                                                __(is_default    = False                               ,
                                                                  is_mount      = False                                ,
                                                                  method_name   = 'get_user'                           ,
                                                                  route_type    = 'api_route'                          ,
                                                                  route_class   = 'test_Fast_API__Route__Extractor'    ,
                                                                  route_tags    = []                                   ,
                                                                  description   = ''                                   ,
                                                                  path_params   = [__(default      = None              ,
                                                                                      description  = None              ,
                                                                                      required     = True              ,
                                                                                      name         = 'user_id'         ,
                                                                                      param_type   = 'builtins.int'    )],
                                                                  query_params  = []                                   ,
                                                                  body_params   = []                                   ,
                                                                  return_type   = None                                 ,
                                                                  http_path     = '/users/{user_id}'                   ,
                                                                  http_methods  = [Enum__Http__Method.GET              ]),

                                                                __(is_default    = False                               ,
                                                                  is_mount      = False                                ,
                                                                  method_name   = 'websocket_endpoint'                 ,
                                                                  route_type    = 'websocket'                          ,
                                                                  route_class   = None                                 ,
                                                                  route_tags    = None                                 ,
                                                                  description   = ''                                   ,
                                                                  path_params   = None                                 ,
                                                                  query_params  = None                                 ,
                                                                  body_params   = None                                 ,
                                                                  return_type   = None                                 ,
                                                                  http_path     = '/ws'                                ,
                                                                  http_methods  = []                                   ),

                                                                __(is_default    = False                               ,
                                                                  is_mount      = False                                ,
                                                                  method_name   = 'get_items'                          ,
                                                                  route_type    = 'api_route'                          ,
                                                                  route_class   = 'test_Fast_API__Route__Extractor'    ,
                                                                  route_tags    = []                                   ,
                                                                  description   = ''                                   ,
                                                                  path_params   = []                                   ,
                                                                  query_params  = []                                   ,
                                                                  body_params   = []                                   ,
                                                                  return_type   = None                                 ,
                                                                  http_path     = '/api/v1/items'                      ,
                                                                  http_methods  = [Enum__Http__Method.GET              ]),

                                                                __(is_default    = False                               ,
                                                                  is_mount      = False                                ,
                                                                  method_name   = 'update_item'                        ,
                                                                  route_type    = 'api_route'                          ,
                                                                  route_class   = 'test_Fast_API__Route__Extractor'    ,
                                                                  route_tags    = []                                   ,
                                                                  description   = ''                                   ,
                                                                  path_params   = [__(default      = None              ,
                                                                                      description  = None              ,
                                                                                      required     = True              ,
                                                                                      name         = 'item_id'         ,
                                                                                      param_type   = 'builtins.int'    )],
                                                                  query_params  = []                                   ,
                                                                  body_params   = []                                   ,
                                                                  return_type   = None                                 ,
                                                                  http_path     = '/api/v1/items/{item_id}'            ,
                                                                  http_methods  = [Enum__Http__Method.PUT              ]),

                                                                __(is_default    = False                               ,
                                                                  is_mount      = True                                 ,
                                                                  method_name   = 'static_files'                       ,
                                                                  route_type    = 'static'                             ,
                                                                  route_class   = None                                 ,
                                                                  route_tags    = None                                 ,
                                                                  description   = ''                                   ,
                                                                  path_params   = None                                 ,
                                                                  query_params  = None                                 ,
                                                                  body_params   = None                                 ,
                                                                  return_type   = None                                 ,
                                                                  http_path     = '/static'                            ,
                                                                  http_methods  = [Enum__Http__Method.GET              ,
                                                                                  Enum__Http__Method.HEAD             ] )])



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

            assert route.obj() == __(body_params   = None                            ,
                                     description   = ''                              ,
                                     is_default   = False                            ,
                                     is_mount     = False                            ,
                                     method_name  = 'route_name'                     ,
                                     route_type   = 'route'                          ,
                                     route_class  = 'test_Fast_API__Route__Extractor',
                                     route_tags   = None                             ,
                                     http_path    = '/api'                           ,
                                     http_methods = [ Enum__Http__Method.GET         ,
                                                      Enum__Http__Method.HEAD        ,
                                                      Enum__Http__Method.POST       ],
                                    path_params   = None                             ,
                                    query_params  = None                             ,
                                    return_type   = None                             )
            assert type(route)              is Schema__Fast_API__Route
            assert route.http_path          == '/api'
            assert route.method_name        == 'route_name'
            assert route.route_type         == Enum__Route__Type.ROUTE
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
            assert route.obj() == __(body_params    = None          ,
                                     is_default     = False         ,
                                     is_mount       = False         ,
                                     method_name    = 'chat_handler',
                                     route_type     = 'websocket'   ,
                                     route_class    = None          ,
                                     route_tags     = None          ,
                                     http_path      = '/ws/chat'    ,
                                     http_methods   =   []          ,
                                     path_params    = None          ,
                                     query_params   = None          ,
                                     return_type    = None          ,
                                     description    = ''            )
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
                                                       Enum__Http__Method.HEAD],
                                        body_params  = None          ,
                                        path_params  = None          ,
                                        query_params = None          ,
                                        return_type  = None          ,
                                        description  = ''            )]

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
                                        http_methods = []        ,
                                        body_params  = None      ,
                                        path_params  = None      ,
                                        query_params = None      ,
                                        return_type  = None      ,
                                        description  = ''        )                                    ]

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
            result = _.combine_paths(prefix, '/users')
            assert result == '/api/v1/users'

            # Path with trailing slash
            prefix = Safe_Str__Fast_API__Route__Prefix('/api/v1/')
            result = _.combine_paths(prefix, '/users')
            assert result == '/api/v1/users'

            # Path with leading slash
            prefix = Safe_Str__Fast_API__Route__Prefix('/api/v1')
            result = _.combine_paths(prefix, 'users')
            assert result == '/api/v1/users'

            # Empty prefix
            prefix = Safe_Str__Fast_API__Route__Prefix('')
            result = _.combine_paths(prefix, 'users')
            assert result == '/users'

            # Root path
            prefix = Safe_Str__Fast_API__Route__Prefix('/')
            result = _.combine_paths(prefix, 'users')
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


    def test_empty_app_extraction(self):                                                # Test with empty FastAPI app
        empty_app = FastAPI()
        with Fast_API__Route__Extractor(app=empty_app) as _:
            collection = _.extract_routes()
            assert collection.total_routes      == 0
            assert collection.has_mounts        is False
            assert collection.has_websockets    is False
            assert collection.routes            == []


    def test_duplicate_paths_different_methods(self):                                   # Test same path with different HTTP methods
        app = FastAPI()

        @app.get("/resource")
        def get_resource():
            return {"method": "GET"}

        @app.post("/resource")
        def create_resource():
            return {"method": "POST"}

        @app.delete("/resource")
        def delete_resource():
            return {"method": "DELETE"}

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()

            resource_routes = [r for r in collection.routes if str(r.http_path) == '/resource'] # Should have 3 separate route entries
            assert len(resource_routes) == 3

            methods = [r.http_methods[0] for r in resource_routes]                              # Each should have different methods
            assert methods == [ Enum__Http__Method.GET    ,
                                Enum__Http__Method.POST   ,
                                Enum__Http__Method.DELETE ]


    def test_deeply_nested_mounts(self):                                               # Test multiple levels of mounted apps
        level3_app = FastAPI()
        @level3_app.get("/deep")
        def deep_endpoint():
            return {"level": 3}

        level2_app = FastAPI()
        @level2_app.get("/middle")
        def middle_endpoint():
            return {"level": 2}
        level2_app.mount("/level3", level3_app)

        level1_app = FastAPI()
        @level1_app.get("/top")
        def top_endpoint():
            return {"level": 1}
        level1_app.mount("/level2", level2_app)

        # Test with expand_mounts=True
        with Fast_API__Route__Extractor(app=level1_app, expand_mounts=True) as _:
            collection = _.extract_routes()
            paths = sorted([str(r.http_path) for r in collection.routes])
            assert paths == ['/level2/level3/deep', '/level2/middle', '/top']

        # Test with expand_mounts=False
        with Fast_API__Route__Extractor(app=level1_app, expand_mounts=False) as _:
            collection = _.extract_routes()
            paths = sorted([str(r.http_path) for r in collection.routes])
            assert '/level2'                 in paths
            assert '/level2/level3/deep' not in paths


    def test_path_params_extraction(self):                                             # Test complex path parameter patterns
        app = FastAPI()

        @app.get("/users/{user_id}/posts/{post_id}/comments/{comment_id}")
        def get_nested_resource(user_id   : int                                   ,
                                post_id   : str =  Path(description="The post Id"),
                                comment_id: int = Path(gt=0)                      ):
            return {}

        @app.put("/items/{item_id:path}")                                               # Path parameter with regex
        def update_item_path(item_id: str):
            return {}

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()

            nested_route = [r for r in collection.routes                                # Check nested path params
                           if 'comments' in str(r.http_path)][0]
            assert len(nested_route.path_params) == 3
            param_names = [p.name for p in nested_route.path_params]
            assert 'user_id'    in param_names
            assert 'post_id'    in param_names
            assert 'comment_id' in param_names
            assert nested_route.path_params.obj() == [__(default     = None                ,
                                                         description = None                ,
                                                         required    = True                ,
                                                         name        = 'user_id'           ,
                                                         param_type  = 'builtins.int'      ),

                                                      __(default     = None                ,
                                                         description = 'The post Id'       ,
                                                         required    = True                ,
                                                         name        = 'post_id'           ,
                                                         param_type  = 'builtins.str'      ),

                                                      __(default     = None                ,
                                                         description = None                ,
                                                         required    = True                ,
                                                         name        = 'comment_id'        ,
                                                         param_type  = 'builtins.int'      )]


    def test_route_tags_extraction(self):                                              # Test route tags are properly extracted
        app = FastAPI()

        @app.get("/public", tags=["public", "v1"])
        def public_endpoint():
            return {}

        @app.post("/admin", tags=["admin", "internal"])
        def admin_endpoint():
            return {}

        @app.get("/no-tags")
        def no_tags_endpoint():
            return {}

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()

            public_route = [r for r in collection.routes if str(r.http_path) == '/public'][0]
            assert public_route.route_tags == ["public", "v1"]

            admin_route = [r for r in collection.routes if str(r.http_path) == '/admin'][0]
            assert admin_route.route_tags == ["admin", "internal"]

            no_tags_route = [r for r in collection.routes if str(r.http_path) == '/no-tags'][0]
            assert no_tags_route.route_tags == []


    def test_mixed_router_and_direct_routes(self):                                     # Test mixing router routes with direct app routes
        app = FastAPI()

        @app.get("/direct")
        def direct_route():
            return {}

        router1 = APIRouter(prefix="/api/v1", tags=["v1"])
        @router1.get("/users")
        def get_users_v1():
            return []

        router2 = APIRouter(prefix="/api/v2", tags=["v2"])
        @router2.get("/users")
        def get_users_v2():
            return []

        app.include_router(router1)
        app.include_router(router2)

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()
            paths = sorted([str(r.http_path) for r in collection.routes])
            assert paths == ['/api/v1/users', '/api/v2/users', '/direct']

            # Check tags are preserved
            v1_route = [r for r in collection.routes if '/v1/' in str(r.http_path)][0]
            assert 'v1' in v1_route.route_tags


    def test_special_characters_in_paths(self):                                        # Test paths with special characters
        app = FastAPI()

        @app.get("/path-with-dash")
        def dash_path():
            return {}

        @app.get("/path_with_underscore")
        def underscore_path():
            return {}

        @app.get("/path.with.dots")
        def dots_path():
            return {}

        @app.get("/path:with:colons")
        def colons_path():
            return {}

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()
            paths = [str(r.http_path) for r in collection.routes]

            assert paths == ['/path-with-dash'      ,
                             '/path_with_underscore',
                             '/path.with.dots'      ,
                             '/path:with:colons'    ]
            assert '/path-with-dash'        in paths
            assert '/path_with_underscore'  in paths
            assert '/path.with.dots'        in paths
            assert '/path:with:colons'      in paths


    def test_routes_with_dependencies(self):                                           # Test routes with FastAPI dependencies
        from fastapi import Depends

        app = FastAPI()

        def common_dependency():
            return {"dep": "value"}

        @app.get("/with-dep", dependencies=[Depends(common_dependency)])
        def route_with_dep():
            return {}

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()
            route = [r for r in collection.routes if str(r.http_path) == '/with-dep'][0]
            assert route.method_name == 'route_with_dep'
            # Dependencies don't affect extraction but route should still be found


    def test_exception_handling_in_extraction(self):                                   # Test handling of malformed routes
        with Fast_API__Route__Extractor(app=self.app) as _:
            # Test with None route
            result = _.extract__route_class(None)
            assert result == ''

            # Test with route missing attributes
            class MalformedRoute:
                path = "/test"
                # Missing methods attribute

            # Should handle gracefully
            result = _.is_default_route(None)
            assert result is False

            # Test empty path combination
            result = _.combine_paths(Safe_Str__Fast_API__Route__Prefix(''), '')
            assert result == '/'


    def test_options_and_head_methods(self):                                           # Test OPTIONS and HEAD methods specifically
        app = FastAPI()

        @app.options("/options-test")
        def options_handler():
            return {}

        @app.head("/head-test")
        def head_handler():
            return {}

        @app.api_route("/multi", methods=["GET", "HEAD", "OPTIONS"])
        def multi_method():
            return {}

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()

            options_route = [r for r in collection.routes
                            if str(r.http_path) == '/options-test'][0]
            assert Enum__Http__Method.OPTIONS in options_route.http_methods

            head_route = [r for r in collection.routes
                         if str(r.http_path) == '/head-test'][0]
            assert Enum__Http__Method.HEAD in head_route.http_methods

            multi_route = [r for r in collection.routes
                          if str(r.http_path) == '/multi'][0]
            assert len(multi_route.http_methods) == 3


    def test_route_name_extraction_edge_cases(self):                                   # Test edge cases in route naming
        app = FastAPI()

        # Lambda function
        app.get("/lambda")(lambda: {"test": "lambda"})

        # Function with special name
        @app.get("/special")
        def __special__name__():
            return {}

        # Class-based view
        class ItemView:
            def get(self):
                return {}

        item_view = ItemView()
        app.get("/class-view")(item_view.get)

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()

            lambda_route = [r for r in collection.routes
                           if str(r.http_path) == '/lambda'][0]
            assert lambda_route.method_name == '_lambda_'

            special_route = [r for r in collection.routes
                            if str(r.http_path) == '/special'][0]
            assert special_route.method_name == '__special__name__'

            class_route = [r for r in collection.routes
                          if str(r.http_path) == '/class-view'][0]
            assert class_route.method_name == 'get'


    def test_path_prefix_edge_cases(self):                                             # Test edge cases in path prefix handling
        with Fast_API__Route__Extractor(app=self.app) as _:
            # Multiple slashes
            result = _.combine_paths(Safe_Str__Fast_API__Route__Prefix('//api//'), '//users//')
            assert '//' not in result
            assert result == '/api/users'

            # Only slashes
            result = _.combine_paths(Safe_Str__Fast_API__Route__Prefix('/'), '/')
            assert result == '/'

            # Very long path
            long_segment = 'a' * 100
            result = _.combine_paths(Safe_Str__Fast_API__Route__Prefix(f'/{long_segment}'), f'/{long_segment}')
            assert len(result) > 200
            assert result == f'/{long_segment}/{long_segment}'


    def test_query_params_with_defaults(self):                                         # Test query parameters with default values
        app = FastAPI()

        @app.get("/search")
        def search(q: str, limit: int = 10, offset: int = 0, published: bool = True):
            return {}

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()

            assert collection.obj() == __(total_routes    = 1                                                         ,
                                          has_mounts      = False                                                     ,
                                          has_websockets  = False                                                     ,
                                          routes          = [__(is_default    = False                                 ,
                                                                is_mount      = False                                 ,
                                                                method_name   = 'search'                              ,
                                                                route_type    = 'api_route'                           ,
                                                                route_class   = 'test_Fast_API__Route__Extractor'     ,
                                                                route_tags    = []                                    ,
                                                                description   = ''                                    ,
                                                                path_params   = []                                    ,
                                                                query_params  = [__(default      = None             ,
                                                                                    description  = None             ,
                                                                                    required     = True             ,
                                                                                    name         = 'q'              ,
                                                                                    param_type   = 'builtins.str'   ),
                                                                                  __(default      = 10              ,
                                                                                     description  = None            ,
                                                                                     required     = False           ,
                                                                                     name         = 'limit'         ,
                                                                                     param_type   = 'builtins.int'  ),
                                                                                  __(default      = 0               ,
                                                                                     description  = None            ,
                                                                                     required     = False           ,
                                                                                     name         = 'offset'        ,
                                                                                     param_type   = 'builtins.int'  ),
                                                                                  __(default      = True            ,
                                                                                     description  = None            ,
                                                                                     required     = False           ,
                                                                                     name         = 'published'     ,
                                                                                     param_type   = 'builtins.bool' )],
                                                                body_params   = []                                    ,
                                                                return_type   = None                                  ,
                                                                http_path     = '/search'                             ,
                                                                http_methods  = [Enum__Http__Method.GET             ] )])

            route = collection.routes[0]

            # Check query params were extracted
            assert len(route.query_params) == 4

            # Check required vs optional
            q_param = [p for p in route.query_params if p.name == 'q'][0]
            assert q_param.required is True

            limit_param = [p for p in route.query_params if p.name == 'limit'][0]
            assert limit_param.required is False
            assert limit_param.default == 10


    def test_body_params_extraction(self):                                            # Test request body parameter extraction
        from pydantic import BaseModel

        app = FastAPI()

        class UserCreate(BaseModel):
            name: str
            email: str
            age: int = None

        @app.post("/users")
        def create_user(user: UserCreate, priority: int = 1):
            return {}

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()
            route = collection.routes[0]

            # Should have body param for user
            assert len(route.body_params) > 0
            user_param = [p for p in route.body_params if p.name == 'user'][0]
            assert 'UserCreate' in str(user_param.param_type)

            # Should also have query param for priority
            assert len(route.query_params) > 0


    def test_return_type_extraction(self):                                            # Test return type extraction
        from typing import List, Dict

        app = FastAPI()

        @app.get("/users")
        def get_users() -> List[Dict[str, str]]:
            return []

        @app.get("/count")
        def get_count() -> int:
            return 42

        @app.get("/void")
        def void_endpoint():
            pass

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()

            users_route = [r for r in collection.routes if str(r.http_path) == '/users'][0]
            assert users_route.return_type is not None
            assert users_route.return_type == list


            count_route = [r for r in collection.routes if str(r.http_path) == '/count'][0]
            assert count_route.return_type is int

            void_route = [r for r in collection.routes if str(r.http_path) == '/void'][0]
            assert void_route.return_type is None


    def test_description_extraction(self):                                            # Test extraction of parameter descriptions
        from fastapi import Query, Path, Body

        app = FastAPI()

        @app.post("/items/{item_id}")
        def create_item(item_id: int = Path (      description="The item's unique identifier"),
                        q      : str = Query(None, description="Search query string"         ),
                        data   : dict = Body (     description="Item data payload"           )
                   ) -> str:
            """Create a new item with the given data."""
            return {}

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()
            route = collection.routes[0]

            # Path param description
            path_param = route.path_params[0]
            assert path_param.description == "The item's unique identifier"

            # Query param description
            query_param = route.query_params[0]
            assert query_param.description == "Search query string"

            # Body param description
            body_param = route.body_params[0]
            assert body_param.description == "Item data payload"

            # Route description from docstring
            assert route.description == "Create a new item with the given data."

            assert collection.obj() == __(total_routes    = 1                                   ,
                                          has_mounts      = False                                ,
                                          has_websockets  = False                                ,
                                          routes          = [__(is_default    = False                                ,
                                                                is_mount      = False                                ,
                                                                method_name   = 'create_item'                          ,
                                                                route_type    = 'api_route'                            ,
                                                                route_class   = 'test_Fast_API__Route__Extractor'      ,
                                                                route_tags    = []                                     ,
                                                                description   = 'Create a new item with the given data.',
                                                                path_params   = [__(default      = None               ,
                                                                                    description  = "The item's unique identifier",
                                                                                    required     = True               ,
                                                                                    name         = 'item_id'          ,
                                                                                    param_type   = 'builtins.int'     )],
                                                                query_params  = [__(default      = None               ,
                                                                                    description  = 'Search query string',
                                                                                    required     = False              ,
                                                                                    name         = 'q'                ,
                                                                                    param_type   = 'builtins.str'     )],
                                                                body_params   = [__(default      = None               ,
                                                                                    description  = 'Item data payload',
                                                                                    required     = True               ,
                                                                                    name         = 'data'             ,
                                                                                    param_type   = 'builtins.dict'    )],
                                                                return_type   = 'builtins.str'                           ,
                                                                http_path     = '/items/{item_id}'                    ,
                                                                http_methods  = [Enum__Http__Method.POST              ] )])



    def test_route_with_no_params(self):                                              # Test routes with no parameters at all
        app = FastAPI()

        @app.get("/health")
        def health_check():
            return {"status": "ok"}

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()
            route = collection.routes[0]

            assert route.path_params  == []
            assert route.query_params == []
            assert route.body_params  == []
            assert route.return_type  is None


    def test_complex_type_safe_params__using__base_model(self):                                         # Test with Type_Safe parameters
        from osbot_utils.type_safe.Type_Safe import Type_Safe
        from pydantic                        import BaseModel

        class UserRequest(BaseModel):
            name: str
            age : int

        class UserResponse(BaseModel):
            id        : int
            name      : str
            created_at: str

        app = FastAPI()

        @app.post("/users")
        def create_user(user: UserRequest) -> UserResponse:
            return UserResponse(id=1, name=user.name, created_at="2024-01-01")

        with Fast_API__Route__Extractor(app=app) as _:
            collection = _.extract_routes()
            route = collection.routes[0]

            # Check body param is detected
            assert len(route.body_params) > 0
            assert 'UserRequest' in str(route.body_params[0].param_type)

            # Check return type is detected
            assert route.return_type is not None
            assert 'UserResponse' in str(route.return_type)

            assert collection.obj() == __(total_routes    = 1                                   ,
                                          has_mounts      = False                                ,
                                          has_websockets  = False                                ,
                                          routes          = [__(is_default    = False                                ,
                                                                is_mount      = False                                ,
                                                                method_name   = 'create_user'                          ,
                                                                route_type    = 'api_route'                            ,
                                                                route_class   = 'test_Fast_API__Route__Extractor'      ,
                                                                route_tags    = []                                     ,
                                                                description   = ''                                     ,
                                                                path_params   = []                                     ,
                                                                query_params  = []                                     ,
                                                                body_params   = [__(default      = None               ,
                                                                                    description  = None               ,
                                                                                    required     = True               ,
                                                                                    name         = 'user'             ,
                                                                                    param_type   = 'test_Fast_API__Route__Extractor.UserRequest')],
                                                                return_type   = 'test_Fast_API__Route__Extractor.UserResponse',
                                                                http_path     = '/users'                              ,
                                                                http_methods  = [Enum__Http__Method.POST              ] )])


    def test__bug__complex_type_safe_params__using__type_safe(self):                                         # Test with Type_Safe parameters
        from osbot_utils.type_safe.Type_Safe import Type_Safe

        class UserRequest(Type_Safe):
            name: str
            age : int

        class UserResponse(Type_Safe):
            id        : int
            name      : str
            created_at: str

        @route_path('/users')
        def create_user(user: UserRequest) -> UserResponse:
            return UserResponse(id=1, name=user.name, created_at="2024-01-01")

        fast_api = Fast_API()

        error_message = "Invalid args for response field! Hint: check that <class 'test_Fast_API__Route__Extractor.test_Fast_API__Route__Extractor.test__bug__complex_type_safe_params__using__type_safe.<locals>.UserResponse'> is a valid Pydantic field type. If you are using a return type annotation that is not a valid Pydantic field (e.g. Union[Response, dict, None]) you can disable generating the response model from the type annotation with the path operation decorator parameter response_model=None. Read more: https://fastapi.tiangolo.com/tutorial/response-model/"
        with pytest.raises(RuntimeError, match=re.escape(error_message)):
            fast_api.add_route_post(create_user)                            # BUG this should work, but it doesn't because the Fast_API class doesn't leverage the Type_Safe conversions from Fast_API__Routes

        fast_api_routes = Fast_API__Routes(router=fast_api.app_router(), app=fast_api.app())
        fast_api_routes.add_route_post(create_user)

        with Fast_API__Route__Extractor(app=fast_api.app()) as _:
            collection = _.extract_routes()

            #collection.print_obj()

            route = collection.routes[0]

            # Check body param is detected
            assert len(route.body_params) > 0
            type_safe__as__base_model = 'osbot_fast_api.api.transformers.Type_Safe__To__BaseModel.UserRequest__BaseModel'
            assert full_type_name(route.body_params[0].param_type) == type_safe__as__base_model # BUG this should be test_Fast_API__Route__Extractor.UserRequest

            # Check return type is detected
            #assert route.return_type is not None                           # BUG
            #assert 'UserResponse' in str(route.return_type)                # BUG
            assert route.return_type is None                                # BUG


            assert collection.obj() == __(total_routes    = 1                                   ,
                                          has_mounts      = False                                ,
                                          has_websockets  = False                                ,
                                          routes          = [__(is_default    = False                                ,
                                                                is_mount      = False                                ,
                                                                method_name   = 'create_user'                          ,
                                                                route_type    = 'api_route'                            ,
                                                                route_class  = 'test_Fast_API__Route__Extractor'      ,
                                                                route_tags    = []                                     ,
                                                                description   = ''                                     ,
                                                                path_params   = []                                     ,
                                                                query_params  = []                                     ,
                                                                body_params   = [__(default      = None               ,
                                                                                    description  = None               ,
                                                                                    required     = True               ,
                                                                                    name         = 'user'             ,
                                                                                    #param_type   = 'test_Fast_API__Route__Extractor.UserRequest',                                            # BUG
                                                                                    param_type   = 'osbot_fast_api.api.transformers.Type_Safe__To__BaseModel.UserRequest__BaseModel'          # BUG
                                                                                    )],
                                                                #return_type   = 'test_Fast_API__Route__Extractor.UserResponse',                    # BUG
                                                                return_type   = None                                  ,                             # BUG
                                                                http_path     = '/users'                              ,
                                                                http_methods  = [Enum__Http__Method.POST              ] )])
