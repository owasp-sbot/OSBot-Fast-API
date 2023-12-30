from osbot_fast_api.api.Fast_API                        import Fast_API
from osbot_fast_api.utils.http_shell.Http_Shell__Server import Model__Shell_Command, Http_Shell__Server


class Fast_API__With_Shell_Server(Fast_API):

    def http_shell(self, shell_command: Model__Shell_Command):
        return Http_Shell__Server().invoke(shell_command)

    def setup_routes(self):
        self.add_route_post(self.http_shell)
        self.add_shell_server()



