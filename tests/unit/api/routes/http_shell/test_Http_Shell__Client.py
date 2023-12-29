from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from pydantic import BaseModel

from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.routes.http_shell.Http_Shell__Client import Http_Shell__Client
from osbot_fast_api.api.routes.http_shell.Http_Shell__Server import Http_Shell__Server
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server

class Model__Shell_Command(BaseModel):
    auth_key: str
    data    : dict



class test_Http_Shell__Client(TestCase):
    fast_api        : Fast_API
    fast_api_server : Fast_API_Server
    @classmethod
    def setUpClass(cls) -> None:
        cls.fast_api = Fast_API()
        cls.fast_api_server = Fast_API_Server(app=cls.fast_api.app())
        assert cls.fast_api_server.start() is True
        cls.fast_api.add_route_post(cls.http_shell_server)

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.fast_api_server.stop() is True

    @staticmethod
    def http_shell_server(shell_command: Model__Shell_Command):
        auth_key           = shell_command.auth_key
        data               = shell_command.data
        http_shell__server = Http_Shell__Server()
        return http_shell__server.invoke(data).get('return_value')


    def test__fast_api_server(self):
        data            = {'method_name':'ping', 'method_kwargs': {}}
        expected_result = 'pong'
        shell_comamnd = Model__Shell_Command(auth_key='aaa', data=data)
        assert self.fast_api.routes_paths() == ['/http-shell-server']
        assert self.fast_api.client().post('/http-shell-server', json=dict(shell_comamnd)).json() == expected_result