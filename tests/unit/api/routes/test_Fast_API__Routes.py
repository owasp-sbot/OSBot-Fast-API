from unittest                                                                import TestCase
from fastapi                                                                 import FastAPI, APIRouter
from osbot_fast_api.api.routes.Fast_API__Routes                              import Fast_API__Routes
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix   import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag      import Safe_Str__Fast_API__Route__Tag
from osbot_fast_api.utils.Fast_API_Utils                                     import Fast_API_Utils


class test_Fast_API__Routes(TestCase):

    def setUp(self):
        self.app             = FastAPI()
        self.tag             = 'test_tag'
        self.fast_api_routes = Fast_API__Routes(app=self.app, tag=self.tag)

    def test__init__(self):
        assert type(self.fast_api_routes.router) is APIRouter
        assert type(self.fast_api_routes.app)    is FastAPI
        assert self.fast_api_routes.tag          == self.tag

    def test_add_route(self):
        expected_endpoints = [{ 'http_methods': ['GET' ], 'http_path': '/get-endpoint' , 'method_name': 'get_endpoint' },
                              { 'http_methods': ['POST'], 'http_path': '/post-endpoint', 'method_name': 'post_endpoint'}]
        expected_paths     = ['/get-endpoint', '/post-endpoint']
        expected_methods   = ['get_endpoint', 'post_endpoint'  ]
        def get_endpoint() : pass
        def post_endpoint(): pass
        assert self.fast_api_routes.add_route(function=get_endpoint , methods=['GET' ]) is self.fast_api_routes
        assert self.fast_api_routes.add_route(function=post_endpoint, methods=['POST']) is self.fast_api_routes
        assert self.fast_api_routes.routes        () == expected_endpoints
        assert self.fast_api_routes.routes_paths  () == expected_paths
        assert self.fast_api_routes.routes_methods() == expected_methods

    def test_add_route_get(self):
        def get_endpoint(): pass
        expected_endpoints = [ { 'http_methods': ['GET'], 'http_path': '/get-endpoint', 'method_name': 'get_endpoint'}]
        expected_paths     = ['/get-endpoint']
        expected_methods   = ['get_endpoint' ]
        assert self.fast_api_routes.add_route_get(get_endpoint) is self.fast_api_routes
        assert self.fast_api_routes.routes        () == expected_endpoints
        assert self.fast_api_routes.routes_paths  () == expected_paths
        assert self.fast_api_routes.routes_methods() == expected_methods

    def test_add_route_post(self):
        def post_endpoint(): pass
        expected_endpoints =  [ { 'http_methods': ['POST'], 'http_path': '/post-endpoint', 'method_name': 'post_endpoint'}]
        assert self.fast_api_routes.add_route_post(post_endpoint) is self.fast_api_routes
        assert self.fast_api_routes.routes() == expected_endpoints

    def test_fast_api_utils(self):
        assert type(self.fast_api_routes.fast_api_utils()) is Fast_API_Utils

    def test_routes(self):
        assert self.fast_api_routes.routes() == []


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

    def test__bug__any_route_loses_colon(self):
        def root_handler(): pass
        with Fast_API__Routes() as _:
            _.add_route_any(root_handler, "/{path:path")
            assert _.routes_paths() == ['/{path:path']
        with self.fast_api_routes as _:
            _.add_route_any(root_handler, "/{path:path")
            assert _.routes_paths() == ['/{path:path']

