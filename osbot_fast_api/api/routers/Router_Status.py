from osbot_fast_api.api.FastAPI_Router import FastAPI_Router
from osbot_fast_api.utils.Version import Version


# todo fix bug that is causing the route to be added multiple times
ROUTE_STATUS__ROUTES = [{ 'http_methods': ['GET'], 'http_path': '/status/status', 'method_name': 'status'},
                         {'http_methods': ['GET'], 'http_path': '/status/version', 'method_name': 'status'},

                         {'http_methods': ['GET'], 'http_path': '/status/status', 'method_name': 'status'},
                         {'http_methods': ['GET'], 'http_path': '/status/version',

                          'method_name': 'status'},
                         {'http_methods': ['GET'],
                          'http_path': '/status/status',
                          'method_name': 'status'},
                         {'http_methods': ['GET'],
                          'http_path': '/status/version',
                          'method_name': 'status'}]

class Router_Status(FastAPI_Router):

    def __init__(self, app):
        super().__init__(app, name='status')
        super().setup()

    def status(self):
        return 'ok'

    def version(self):
        return Version().value()

    def setup_routes(self):
        self.router.get("/status" )(self.status )
        self.router.get("/version")(self.version)


