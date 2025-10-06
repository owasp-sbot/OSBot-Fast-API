import unittest

from osbot_fast_api.api.schemas.Schema__Fast_API__Config import Schema__Fast_API__Config
from osbot_utils.utils.Misc                                 import list_set
from osbot_utils.utils.Objects                              import class_functions
from osbot_fast_api.api.Fast_API                            import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes             import Fast_API__Routes
from osbot_fast_api.api.routes.Routes__Config               import Routes__Config
from osbot_fast_api.api.transformers.OpenAPI__To__Python    import OpenAPI__To__Python
from osbot_fast_api.api.schemas.consts.consts__Fast_API         import EXPECTED_ROUTES_PATHS
from osbot_fast_api.utils.Fast_API_Server                   import Fast_API_Server
from osbot_fast_api.utils.Version                           import version__osbot_fast_api

class test_OpenAPI__To__Python(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.fast_api         = cls.util__create_test_fast_api_server()
        cls.openai_to_python = OpenAPI__To__Python()
        cls.fast_api__server =  Fast_API_Server(app=cls.fast_api.app())
        cls.fast_api__url    =  cls.fast_api__server.url()
        cls.fast_api__server.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fast_api__server.stop()

    @staticmethod
    def util__create_test_fast_api_server():
        class Routes__Ping(Fast_API__Routes):
            tag = 'ping'

            def now(self):
                return 'pong'

            def setup_routes(self):
                self.add_routes_get(self.now)

        class Fast_API__Ping(Fast_API):
            def setup_routes(self):
                self.add_routes(Routes__Ping)

        config   = Schema__Fast_API__Config(default_routes=False)
        fast_api = Fast_API__Ping(config=config).setup()
        return fast_api

    def util__create_client_instance__from__client_code(self, client_python_code):
        namespace = {}                                                                              # namespace far that will hold the compiled classes
        exec(client_python_code, namespace)                                                         # compile code and put it in the namespace dict
        Fast_API__Client__Config = namespace['Fast_API__Client__Config']                            # get config class: Fast_API__Client__Config
        Client__Fast_API_Ping    = namespace['Client__Fast_API_Ping'   ]                            # get fast api class: Client__Fast_API_Ping

        config = Fast_API__Client__Config(base_url=self.fast_api__url)                              # Use the dynamically created classes
        client = Client__Fast_API_Ping   (config=config)
        return client

    def test_1__setUpClass(self):
        with self.fast_api  as _:
            assert isinstance(_, Fast_API)
            assert _.routes_paths()  == [ '/ping/now']
            assert _.open_api_json() == { 'info'   : {'title': 'Fast_API__Ping', 'version': version__osbot_fast_api},
                                          'openapi': '3.1.0',
                                          'paths'  : { '/ping/now': { 'get': {  'operationId': 'now_ping_now_get',
                                                                                'responses'  : { '200': { 'content'    : { 'application/json': { 'schema': { }}},
                                                                                                         'description': 'Successful Response'}},
                                                                                'summary'    : 'Now',
                                                                                'tags'       : ['ping']}}}}
        assert self.fast_api__server.running is True
        assert self.fast_api__url            == f'http://127.0.0.1:{self.fast_api__server.port}/'

    def test_2__generate_from_app(self):
        client__python_code = self.openai_to_python.generate_from_app(self.fast_api.app())             # generate the python code with the client
        client              = self.util__create_client_instance__from__client_code(client__python_code)
        assert client.get_ping_now() == 'pong'                                                  # todo: BUG: this should just be client.get__ping_now()

    def test_3__generate_from_route(self):
        with self.fast_api as _:
            _.add_routes(Routes__Config)                                                            # add the Routes__Config
            response__openapi_py = _.client().get('/config/openapi.py')                             # invoke it
            client__python_code  = response__openapi_py.text  # get python client code
            client               = self.util__create_client_instance__from__client_code(client__python_code)
            assert client.get_ping_now() == 'pong'                                                  # todo: BUG: this should just be client.get__ping_now()

    def test_4__check_client_on_test_fast_api(self):
        from tests.unit.fast_api__for_tests import fast_api                                             # let's use the main fast_api instance used in most tests
        from osbot_utils.utils.Dev import pprint
        import requests
        fast_api_server = Fast_API_Server(app=fast_api.app())
        with fast_api as _:
            assert _.routes_paths() == sorted(EXPECTED_ROUTES_PATHS)
            namespace   = {}
            python_code = _.client().get('/config/openapi.py').text
            exec(python_code, namespace)
            Client__Fast_API         = namespace['Client__Fast_API']
            client = Client__Fast_API(url=fast_api_server.url())
            assert client.config.base_url == fast_api_server.url()

        api_functions = list_set(class_functions(client))
        assert 'get_config_status'     in api_functions
        assert 'get_config_info'       in api_functions
        assert 'get_config_openapi_py' in api_functions
        assert 'get_config_version'    in api_functions



        #pprint(fast_api.routes())
        response_client = fast_api.client().get('config/version')
        url = fast_api_server.url() + 'config/version'

        with fast_api_server:
            assert fast_api_server.is_port_open() is True
            response = requests.get(url)
            assert response.status_code == 200
            assert response.json() == {'version': version__osbot_fast_api}
            assert response.json() == response_client.json()

            with client as _:
                assert type(_) is Client__Fast_API
                assert _.get_config_version() == { 'version': version__osbot_fast_api }
                assert _.get_config_version() == response_client.json()
                assert _.get_config_status () == {'status'  : 'ok'                    }




