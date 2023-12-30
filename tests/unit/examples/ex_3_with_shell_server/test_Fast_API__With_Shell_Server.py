import os
from unittest import TestCase

from dotenv import load_dotenv
from osbot_utils.utils.Dev import pprint

from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.routes.http_shell.Http_Shell__Client import Http_Shell__Client
from osbot_fast_api.api.routes.http_shell.Http_Shell__Server import Model__Shell_Data, ENV__HTTP_SHELL_AUTH_KEY, \
    Model__Shell_Command
from osbot_fast_api.examples.ex_3_with_shell_server.Fast_API__With_Shell_Server import Fast_API__With_Shell_Server


class test_Fast_API__With_Shell_Server(TestCase):
    auth_key        : str
    fast_api        : Fast_API

    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv()
        cls.auth_key = os.environ.get(ENV__HTTP_SHELL_AUTH_KEY)
        cls.fast_api = Fast_API__With_Shell_Server()

    def test__invoke_method(self, method_name='ping', method_kwargs=None):
        shell_data            = Model__Shell_Data   (method_name=method_name, method_kwargs = method_kwargs or {})
        shell_command         = Model__Shell_Command(auth_key=self.auth_key, data=shell_data)
        shell_command_json    = shell_command.model_dump()
        response              = self.fast_api.client().post('/http-shell', json=shell_command_json).json()
        if response.get('status') == 'ok':
            return response.get('return_value')
        return response

    def test_routes_paths(self):
        assert self.fast_api.routes_paths() == ['/http-shell', '/shell-server']

    def test_invoke__ping(self):
        assert self.test__invoke_method('ping') == 'pong'

    def test_invoke__python_exec(self):
        code   = 'result = 40+2'
        result = self.test__invoke_method('python_exec', {'code': code})
        assert result == 42

