from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Http import is_port_open

from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server
from osbot_fast_api.utils.Version import Version


class test_integration__Fast_API(TestCase):
    fast_api        : Fast_API           = None
    fast_api_server : Fast_API_Server    = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.fast_api        = Fast_API().setup()
        cls.fast_api_server = Fast_API_Server(app=cls.fast_api.app())
        cls.fast_api_server.start()
        assert cls.fast_api_server.is_port_open() is True

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fast_api_server.stop()
        assert cls.fast_api_server.is_port_open() is False


    def test_version(self):
        response = self.fast_api_server.requests_get('/config/version')
        assert response.status_code == 200
        assert response.json()      == {'version': Version().value() }