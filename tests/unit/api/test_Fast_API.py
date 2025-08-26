import re
import pytest
from unittest                                                        import TestCase
from fastapi                                                         import FastAPI
from osbot_utils.type_safe.primitives.safe_str.git.Safe_Str__Version import Safe_Str__Version
from osbot_utils.type_safe.primitives.safe_str.text.Safe_Str__Text   import Safe_Str__Text
from starlette.testclient                                            import TestClient
from osbot_fast_api.api.Fast_API                                     import Fast_API
from osbot_fast_api.schemas.Safe_Str__Fast_API__Name                 import Safe_Str__Fast_API__Name
from osbot_fast_api.schemas.consts__Fast_API                         import EXPECTED_ROUTES_PATHS, EXPECTED_ROUTES_METHODS, EXPECTED_DEFAULT_ROUTES, ROUTES__CONFIG, ROUTES__STATIC_DOCS, FAST_API_DEFAULT_ROUTES
from osbot_fast_api.utils.Fast_API_Utils                             import Fast_API_Utils
from osbot_fast_api.utils.Version                                    import version__osbot_fast_api
from tests.unit.fast_api__for_tests                                  import fast_api, fast_api_client


class test_Fast_API(TestCase):

    def setUp(self):
        self.fast_api = fast_api        # Fast_API().setup()
        self.client   = fast_api_client # self.fast_api.client()

    def test__init__(self):
        assert type(self.fast_api.app()) is FastAPI

    
    def test_add_flask_app(self):
        flask = pytest.importorskip("flask", reason="Flask is not installed")       # noqa
        from flask import Flask                                                     # noqa
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
        #assert app.docs_url             == '/docs'
        assert app.dependency_overrides == {}
        assert app.openapi_url          == '/openapi.json'
        assert app.title                == 'Fast_API'
        assert app.version              == version__osbot_fast_api

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
        expected_routes = FAST_API_DEFAULT_ROUTES + ROUTES__CONFIG + ROUTES__STATIC_DOCS
        routes          = self.fast_api.routes(include_default=True)
        assert routes == expected_routes

    def test_routes_methods(self):
        routes_methods         = self.fast_api.routes_methods()
        assert routes_methods == EXPECTED_ROUTES_METHODS

    def test_routes_paths(self):
        assert self.fast_api.routes_paths(                     ) == sorted(EXPECTED_ROUTES_PATHS)
        assert self.fast_api.routes_paths(include_default=False) == sorted(EXPECTED_ROUTES_PATHS)
        assert self.fast_api.routes_paths(include_default=True ) == sorted(EXPECTED_ROUTES_PATHS + EXPECTED_DEFAULT_ROUTES)

    def test_setup_routes(self):
        assert self.fast_api.setup_routes() == self.fast_api

    def test_user_middleware(self):
        http_events = self.fast_api.http_events
        params = {'http_events' : http_events}
        assert self.fast_api.user_middlewares() == [{'function_name': None, 'params': params, 'type': 'Middleware__Http_Request'     },
                                                    {'function_name': None, 'params': {}     ,'type': 'Middleware__Detect_Disconnect'}]

    def test__verify__title_description_version(self):

        app = self.fast_api.app()
        assert type(app) is FastAPI
        assert app.title       == 'Fast_API'
        assert app.version     == version__osbot_fast_api
        assert app.description == ''

        kwargs = dict(name        = 'An Fast API !!',
                      version     = 'v0.1.0'        ,
                      description = 'now with more available charts to talk about Fast API !! @£$%^&*()')
        with Fast_API(**kwargs) as _:
            assert _.name       == 'An Fast API __'                                                         # note the chars sanitization
            assert _.version    ==  'v0.1.0'
            assert _.description == 'now with more available charts to talk about Fast API __ ______*()'    # note the chars sanitization

            assert type(_.name       ) is Safe_Str__Fast_API__Name
            assert type(_.version    ) is Safe_Str__Version
            assert type(_.description) is Safe_Str__Text

            app = _.app()
            assert type(app) is FastAPI
            assert app.title         == Safe_Str__Fast_API__Name('An Fast API __')
            assert app.version       == Safe_Str__Version        ('v0.1.0')
            assert app.description   == Safe_Str__Text('now with more available charts to talk about Fast API __ ______*()')

        error_message = 'Value does not match required pattern: ^v(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})$'
        with pytest.raises(ValueError, match=re.escape(error_message)):
            Fast_API(version="0.1.1")                                       # confirm validation provided by Safe_Str__Version



