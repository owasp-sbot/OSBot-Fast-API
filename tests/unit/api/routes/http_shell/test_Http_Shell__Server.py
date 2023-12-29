import inspect
import os
import sys
from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from osbot_fast_api.api.routes.http_shell.Http_Shell__Server import Http_Shell__Server


class test_Http_Shell__Server(TestCase):

    def setUp(self):
        self.server = Http_Shell__Server()


    def _shell_invoke(self, method_name, method_kwargs=None):
        event = {'method_name': method_name, 'method_kwargs': method_kwargs}
        return self.server.invoke(event).get('return_value')

    # test methods
    def test_bash(self):
        #assert 'test_Shell_Server.py' in self.server.bash('ls'    ).get('stdout')
        assert 'bin'                  in self.server.bash('ls /'  ).get('stdout')
        assert 'bin'                  in self.server.bash('ls','/').get('stdout')
        assert 'AAAAAa: command not found' in self.server.bash('AAAAAa').get('stderr')

    def test_disk_space(self):
        disk_space = self.server.disk_space()
        assert 'Filesystem' in disk_space
        assert 'Size'       in disk_space

    def test_invoke(self):
        assert self.server.invoke({}) is None
        assert self.server.invoke({'method_name':'ping', 'method_kwargs': {}}) == { 'method_invoked': True,
                                                                                    'method_kwargs': {},
                                                                                    'method_name': 'ping',
                                                                                    'return_value': 'pong'}
        assert self.server.invoke({'shell': {'method_name':'aaaa', 'method_kwargs': {}}}) is None
        assert self._shell_invoke('ping', {}  ) == 'pong'
        assert self._shell_invoke('ping', None) == 'pong'


    def test_invoke__process_run(self):
        pwd = self._shell_invoke('process_run', {'executable':'pwd'}).get('stdout')
        assert 'OSBot-Fast-API' in pwd

    def test_file_contents(self):
        path = inspect.getfile(Http_Shell__Server)
        file_contents = self._shell_invoke('file_contents',{'path': path})
        assert 'class Http_Shell__Server:' in file_contents

    def test_list_processes(self):
        processes_list = self.server.list_processes()
        assert 'PID' in processes_list
        assert 'TTY' in processes_list
        assert 'CMD' in processes_list

    def test_pwd(self):
        assert 'OSBot-Fast-API' in self.server.pwd()

    def test_python_exec(self):
        assert self.server.python_exec('result=40+2'                              ) == 42
        assert self.server.python_exec('result={"answer": 40+2 } '                ) == { 'answer': 42                           }
        assert self.server.python_exec('import sys;\npath = sys.path\nresult=path') == sys.path
        assert self.server.python_exec('aaaa.bbb()'                               ) == { 'error' : "name 'aaaa' is not defined" }