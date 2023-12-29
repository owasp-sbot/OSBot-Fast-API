from unittest import TestCase

import requests
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set
from pydantic import BaseModel

from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.api.routes.http_shell.Http_Shell__Client import Http_Shell__Client
from osbot_fast_api.api.routes.http_shell.Http_Shell__Server import Http_Shell__Server, Model__Shell_Data, \
    Model__Shell_Command
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server

class test_Http_Shell__Client(TestCase):
    client          : Http_Shell__Client
    server_endpoint : str
    fast_api        : Fast_API
    fast_api_server : Fast_API_Server

    # setup local server to simular the post request
    @classmethod
    def setUpClass(cls) -> None:
        cls.fast_api            = Fast_API()
        cls.fast_api_server     = Fast_API_Server(app=cls.fast_api.app())
        cls.server_endpoint     = cls.fast_api_server.url() + 'http-shell-server'
        cls.client              = Http_Shell__Client(server_endpoint=cls.server_endpoint)
        cls.fast_api.add_route_post(cls.http_shell_server)
        assert cls.fast_api_server.start() is True

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.fast_api_server.stop() is True

    @staticmethod
    def http_shell_server(shell_command: Model__Shell_Command):
        http_shell__server = Http_Shell__Server()
        exec_result        = http_shell__server.invoke(shell_command)
        if exec_result.get('status') == 'ok':
            return exec_result.get('return_value')
        return exec_result


    def test__fast_api_server(self):
        auth_key              = 'an-auth_key'                                                       # todo: add support for getting auth key from env-var
        expected_result       = 'pong'
        shell_data            = Model__Shell_Data   (method_name='ping', method_kwargs = {})
        shell_command         = Model__Shell_Command(auth_key=auth_key, data=shell_data)
        shell_command_json    = shell_command.model_dump()
        response_openapi      = requests.get(self.fast_api_server.url() + 'openapi.json')
        response_shell_invoke = self.fast_api.client().post('/http-shell-server', json=shell_command_json)
        response_options      = requests.options(self.server_endpoint)
        options_headers       = response_options.headers

        del options_headers['date']

        assert response_shell_invoke.json()         == expected_result
        assert self.fast_api.routes_paths()         == ['/http-shell-server']
        assert self.fast_api_server.port            >  19999
        assert self.fast_api_server.is_port_open()  is True
        assert response_options.json()              == { "detail"         : "Method Not Allowed" }
        assert options_headers                      == { 'server'         : 'uvicorn'           ,
                                                         'allow'          : 'POST'              ,
                                                         'content-length' : '31'                ,
                                                         'content-type'   : 'application/json'   }

        assert list_set(response_openapi.json().get('paths')) == self.fast_api.routes_paths(include_default=True)


    # test methods

    def test_bash(self):
        assert '.py'                        in self.client.bash('ls'    ).get('stdout')
        assert 'bin'                        in self.client.bash('ls /'  ).get('stdout')
        assert 'bin'                        in self.client.bash('ls','/').get('stdout')
        assert self.client.bash('AAAAAa').get('stderr') == 'bash: AAAAAa: command not found\n'

    def test_ls(self):
        assert '.py'    in self.client.ls()
        assert ''       == self.client.ls('aaaa')
        assert 'bin'    in self.client.ls('/')
        assert 'bin'    in self.client.ls('' , '/')
        assert 'bash'   in self.client.ls('bin', '/')

    def test_ping(self):
        assert self.client.ping() == 'pong'

    def test_list_processes(self):
        assert 'PID' in self.client.list_processes()

    def test_memory_usage(self):
        assert self.client.memory_usage() == { 'error_message'  : 'unknown method: memory_usage',
                                               'method_kwargs'  : {}                            ,
                                               'method_name'    : 'memory_usage'                ,
                                               'return_value'   : None                          ,
                                               'status'         : 'error'                       }

    def test_process_run(self):
        assert 'OSBot-Fast-API' in self.client.process_run('pwd').get('stdout')

    def test_pwd(self):
        assert 'OSBot-Fast-API' in self.client.pwd()