import os

from dotenv                                     import load_dotenv
from osbot_utils.utils.Process                  import Process
from pydantic                                   import BaseModel
from osbot_fast_api.utils._extra_osbot_utils    import is_guid


class Model__Shell_Data(BaseModel):
    method_name   : str
    method_kwargs : dict = {}

class Model__Shell_Command(BaseModel):
    auth_key: str
    data    : Model__Shell_Data

ENV__HTTP_SHELL_AUTH_KEY       = 'HTTP_SHELL__AUTH_KEY'
AUTH_MESSAGE__KEY_NOT_PROVIDED = 'auth key not provided'
AUTH_MESSAGE__KEY_NOT_GUID     = 'auth key was not a valid guid/uuid'
AUTH_MESSAGE__ENV_KEY_NOT_SET  = f'server env variable "ENV__HTTP_SHELL_AUTH_KEY" not set'
AUTH_MESSAGE__AUTH_OK          = 'ok - valid auth key'
AUTH_MESSAGE__AUTH_FAILED      = 'failed - invalid auth key'

class Http_Shell__Server:

    def check_auth_key(self, auth_key):
        auth_status  = "failed"
        env_auth_key = self.env_auth_key()
        if not auth_key:
            auth_message = AUTH_MESSAGE__KEY_NOT_PROVIDED
        elif is_guid(auth_key) is False:
            auth_message = AUTH_MESSAGE__KEY_NOT_GUID
        elif not env_auth_key:
            auth_message = AUTH_MESSAGE__ENV_KEY_NOT_SET
        elif auth_key == env_auth_key:
            auth_status  = "ok"
            auth_message = AUTH_MESSAGE__AUTH_OK
        else:
            auth_message = AUTH_MESSAGE__AUTH_FAILED
        return dict(auth_status=auth_status, auth_message=auth_message)

    def env_auth_key(self):
        load_dotenv()
        return os.environ.get(ENV__HTTP_SHELL_AUTH_KEY)

    def invoke(self, command: Model__Shell_Command):
        auth_key       = command.auth_key
        data           = command.data
        method_name    = data.method_name
        method_kwargs  = data.method_kwargs
        return_value   = None
        error_message  = None
        auth_result   = self.check_auth_key(auth_key)
        if auth_result.get('auth_status') != 'ok':
            error_message = f'failed auth: {auth_result.get("auth_message")}'
            status        = "error"
        else:
            if hasattr(Http_Shell__Server,method_name):
                method = getattr(Http_Shell__Server, method_name)
                try:
                    if type(method_kwargs) is dict:
                        return_value = method(**method_kwargs)
                    # else:
                    #     return_value = method()
                    status         = "ok"
                except Exception as error:
                    error_message = str(error)
                    status        = "error"
            else:
                error_message = f'unknown method: {method_name}'
                status        = "error"
        return { "error_message"  : error_message  ,
                 "method_name"    : method_name    ,
                 "method_kwargs"  : method_kwargs  ,
                 "return_value"   : return_value   ,
                 "status"         : status         }


    @staticmethod  # note: this method by design allows extra commands injection via | and ;
    def bash(command, cwd=None):
        bash_command = 'bash'
        bash_params  = ['-c', command]
        return Http_Shell__Server.process_run(bash_command, bash_params, cwd)


    @staticmethod
    def process_run(executable, params=None, cwd='.'):
        return Process.run(executable,params, cwd)

    @staticmethod
    def ping():
        return 'pong'

    @staticmethod
    def python_exec(code):
        try:
            exec(code)
            return locals().get('result')
        except Exception as error:
            return {'error': f'{error}'}

    # helper process_run methods
    @staticmethod
    def pwd():
        return Http_Shell__Server.process_run('pwd').get('stdout')

    @staticmethod
    def disk_space():
        return Http_Shell__Server.bash('df -h').get('stdout').strip()

    @staticmethod
    def file_contents(path):
        return Http_Shell__Server.process_run('cat',[path]).get('stdout')

    @staticmethod
    def list_processes():
        return Http_Shell__Server.bash('ps -a').get('stdout').strip()

    #todo: refactor this to a linux sepecific class
    # @staticmethod
    # def memory_usage():
    #     return Http_Shell__Server.file_contents('/proc/meminfo')