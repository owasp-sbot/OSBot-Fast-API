from fastapi                                             import Response
from osbot_fast_api.api.decorators.route_path            import route_path
from osbot_fast_api.api.routes.Fast_API__Routes          import Fast_API__Routes
from osbot_fast_api.api.transformers.OpenAPI__To__Python import OpenAPI__To__Python
from osbot_fast_api.utils.Fast_API__Server_Info          import fast_api__server_info
from osbot_fast_api.utils.Version                        import version__osbot_fast_api

# todo: these are actually routes, so we should move them into a better location
#       maybe 'default_routes' or something similar

ROUTES_PATHS__CONFIG = ['/config/info'          ,
                        '/config/openapi.py'    ,
                        '/config/status'        ,
                        '/config/version'       ]

class Routes__Config(Fast_API__Routes):
    tag  = 'config'

    def info(self):
        return fast_api__server_info.json()

    def status(self):
        return {'status':'ok'}

    def version(self):
        return {'version': version__osbot_fast_api}

    @route_path('/openapi.py')
    def openapi_python(self):
        open_api_to_python = OpenAPI__To__Python()
        client_python_code = open_api_to_python.generate_from_app(app=self.app)

        return Response(content    = client_python_code,
                        media_type = "text/x-python"   )

    def setup_routes(self):
        self.add_route_get(self.info          )
        self.add_route_get(self.status        )
        self.add_route_get(self.version       )
        self.add_route_get(self.openapi_python)