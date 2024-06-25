from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes
from osbot_fast_api.utils.Version import Version


# todo fix bug that is causing the route to be added multiple times
ROUTES__CONFIG = [{ 'http_methods': ['GET'], 'http_path': '/config/status' , 'method_name': 'status' },
                  { 'http_methods': ['GET'], 'http_path': '/config/version', 'method_name': 'version'}]

ROUTES_PATHS__CONFIG = ['/config/status', '/config/version']

class Routes_Config(Fast_API_Routes):
    tag : str = 'config'

    def status(self):
        return {'status':'ok'}

    def version(self):
        return {'version': Version().value()}

    def setup_routes(self):
        self.router.get("/status" )(self.status )
        self.router.get("/version")(self.version)


