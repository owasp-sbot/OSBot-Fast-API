from unittest import TestCase

from fastapi import FastAPI
from osbot_utils.utils.Dev import pprint
from starlette.testclient import TestClient

from osbot_fast_api.api.Fast_API         import Fast_API
from osbot_fast_api.api.routers.Router_Status import ROUTE_STATUS__ROUTES
from osbot_fast_api.utils.Fast_API_Utils import FAST_API_DEFAULT_ROUTES

from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils


class test_Fast_API(TestCase):

    def setUp(self):
        self.fast_api = Fast_API()
        self.client   = self.fast_api.client()

    def test__init__(self):
        assert type(self.fast_api.app()) is FastAPI

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
        assert dict(response.headers) == {'content-length': '0', 'location': '/docs'}

    def test_routes(self):
        expected_routes = FAST_API_DEFAULT_ROUTES + ROUTE_STATUS__ROUTES
        routes          = self.fast_api.routes(include_default=True)
        assert routes == expected_routes

    def test_setup_routes(self):
        assert self.fast_api.setup_routes() == self.fast_api

    def test_user_middleware(self):
        assert self.fast_api.user_middleware() == []