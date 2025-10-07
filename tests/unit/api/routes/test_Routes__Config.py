from unittest                                   import TestCase
from fastapi                                    import FastAPI
from starlette.testclient                       import TestClient
from osbot_fast_api.api.routes.Routes__Config   import Routes__Config
from osbot_fast_api.utils.Version               import Version


class test_Routes__Config(TestCase):

    def setUp(self):
        self.app           = FastAPI()
        self.routes_config = Routes__Config(app=self.app).setup()
        self.client        = TestClient(self.app)

    def test__init__(self):
        assert type(self.routes_config) is Routes__Config
        assert self.routes_config.tag    == 'config'
        assert self.routes_config.app    == self.app
        assert self.routes_config.router is not None

    def test_client__status(self):
        response = self.client.get("/config/status")
        assert response.status_code == 200
        assert response.json()      == {'status': 'ok'}

    def test_client__version(self):
        response = self.client.get("/config/version")
        assert response.status_code == 200
        assert response.json() == {'version': Version().value()}

    def test_routes(self):
        expected_routes = [{'http_methods': ['GET'], 'http_path': '/info'       , 'method_name': 'info'          },
                           {'http_methods': ['GET'], 'http_path': '/status'     , 'method_name': 'status'        },
                           {'http_methods': ['GET'], 'http_path': '/version'    , 'method_name': 'version'       },
                           #{'http_methods': ['GET'], 'http_path': '/routes/json', 'method_name': 'routes__json'  },
                           #{'http_methods': ['GET'], 'http_path': '/routes/html', 'method_name': 'routes__html'  },
                           {'http_methods': ['GET'], 'http_path': '/openapi.py' , 'method_name': 'openapi_python'}]
        assert self.routes_config.routes() == expected_routes
