import inspect
import os
import sys
from unittest                                           import TestCase
from osbot_utils.utils.Misc                             import new_guid
from osbot_fast_api.utils.http_shell.Http_Shell__Server import Http_Shell__Server, Model__Shell_Data, \
    Model__Shell_Command, AUTH_MESSAGE__KEY_NOT_PROVIDED, AUTH_MESSAGE__KEY_NOT_GUID, AUTH_MESSAGE__ENV_KEY_NOT_SET, \
    ENV__HTTP_SHELL_AUTH_KEY, AUTH_MESSAGE__AUTH_FAILED, AUTH_MESSAGE__AUTH_OK


class test_Http_Shell__Server(TestCase):

    def setUp(self):
        self.auth_key = new_guid()
        self.server   = Http_Shell__Server()
        self._set_auth_key(self.auth_key)

    def _shell_invoke(self, method_name, method_kwargs=None):
        data    = Model__Shell_Data   (method_name=method_name, method_kwargs=method_kwargs)
        command = Model__Shell_Command(auth_key=self.auth_key, data=data)
        return self.server.invoke(command).get('return_value')

    def _set_auth_key(self, auth_key):
        os.environ[ENV__HTTP_SHELL_AUTH_KEY] = auth_key

    # test auth
    def test_check_auth_key(self):
        self._set_auth_key('')
        assert self.server.check_auth_key(''           ) == {'auth_message': AUTH_MESSAGE__KEY_NOT_PROVIDED , 'auth_status': 'failed' }
        assert self.server.check_auth_key('aaaa'       ) == {'auth_message': AUTH_MESSAGE__KEY_NOT_GUID     , 'auth_status': 'failed' }
        assert self.server.check_auth_key(self.auth_key) == {'auth_message': AUTH_MESSAGE__ENV_KEY_NOT_SET  , 'auth_status': 'failed' }
        self._set_auth_key('aaaaa')
        assert self.server.check_auth_key(self.auth_key) == {'auth_message': AUTH_MESSAGE__AUTH_FAILED      , 'auth_status': 'failed' }
        self._set_auth_key(self.auth_key    )
        assert self.server.check_auth_key(self.auth_key) == {'auth_message': AUTH_MESSAGE__AUTH_OK          , 'auth_status': 'ok'     }


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
        data    = Model__Shell_Data   (method_name='', method_kwargs={})
        command = Model__Shell_Command(auth_key=self.auth_key, data=data)
        assert self.server.invoke(command) == dict(error_message = 'unknown method: ' , method_kwargs = {}  ,
                                                   method_name   = ''                ,  return_value  = None,
                                                   status        = 'error'                                  )
        data.method_name = 'ping'
        assert self.server.invoke(command) == dict(error_message = None  , method_kwargs = {}    ,
                                                   method_name   = 'ping', return_value  = 'pong',
                                                   status        = 'ok'                          )
        data.method_kwargs = {'a':1}
        assert self.server.invoke(command) == dict(error_message = "Http_Shell__Server.ping() got an unexpected keyword argument 'a'",
                                                   method_kwargs = {'a': 1} , method_name = 'ping'                                   ,
                                                   return_value  = None     , status      = 'error'                                  )
        data.method_name   = 'file_contents'
        data.method_kwargs = {}
        assert self.server.invoke(command) == dict(error_message = "Http_Shell__Server.file_contents() missing 1 required positional argument: 'path'",
                                                   method_kwargs = {}   , method_name = 'file_contents'                                               ,
                                                   return_value  = None , status      = 'error'                                                       )

        command.auth_key = 'aaaaaa'
        data.method_name = 'ping'
        assert self.server.invoke(command) == dict(error_message = 'failed auth: auth key was not a valid guid/uuid',
                                                   method_kwargs = {}   , method_name   = 'ping'                    ,
                                                   return_value  = None , status        = 'error'                   )


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