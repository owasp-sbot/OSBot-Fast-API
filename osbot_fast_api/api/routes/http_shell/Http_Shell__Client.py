class Http_Shell__Client:
    def __init__(self, shell_server_endpoint=None):
        self.shell_server_endpoint = shell_server_endpoint
        pass

    def _invoke(self, method_name, method_kwargs=None):
        event = {'lambda_shell': {'method_name': method_name, 'method_kwargs': method_kwargs}}
        return Shell_Server().invoke(event)

    def bash(self, command, cwd=None):
        return self._invoke('bash', {'command': command, 'cwd': cwd})

    def exec(self, executable, params=None, cwd=None):
        result = self.process_run(executable, params, cwd)
        std_out = result.get('stdout', '').strip()
        std_err = result.get('stderr', '').strip()
        std_console = std_out + std_err
        if std_console:
            return std_console
        if result.get('errorMessage'):
            return f'Error: {result.get("errorMessage")}'
        return result

    def exec_function(self, function):
        return self.python_exec_function(function)

    def process_run(self, executable, params=None, cwd=None):
        return self._invoke('process_run', {'executable': executable, 'params': params, 'cwd': cwd})

    def reset(self):
        if self.aws_lambda.s3_bucket is None:  # if these values are not set
            self.aws_lambda.set_s3_bucket(AWS_Config().lambda_s3_bucket())  # use default values
            self.aws_lambda.set_s3_key(
                f'{AWS_Config().lambda_s3_folder_lambdas()}/{self.aws_lambda.original_name}.zip')  # which are needed
        return self.aws_lambda.update_lambda_code()  # to trigger the update (which will reset the lambda and force a cold start on next lambda invocation)

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