from unittest import TestCase

from fastapi import FastAPI
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, folder_name, files_names, files_list

from osbot_fast_api.api.Fast_API                          import Fast_API
from osbot_fast_api.examples.ex_1_simple.Fast_API__Simple import Fast_API__Simple, EX_1__FOLDER_NAME__STATIC_FOLDER


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
        pprint(response.headers)

        response = self.client.head('/docs')
        pprint(response.headers)


    def test_route__root(self):
        response = self.client.get('/', follow_redirects=False)
        assert response.status_code == 307
        assert response.headers.get('location') == '/docs'
        assert dict(response.headers) == {'content-length': '0', 'location': '/docs'}

    def test_routes(self):
        routes = self.fast_api.routes()
        assert routes == [{'http_methods': ['GET'        ], 'http_path': '/'      , 'method_name': 'redirect_to_docs'},
                          {'http_methods': ['GET', 'HEAD'], 'http_path': '/static', 'method_name': 'static'          }]

    def test_user_middleware(self):
        middlewares = self.fast_api.user_middleware()
        middleware  = middlewares[0]
        assert len(middlewares)  == 1
        assert str(middleware) == "Middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['GET', 'POST', 'HEAD'], allow_headers=['Content-Type', 'X-Requested-With', 'Origin', 'Accept', 'Authorization'], expose_headers=['Content-Type', 'X-Requested-With', 'Origin', 'Accept', 'Authorization'])"
