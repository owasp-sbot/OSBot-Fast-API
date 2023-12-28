from unittest import TestCase

from fastapi import FastAPI
from starlette.testclient import TestClient

from osbot_fast_api.api.Fast_API         import Fast_API
from osbot_fast_api.utils.Fast_API_Utils import FAST_API_DEFAULT_ROUTES

from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils


class test_Fast_API(TestCase):

    def setUp(self):
        self.fast_api = Fast_API()
        self.app    = self.fast_api.app()
        self.client = TestClient(self.app)

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

    def test_fast_api_utils(self):
        fast_api_utils = self.fast_api.fast_api_utils()
        assert type(fast_api_utils)    is Fast_API_Utils
        assert fast_api_utils.fast_api == self.fast_api

    def test_path_static_folder(self):
        assert self.fast_api.path_static_folder() is None

    def test_routes(self):
        expected_routes = FAST_API_DEFAULT_ROUTES
        routes          = self.fast_api.routes(include_default=True)
        assert routes == expected_routes