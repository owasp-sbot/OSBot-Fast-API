import requests
from osbot_utils.utils.Functions                             import function_source_code
from osbot_fast_api.api.routes.http_shell.Http_Shell__Server import Model__Shell_Command, Model__Shell_Data


class Http_Shell__Client:
    def __init__(self, server_endpoint=None):
        self.server_endpoint = server_endpoint

    def _invoke(self, method_name, method_kwargs=None):
        shell_data         =  Model__Shell_Data(method_name=method_name, method_kwargs=method_kwargs or {})
        shell_command      =  Model__Shell_Command(auth_key='aaa', data=shell_data)
        shell_command_json = shell_command.model_dump()
        response           = requests.post(self.server_endpoint, json=shell_command_json)
        return response.json()

    def bash(self, command, cwd=None):
        return self._invoke('bash', {'command': command, 'cwd': cwd})

    # def exec(self, executable, params=None, cwd=None):
    #     result = self.process_run(executable, params, cwd)
    #     std_out = result.get('stdout', '').strip()
    #     std_err = result.get('stderr', '').strip()
    #     std_console = std_out + std_err
    #     if std_console:
    #         return std_console
    #     if result.get('errorMessage'):
    #         return f'Error: {result.get("errorMessage")}'
    #     return result

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
        return self.bash(f'ls {path}', cwd).get('stdout')

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
        return self.exec('ps')

    def pwd(self):
        return self._invoke('pwd')

    def whoami(self):
        return self.exec('whoami')