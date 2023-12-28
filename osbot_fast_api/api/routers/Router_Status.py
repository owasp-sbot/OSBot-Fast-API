from osbot_fast_api.api.Fast_API_Router import Fast_API_Router
from osbot_fast_api.utils.Version import Version


# todo fix bug that is causing the route to be added multiple times
ROUTE_STATUS__ROUTES = [{ 'http_methods': ['GET'], 'http_path': '/status/status', 'method_name': 'status'},
                         {'http_methods': ['GET'], 'http_path': '/status/version', 'method_name': 'version'},
                         {'http_methods': ['GET'], 'http_path': '/status/status', 'method_name': 'status'},
                         {'http_methods': ['GET'], 'http_path': '/status/version', 'method_name': 'version'},
                         {'http_methods': ['GET'], 'http_path': '/status/status', 'method_name': 'status'},
                         {'http_methods': ['GET'], 'http_path': '/status/version', 'method_name': 'version'}]

class Router_Status(Fast_API_Router):

    def __init__(self, app):
        super().__init__(app, tag='status')
        super().setup()

    def status(self):
        return {'status':'ok'}

    def version(self):
        return {'version': Version().value()}

    def setup_routes(self):
        self.router.get("/status" )(self.status )
        self.router.get("/version")(self.version)


