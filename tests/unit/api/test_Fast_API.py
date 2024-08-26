from unittest import TestCase

from fastapi import FastAPI
from flask import Flask
from starlette.testclient                       import TestClient
from osbot_fast_api.api.Fast_API                import Fast_API, DEFAULT__NAME__FAST_API
from osbot_fast_api.api.routes.Routes_Config    import ROUTES__CONFIG
from osbot_fast_api.utils.Fast_API_Utils        import FAST_API_DEFAULT_ROUTES
from osbot_fast_api.utils.Fast_API_Utils        import Fast_API_Utils
from osbot_utils.utils.Dev import pprint
from tests.unit.fast_api__for_tests import fast_api, fast_api_client

EXPECTED_ROUTES_METHODS = ['redirect_to_docs', 'status', 'version']
EXPECTED_ROUTES_PATHS   = ['/', '/config/status', '/config/version']
EXPECTED_DEFAULT_ROUTES = ['/docs', '/docs/oauth2-redirect', '/openapi.json', '/redoc']

class test_Fast_API(TestCase):

    def setUp(self):
        self.fast_api = fast_api        #Fast_API().setup()
        self.client   = fast_api_client # self.fast_api.client()

    def test__init__(self):
        assert type(self.fast_api.app()) is FastAPI

    def test_add_flask_app(self):
        path      = '/flask-app'
        flask_app = Flask(__name__)

        @flask_app.route('/flask-route')
        def hello_flask():
            return "Hello from Flask!"

        with self.fast_api as _:
            _.add_flask_app(path, flask_app)
            assert _.routes_paths(expand_mounts=True) == EXPECTED_ROUTES_PATHS + ['/flask-app']
            assert _.client().get('/flask-app/flask-route').text == 'Hello from Flask!'
            assert _.route_remove('/flask-app') is True
            assert _.route_remove('/flask-app') is False
            assert _.routes_paths(expand_mounts=True) == EXPECTED_ROUTES_PATHS

    def test_app(self):
        app = self.fast_api.app()
        assert type(app) == FastAPI
        assert app.openapi_version      == '3.1.0'
        assert app.debug                is False
        assert app.docs_url             == '/docs'
        assert app.dependency_overrides == {}
        assert app.openapi_url          == '/openapi.json'
        assert app.title                == 'FastAPI'
        assert app.version              == '0.1.0'

        assert self.fast_api.enable_cors is False

    def test_client(self):
        assert type(self.client) is TestClient

    def test_fast_api_utils(self):
        fast_api_utils = self.fast_api.fast_api_utils()
        assert type(fast_api_utils)    is Fast_API_Utils
        assert fast_api_utils.app      == self.fast_api.app()

    def test_path_static_folder(self):
        assert self.fast_api.path_static_folder() is None

    def test_route__root(self):
        response = self.client.get('/', follow_redirects=False)
        assert response.status_code == 307
        assert response.headers.get('location') == '/docs'
        fast_api_request_id = response.headers.get('fast-api-request-id')
        assert dict(response.headers) == {'content-length': '0', 'location': '/docs', 'fast-api-request-id': fast_api_request_id}

    def test_routes(self):
        expected_routes = FAST_API_DEFAULT_ROUTES + ROUTES__CONFIG
        routes          = self.fast_api.routes(include_default=True)
        assert routes == expected_routes

    def test_routes_methods(self):
        routes_methods         = self.fast_api.routes_methods()
        assert routes_methods == EXPECTED_ROUTES_METHODS

    def test_routes_paths(self):
        assert self.fast_api.routes_paths(                     ) == EXPECTED_ROUTES_PATHS
        assert self.fast_api.routes_paths(include_default=False) == EXPECTED_ROUTES_PATHS
        assert self.fast_api.routes_paths(include_default=True ) == EXPECTED_ROUTES_PATHS + EXPECTED_DEFAULT_ROUTES

    def test_setup_routes(self):
        assert self.fast_api.setup_routes() == self.fast_api

    def test_user_middleware(self):
        http_events = self.fast_api.http_events
        params = {'http_events' : http_events}
        assert self.fast_api.user_middlewares() == [{'function_name': None, 'params': params, 'type': 'Middleware__Http_Request'             },
                                                    {'function_name': None, 'params': params, 'type': 'Middleware__Http_Request__Trace_Calls'}]