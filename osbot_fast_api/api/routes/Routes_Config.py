from osbot_fast_api.api.Fast_API__Routes        import Fast_API__Routes
from osbot_fast_api.utils.Fast_API__Server_Info import fast_api__server_info
from osbot_fast_api.utils.Version               import version__osbot_fast_api

# todo fix bug that is causing the route to be added multiple times
ROUTES__CONFIG = [{ 'http_methods': ['GET'], 'http_path': '/config/info'   , 'method_name': 'info'   },
                  { 'http_methods': ['GET'], 'http_path': '/config/status' , 'method_name': 'status' },
                  { 'http_methods': ['GET'], 'http_path': '/config/version', 'method_name': 'version'}]

ROUTES_PATHS__CONFIG = ['/config/status', '/config/version']

class Routes_Config(Fast_API__Routes):
    tag : str = 'config'

    def info(self):
        return fast_api__server_info.json()

    def status(self):
        return {'status':'ok'}

    def version(self):
        return {'version': version__osbot_fast_api}

    def setup_routes(self):
        self.add_route_get(self.info   )
        self.add_route_get(self.status )
        self.add_route_get(self.version)