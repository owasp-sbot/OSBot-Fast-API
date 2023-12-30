import os

import requests
from dotenv import load_dotenv
from osbot_utils.utils.Functions                        import function_source_code
from osbot_fast_api.utils.http_shell.Http_Shell__Server import Model__Shell_Command, Model__Shell_Data, \
    ENV__HTTP_SHELL_AUTH_KEY


class Http_Shell__Client:
    def __init__(self, server_endpoint, auth_key=None, return_value_if_ok=True):
        self.server_endpoint    = server_endpoint
        self.auth_key           = auth_key or self.auth_key()
        self.return_value_if_ok = return_value_if_ok

    def _invoke(self, method_name, method_kwargs=None):
        shell_data         =  Model__Shell_Data(method_name=method_name, method_kwargs=method_kwargs or {})
        shell_command      =  Model__Shell_Command(auth_key=self.auth_key, data=shell_data)
        shell_command_json = shell_command.model_dump()
        response           = requests.post(self.server_endpoint, json=shell_command_json)
        response_json      = response.json()
        if self.return_value_if_ok and response_json.get('status') == 'ok':
            return response_json.get('return_value')
        return response_json

    def auth_key(self):
        load_dotenv()
        return os.environ.get(ENV__HTTP_SHELL_AUTH_KEY)

    def bash(self, command, cwd=None):
        result = self._invoke('bash', {'command': command, 'cwd': cwd})
        if result.get('status') == 'ok' and not result.get('stderr'):
            return result.get('stdout', '').strip()
        return result

    def exec_function(self, function):
        return self.python_exec_function(function)

    def process_run(self, executable, params=None, cwd=None):
        return self._invoke('process_run', {'executable': executable, 'params': params, 'cwd': cwd})

    def python_exec(self, code):
        return self._invoke('python_exec', {'code': code})

    def python_exec_function(self, function):
        function_name = function.__name__
        function_code = function_source_code(function)
        exec_code = f"{function_code}\nresult= {function_name}()"
        return self.python_exec(exec_code)

    # command methods

    def ls(self, path='', cwd='.'):  # todo: fix vuln: this method allows extra process executions via ; and |
        return self.bash(f'ls {path}', cwd)

    def file_contents(self, path):
        return self._invoke('file_contents', {'path': path})

    # with not params
    def disk_space(self):
        return self._invoke('disk_space')

    def list_processes(self):
        return self._invoke('list_processes')

    def memory_usage(self):
        return self._invoke('memory_usage')

    def ping(self):
        return self._invoke('ping')

    def ps(self):
        return self.bash('ps')

    def pwd(self):
        return self._invoke('pwd')


    def whoami(self):
        return self.bash('whoami')