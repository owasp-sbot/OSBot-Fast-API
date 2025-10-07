from unittest                                                               import TestCase
from fastapi                                                                import FastAPI, APIRouter
from osbot_utils.utils.Objects                                              import __
from osbot_fast_api.api.routes.Fast_API__Routes                             import Fast_API__Routes
from osbot_fast_api.api.routes.Type_Safe__Route__Registration               import Type_Safe__Route__Registration
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix  import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag     import Safe_Str__Fast_API__Route__Tag
from osbot_fast_api.utils.Fast_API_Utils                                    import Fast_API_Utils


class test_Fast_API__Routes(TestCase):

    def setUp(self):
        self.app             = FastAPI()
        self.tag             = 'test_tag'
        self.fast_api_routes = Fast_API__Routes(app=self.app, tag=self.tag)


    def test__tag_and_prefix(self):
        with Fast_API__Routes(tag='abc') as _:
            assert _.tag          == 'abc'
            assert _.prefix       == '/abc'
            assert type(_.tag   ) is Safe_Str__Fast_API__Route__Tag
            assert type(_.prefix) is Safe_Str__Fast_API__Route__Prefix

        with Fast_API__Routes(tag='a/bc') as _:
            assert _.tag    == 'a/bc'
            assert _.prefix == '/a/bc'

        with Fast_API__Routes(tag='a/b/c') as _:
            assert _.tag    == 'a/b/c'
            assert _.prefix == '/a/b/c'

        with Fast_API__Routes(tag='/a/b/c') as _:
            assert _.tag          == '/a/b/c'
            assert _.prefix       == '/a/b/c'
            assert type(_.tag   ) is Safe_Str__Fast_API__Route__Tag
            assert type(_.prefix) is Safe_Str__Fast_API__Route__Prefix


    def test__tag_and_prefix__edge_cases(self):
        # Empty tag (if allowed)
        with  Fast_API__Routes() as _:
            assert _.tag    == ''
            assert _.prefix == '/'

        # Tag with spaces
        with Fast_API__Routes(tag='User Management') as _:
            assert _.tag == 'User_Management'  # Spaces replaced
            assert _.prefix == '/user_management'

        # Tag with special characters
        with Fast_API__Routes(tag='api@v2#users') as _:
            assert _.tag == 'api_v2_users'  # Special chars replaced
            assert _.prefix == '/api_v2_users'

        # Very long tag
        long_tag = 'a' * 100 + '/b' * 50
        with Fast_API__Routes(tag=long_tag[:128]) as _:  # Assuming max length is 128
            assert len(_.tag) <= 128

        # Unicode characters
        with Fast_API__Routes(tag='用户/管理') as _:
            assert _.tag == '__/__'  # Non-ASCII replaced
            assert _.prefix == '/__/__'

        # Multiple consecutive slashes
        with Fast_API__Routes(tag='a//b///c') as _:
            assert _.tag == 'a//b///c'  # Tag preserves them
            assert _.prefix == '/a/b/c'  # Prefix cleans them

        # Explicit prefix overrides
        with Fast_API__Routes(tag='users', prefix='/custom/path') as _:
            assert _.tag == 'users'
            assert _.prefix == '/custom/path'

        # Both tag and prefix with type safety
        with Fast_API__Routes(tag    = Safe_Str__Fast_API__Route__Tag('USERS')          ,
                              prefix = Safe_Str__Fast_API__Route__Prefix('/API/V2/USERS')) as _:
            assert _.tag == 'USERS'  # Tag keeps case
            assert _.prefix == '/api/v2/users'  # Prefix lowercase

    def test_add_route_any(self):                               # Test with default path parsing
        def handle_any():
            return "any method"


        assert self.fast_api_routes.add_route_any(handle_any) is self.fast_api_routes
        routes = self.fast_api_routes.routes()

        assert len(routes)                                    == 1
        assert routes[0]['http_path']                         == '/handle-any'
        assert routes[0]['method_name']                       == 'handle_any'
        assert set(routes[0]['http_methods'])                 == {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}

    def test_add_route_any_with_explicit_path(self):          # Test with explicit path - common for proxy routes
        def proxy_request(path: str):
            return f"proxied: {path}"

        assert self.fast_api_routes.add_route_any(proxy_request, "/{path:path}") is self.fast_api_routes
        routes = self.fast_api_routes.routes()
        assert len(routes)                    == 1
        assert routes[0]['http_path']         == '/{path:path}'
        assert routes[0]['method_name']       == 'proxy_request'
        assert set(routes[0]['http_methods']) == {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}

    def test_add_route_any_with_multiple_routes(self):      # Test adding multiple ANY routes
        def catch_all(): pass
        def api_gateway(): pass
        def proxy(path: str): pass

        self.fast_api_routes.add_route_any(catch_all)
        self.fast_api_routes.add_route_any(api_gateway)
        self.fast_api_routes.add_route_any(proxy, "/api/{path:path}")

        routes = self.fast_api_routes.routes()
        assert len(routes) == 3

        # Check each route
        assert routes[0]['http_path'] == '/catch-all'
        assert routes[1]['http_path'] == '/api-gateway'
        assert routes[2]['http_path'] == '/api/{path:path}'

        # All should have same methods
        for route in routes:
            assert set(route['http_methods']) == {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}

    def test_add_route_any_with_path_parameters(self):                  # Test various path parameter patterns
        def get_item(item_id: int): pass
        def get_user_post(user_id: str, post_id: int): pass

        self.fast_api_routes.add_route_any(get_item, "/items/{item_id}")
        self.fast_api_routes.add_route_any(get_user_post, "/users/{user_id}/posts/{post_id}")

        routes = self.fast_api_routes.routes()
        assert routes[0]['http_path'] == '/items/{item_id}'
        assert routes[1]['http_path'] == '/users/{user_id}/posts/{post_id}'

    def test_add_route_any_edge_cases(self):                            # Test with root path
        def root_handler(): pass
        self.fast_api_routes.add_route_any(root_handler, "/")

        # Test with trailing slash
        def api_handler(): pass
        self.fast_api_routes.add_route_any(api_handler, "/api/")

        routes = self.fast_api_routes.routes()
        assert routes[0]['http_path'] == '/'
        assert routes[1]['http_path'] == '/api/'



    def test__init__(self):                                                         # Test Fast_API__Routes initialization
        with self.fast_api_routes as _:
            assert type(_)                     is Fast_API__Routes
            assert type(_.router)              is APIRouter
            assert type(_.app)                 is FastAPI
            assert type(_.route_registration)  is Type_Safe__Route__Registration
            assert _.tag                       == self.tag
            assert _.filter_tag                is True
            assert _.obj() == __(router             = 'APIRouter'                            ,
                                 app                = 'FastAPI'                              ,
                                 prefix             = '/test_tag'                            ,
                                 tag                = 'test_tag'                             ,
                                 filter_tag         = True                                   ,
                                 route_registration = __(analyzer        =__()              ,
                                                         converter       =__()              ,
                                                         wrapper_creator =__(converter=__()),
                                                         route_parser    =__()              ))

    def test__init__prefix_auto_generation(self):                                  # Test prefix auto-generated from tag
        with Fast_API__Routes(tag='abc') as _:
            assert _.tag          == 'abc'
            assert _.prefix       == '/abc'
            assert type(_.tag)    is Safe_Str__Fast_API__Route__Tag
            assert type(_.prefix) is Safe_Str__Fast_API__Route__Prefix

    def test__init__prefix_explicit(self):                                          # Test explicit prefix override
        with Fast_API__Routes(tag='users', prefix='/custom/path') as _:
            assert _.tag    == 'users'
            assert _.prefix == '/custom/path'

    def test_add_route(self):                                                       # Test adding routes with specified methods
        def get_endpoint():
            pass

        def post_endpoint():
            pass

        expected_endpoints = [{ 'http_methods': ['GET' ], 'http_path': '/get-endpoint' , 'method_name': 'get_endpoint' },
                              { 'http_methods': ['POST'], 'http_path': '/post-endpoint', 'method_name': 'post_endpoint'}]
        expected_paths     = ['/get-endpoint', '/post-endpoint']
        expected_methods   = ['get_endpoint', 'post_endpoint']

        with self.fast_api_routes as _:
            result_1 = _.add_route(function=get_endpoint , methods=['GET' ])
            result_2 = _.add_route(function=post_endpoint, methods=['POST'])

            assert result_1 is _                                                    # Method chaining support
            assert result_2 is _
            assert _.routes()         == expected_endpoints
            assert _.routes_paths()   == expected_paths
            assert _.routes_methods() == expected_methods

    def test_add_route_get(self):                                                   # Test GET route registration
        def get_endpoint():
            pass

        expected_endpoints = [{ 'http_methods': ['GET'], 'http_path': '/get-endpoint', 'method_name': 'get_endpoint'}]
        expected_paths     = ['/get-endpoint']
        expected_methods   = ['get_endpoint']

        with self.fast_api_routes as _:
            result = _.add_route_get(get_endpoint)

            assert result is _                                                      # Method chaining
            assert _.routes()         == expected_endpoints
            assert _.routes_paths()   == expected_paths
            assert _.routes_methods() == expected_methods

    def test_add_route_post(self):                                                  # Test POST route registration
        def post_endpoint():
            pass

        expected_endpoints = [{ 'http_methods': ['POST'], 'http_path': '/post-endpoint', 'method_name': 'post_endpoint'}]

        with self.fast_api_routes as _:
            result = _.add_route_post(post_endpoint)

            assert result is _
            assert _.routes() == expected_endpoints

    def test_add_route_put(self):                                                   # Test PUT route registration
        def put_endpoint():
            pass

        with self.fast_api_routes as _:
            result = _.add_route_put(put_endpoint)

            assert result is _
            assert len(_.routes())        == 1
            assert _.routes()[0]['http_methods'] == ['PUT']

    def test_add_route_delete(self):                                                # Test DELETE route registration
        def delete_endpoint():
            pass

        with self.fast_api_routes as _:
            result = _.add_route_delete(delete_endpoint)

            assert result is _
            assert len(_.routes())        == 1
            assert _.routes()[0]['http_methods'] == ['DELETE']

    def test_add_route_any__default_path(self):                                     # Test ANY method with default path parsing
        def handle_any():
            return "any method"

        with self.fast_api_routes as _:
            result = _.add_route_any(handle_any)
            routes = _.routes()

            assert result is _
            assert len(routes)                    == 1
            assert routes[0]['http_path']         == '/handle-any'
            assert routes[0]['method_name']       == 'handle_any'
            assert set(routes[0]['http_methods']) == {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}

    def test_add_route_any__explicit_path(self):                                    # Test ANY method with explicit path
        def proxy_request(path: str):
            return f"proxied: {path}"

        with self.fast_api_routes as _:
            result = _.add_route_any(proxy_request, "/{path:path}")
            routes = _.routes()

            assert result is _
            assert len(routes)                    == 1
            assert routes[0]['http_path']         == '/{path:path}'
            assert routes[0]['method_name']       == 'proxy_request'
            assert set(routes[0]['http_methods']) == {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}

    def test_add_route_any__multiple_routes(self):                                  # Test adding multiple ANY routes
        def catch_all():
            pass

        def api_gateway():
            pass

        def proxy(path: str):
            pass

        with self.fast_api_routes as _:
            _.add_route_any(catch_all)
            _.add_route_any(api_gateway)
            _.add_route_any(proxy, "/api/{path:path}")

            routes = _.routes()
            assert len(routes) == 3

            assert routes[0]['http_path'] == '/catch-all'
            assert routes[1]['http_path'] == '/api-gateway'
            assert routes[2]['http_path'] == '/api/{path:path}'

            for route in routes:                                                    # All should have same methods
                assert set(route['http_methods']) == {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}

    def test_add_routes_get(self):                                                  # Test batch GET route registration
        def endpoint_1():
            pass

        def endpoint_2():
            pass

        def endpoint_3():
            pass

        with self.fast_api_routes as _:
            result = _.add_routes_get(endpoint_1, endpoint_2, endpoint_3)

            assert result is _                                                      # Method chaining
            assert len(_.routes()) == 3
            assert _.routes_paths() == ['/endpoint-1', '/endpoint-2', '/endpoint-3']

    def test_add_routes_post(self):                                                 # Test batch POST route registration
        def endpoint_1():
            pass

        def endpoint_2():
            pass

        with self.fast_api_routes as _:
            result = _.add_routes_post(endpoint_1, endpoint_2)

            assert result is _
            assert len(_.routes()) == 2
            for route in _.routes():
                assert route['http_methods'] == ['POST']

    def test_add_routes_put(self):                                                  # Test batch PUT route registration
        def endpoint_1():
            pass

        def endpoint_2():
            pass

        with self.fast_api_routes as _:
            result = _.add_routes_put(endpoint_1, endpoint_2)

            assert result is _
            assert len(_.routes()) == 2
            for route in _.routes():
                assert route['http_methods'] == ['PUT']

    def test_add_routes_delete(self):                                               # Test batch DELETE route registration
        def endpoint_1():
            pass

        def endpoint_2():
            pass

        with self.fast_api_routes as _:
            result = _.add_routes_delete(endpoint_1, endpoint_2)

            assert result is _
            assert len(_.routes()) == 2
            for route in _.routes():
                assert route['http_methods'] == ['DELETE']

    def test_fast_api_utils(self):                                                  # Test utility helper access
        with self.fast_api_routes as _:
            utils = _.fast_api_utils()

            assert type(utils) is Fast_API_Utils

    def test_routes(self):                                                          # Test routes() returns empty list initially
        with self.fast_api_routes as _:
            assert _.routes() == []

    def test_routes_methods(self):                                                  # Test routes_methods() extracts method names
        def method_a():
            pass

        def method_b():
            pass

        def method_c():
            pass

        with self.fast_api_routes as _:
            _.add_routes_get(method_a, method_b, method_c)

            assert _.routes_methods() == ['method_a', 'method_b', 'method_c']

    def test_routes_paths(self):                                                    # Test routes_paths() extracts and sorts paths
        def zebra():
            pass

        def alpha():
            pass

        def beta():
            pass

        with self.fast_api_routes as _:
            _.add_routes_get(zebra, alpha, beta)

            assert _.routes_paths() == ['/alpha', '/beta', '/zebra']                # Sorted alphabetically

    def test_tag_and_prefix__with_slashes(self):                                    # Test tag/prefix with slash characters
        with Fast_API__Routes(tag='a/bc') as _:
            assert _.tag    == 'a/bc'
            assert _.prefix == '/a/bc'

        with Fast_API__Routes(tag='a/b/c') as _:
            assert _.tag    == 'a/b/c'
            assert _.prefix == '/a/b/c'

        with Fast_API__Routes(tag='/a/b/c') as _:
            assert _.tag          == '/a/b/c'
            assert _.prefix       == '/a/b/c'
            assert type(_.tag)    is Safe_Str__Fast_API__Route__Tag
            assert type(_.prefix) is Safe_Str__Fast_API__Route__Prefix

    def test_tag_and_prefix__edge_cases(self):                                      # Test edge cases for tag/prefix handling
        with Fast_API__Routes() as _:                                               # Empty tag
            assert _.tag    == ''
            assert _.prefix == '/'

        with Fast_API__Routes(tag='User Management') as _:                          # Spaces in tag
            assert _.tag    == 'User_Management'
            assert _.prefix == '/user_management'

        with Fast_API__Routes(tag='api@v2#users') as _:                             # Special characters
            assert _.tag    == 'api_v2_users'
            assert _.prefix == '/api_v2_users'

        with Fast_API__Routes(tag='用户/管理') as _:                                # Unicode characters
            assert _.tag    == '__/__'
            assert _.prefix == '/__/__'

        with Fast_API__Routes(tag='a//b///c') as _:                                 # Multiple consecutive slashes
            assert _.tag    == 'a//b///c'
            assert _.prefix == '/a/b/c'

    def test_tag_and_prefix__with_safe_types(self):                                 # Test explicit Safe type initialization
        with Fast_API__Routes(tag    = Safe_Str__Fast_API__Route__Tag('USERS')          ,
                              prefix = Safe_Str__Fast_API__Route__Prefix('/API/V2/USERS')) as _:
            assert _.tag    == 'USERS'
            assert _.prefix == '/api/v2/users'

    def test_any_route__doesnt__lose_colon(self):
        def root_handler():
            pass

        with Fast_API__Routes() as _:
            _.add_route_any(root_handler, "/{path:path}")
            assert _.routes_paths() == ['/{path:path}']                             # Colon preserved

        routes = Fast_API__Routes()
        routes.add_route_any(root_handler, "/{path:path}")
        assert routes.routes_paths() == ['/{path:path}']

    def test_setup__with_root_prefix(self):                                         # Test setup() with root-level routes
        app = FastAPI()

        class Test_Routes(Fast_API__Routes):
            tag = 'test'

            def endpoint(self):
                pass

            def setup_routes(self):
                self.add_route_get(self.endpoint)

        routes = Test_Routes(app=app, prefix='/')
        routes.setup()

        from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils
        utils = Fast_API_Utils(app)
        all_routes = utils.fastapi_routes()

        route_paths = [r['http_path'] for r in all_routes]
        assert '/endpoint' in route_paths                                           # No prefix for root

    def test_setup__with_custom_prefix(self):                                       # Test setup() with custom prefix
        app = FastAPI()

        class Test_Routes(Fast_API__Routes):
            tag = 'test'

            def endpoint(self):
                pass

            def setup_routes(self):
                self.add_route_get(self.endpoint)

        routes = Test_Routes(app=app, prefix='/custom')
        routes.setup()

        from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils
        utils = Fast_API_Utils(app)
        all_routes = utils.fastapi_routes()

        route_paths = [r['http_path'] for r in all_routes]
        assert '/custom/endpoint' in route_paths