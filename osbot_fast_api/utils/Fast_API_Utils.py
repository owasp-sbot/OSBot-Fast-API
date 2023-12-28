from starlette.routing import Mount

ROUTE_REDIRECT_TO_DO            = [{'http_methods': ['GET'        ], 'http_path': '/'      , 'method_name': 'redirect_to_docs'}]
FAST_API_DEFAULT_ROUTES_PATHS   = ['/docs', '/docs/oauth2-redirect', '/openapi.json', '/redoc']
FAST_API_DEFAULT_ROUTES         = [ { 'http_methods': ['GET','HEAD'], 'http_path': '/openapi.json'         , 'method_name': 'openapi'              },
                                    { 'http_methods': ['GET','HEAD'], 'http_path': '/docs'                 , 'method_name': 'swagger_ui_html'      },
                                    { 'http_methods': ['GET','HEAD'], 'http_path': '/docs/oauth2-redirect' , 'method_name': 'swagger_ui_redirect'  },
                                    { 'http_methods': ['GET','HEAD'], 'http_path': '/redoc'                , 'method_name': 'redoc_html'           },
                                    { 'http_methods': ['GET'       ], 'http_path': '/'                     , 'method_name': 'redirect_to_docs'     }]

class Fast_API_Utils():

    def __init__(self, fast_api):
        self.fast_api = fast_api
        self.app      = fast_api.app()

    def fastapi_routes(self, router=None, include_default=False):
        if router is None:
            router = self.app
        routes = []
        for route in router.routes:
            if include_default is False and route.path in FAST_API_DEFAULT_ROUTES_PATHS:
                continue
            if type(route) is Mount:
                methods = ['GET', 'HEAD']
            else:
                methods = sorted(route.methods)
            route = {"http_path": route.path, "method_name": route.name, "http_methods": methods}
            routes.append(route)
        return routes