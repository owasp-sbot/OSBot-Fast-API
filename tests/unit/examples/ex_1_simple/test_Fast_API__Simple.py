from unittest import TestCase

from fastapi import FastAPI
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, folder_name, files_names, files_list

from osbot_fast_api.api.Fast_API                          import Fast_API
from osbot_fast_api.api.routers.Router_Status             import ROUTER_STATUS__ROUTES
from osbot_fast_api.examples.ex_1_simple.Fast_API__Simple import Fast_API__Simple, EX_1__FOLDER_NAME__STATIC_FOLDER, \
    EX_1_ROUTES


class test_Fast_API__Simple(TestCase):

    def setUp(self):
        self.enable_cors = True
        self.fast_api    = Fast_API__Simple(enable_cors=self.enable_cors)
        self.client       = self.fast_api.client()

    def test__init__(self):
        assert isinstance(self.fast_api, Fast_API__Simple)
        assert isinstance(self.fast_api, Fast_API        )
        assert type(self.fast_api.app()) is FastAPI
        assert self.fast_api.enable_cors is True

        print(self.fast_api.app().user_middleware)

    def test_path_static_folder(self):
        static_folder = self.fast_api.path_static_folder()
        assert static_folder is not None
        assert folder_exists(static_folder) is True
        assert folder_name(static_folder)   == EX_1__FOLDER_NAME__STATIC_FOLDER
        assert files_names(files_list(static_folder)) == ['aaa.txt']

    def test_route__docs(self):
        response = self.client.get('/docs')
        assert response.status_code == 200
        assert '<title>FastAPI - Swagger UI</title>' in response.text
        assert dict(response.headers) == {'content-length': '939', 'content-type': 'text/html; charset=utf-8'}

    def test_route__root(self):
        response = self.client.get('/', follow_redirects=False)
        assert response.status_code == 307
        assert response.headers.get('location') == '/docs'
        assert dict(response.headers) == {'content-length': '0', 'location': '/docs'}

    def test_routes(self):
        routes = self.fast_api.routes()
        assert (routes == EX_1_ROUTES + ROUTER_STATUS__ROUTES)

    def test_static_file(self):
        response = self.client.get('/static/aaa.txt')
        assert response.status_code == 200
        assert response.text        == 'this is a static file'

    def test_user_middleware(self):
        middlewares = self.fast_api.user_middleware()
        middleware  = middlewares[0]
        assert len(middlewares)  == 1
        assert str(middleware) == "Middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['GET', 'POST', 'HEAD'], allow_headers=['Content-Type', 'X-Requested-With', 'Origin', 'Accept', 'Authorization'], expose_headers=['Content-Type', 'X-Requested-With', 'Origin', 'Accept', 'Authorization'])"


    # BUGS

    def test_bug___CORS_headers_are_not_showing_in_headers(self):
        assert self.enable_cors is True
        response = self.client.get('/docs')
        assert dict(response.headers) == {'content-length': '939', 'content-type': 'text/html; charset=utf-8'} # bug: the cors heaaders should show here