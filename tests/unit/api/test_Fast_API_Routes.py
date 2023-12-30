from unittest                               import TestCase
from fastapi                                import FastAPI, APIRouter
from osbot_fast_api.api.Fast_API_Routes     import Fast_API_Routes
from osbot_fast_api.utils.Fast_API_Utils    import Fast_API_Utils


class test_Fast_API_Router(TestCase):

    def setUp(self):
        self.app             = FastAPI()
        self.tag             = 'test_tag'
        self.fast_api_router = Fast_API_Routes(app=self.app, tag=self.tag)

    def test__init__(self):
        assert type(self.fast_api_router.router) is APIRouter
        assert type(self.fast_api_router.app)    is FastAPI
        assert self.fast_api_router.tag          == self.tag

    def test_add_route(self):
        expected_endpoints = [{ 'http_methods': ['GET' ], 'http_path': '/get-endpoint' , 'method_name': 'get_endpoint' },
                              { 'http_methods': ['POST'], 'http_path': '/post-endpoint', 'method_name': 'post_endpoint'}]
        expected_paths     = ['/get-endpoint', '/post-endpoint']
        expected_methods   = ['get_endpoint', 'post_endpoint'  ]
        def get_endpoint() : pass
        def post_endpoint(): pass
        assert self.fast_api_router.add_route(function=get_endpoint , methods=['GET' ]) is self.fast_api_router
        assert self.fast_api_router.add_route(function=post_endpoint, methods=['POST']) is self.fast_api_router
        assert self.fast_api_router.routes        () == expected_endpoints
        assert self.fast_api_router.routes_paths  () == expected_paths
        assert self.fast_api_router.routes_methods() == expected_methods

    def test_add_route_get(self):
        def get_endpoint(): pass
        expected_endpoints = [ { 'http_methods': ['GET'], 'http_path': '/get-endpoint', 'method_name': 'get_endpoint'}]
        expected_paths     = ['/get-endpoint']
        expected_methods   = ['get_endpoint' ]
        assert self.fast_api_router.add_route_get(get_endpoint) is self.fast_api_router
        assert self.fast_api_router.routes        () == expected_endpoints
        assert self.fast_api_router.routes_paths  () == expected_paths
        assert self.fast_api_router.routes_methods() == expected_methods

    def test_add_route_post(self):
        def post_endpoint(): pass
        expected_endpoints =  [ { 'http_methods': ['POST'], 'http_path': '/post-endpoint', 'method_name': 'post_endpoint'}]
        assert self.fast_api_router.add_route_post(post_endpoint) is self.fast_api_router
        assert self.fast_api_router.routes() == expected_endpoints

    def test_fast_api_utils(self):
        assert type(self.fast_api_router.fast_api_utils()) is Fast_API_Utils

    def test_routes(self):
        assert self.fast_api_router.routes() == []


