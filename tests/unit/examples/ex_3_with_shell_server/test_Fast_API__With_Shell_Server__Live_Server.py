import os
from unittest import TestCase

from dotenv import load_dotenv
from osbot_utils.testing.Trace_Call import trace_calls
from osbot_utils.utils.Dev import pprint

from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.routes.http_shell.Http_Shell__Client import Http_Shell__Client
from osbot_fast_api.api.routes.http_shell.Http_Shell__Server import Model__Shell_Data, ENV__HTTP_SHELL_AUTH_KEY, \
    Model__Shell_Command
from osbot_fast_api.examples.ex_3_with_shell_server.Fast_API__With_Shell_Server import Fast_API__With_Shell_Server
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server


class test_Fast_API__With_Shell_Server__Live_Server(TestCase):
    auth_key        : str
    server_endpoint : str
    fast_api        : Fast_API
    fast_api_server : Fast_API_Server

    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv()
        cls.auth_key        = os.environ.get(ENV__HTTP_SHELL_AUTH_KEY)
        cls.fast_api        = Fast_API__With_Shell_Server()
        cls.fast_api_server = Fast_API_Server(app=cls.fast_api.app())
        cls.fast_api_server.start()
        cls.server_endpoint = cls.fast_api_server.url() + 'http-shell'
        cls.client          = Http_Shell__Client(server_endpoint=cls.server_endpoint, auth_key=cls.auth_key)
        assert cls.fast_api_server.is_port_open() is True

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fast_api_server.stop()
        assert cls.fast_api_server.is_port_open() is False

    def test_invoke__ping(self):
        assert self.client.ping() == 'pong'

    def test_exec__function(self):
        def the_answer():
            return 40 + 2
        assert self.client.exec_function(the_answer) == 42

