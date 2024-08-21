from starlette.middleware.wsgi import WSGIMiddleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

ROUTE_REDIRECT_TO_DOCS          = {'http_methods': ['GET'        ], 'http_path': '/'      , 'method_name': 'redirect_to_docs'}
FAST_API_DEFAULT_ROUTES_PATHS   = ['/docs', '/docs/oauth2-redirect', '/openapi.json', '/redoc']
FAST_API_DEFAULT_ROUTES         = [ { 'http_methods': ['GET','HEAD'], 'http_path': '/openapi.json'         , 'method_name': 'openapi'              },
                                    { 'http_methods': ['GET','HEAD'], 'http_path': '/docs'                 , 'method_name': 'swagger_ui_html'      },
                                    { 'http_methods': ['GET','HEAD'], 'http_path': '/docs/oauth2-redirect' , 'method_name': 'swagger_ui_redirect'  },
                                    { 'http_methods': ['GET','HEAD'], 'http_path': '/redoc'                , 'method_name': 'redoc_html'           },
                                    ROUTE_REDIRECT_TO_DOCS]

class Fast_API_Utils:

    def __init__(self, app):
        self.app = app

    def fastapi_routes(self, router=None, include_default=False, expand_mounts=False, route_prefix=''):
        if router is None:
            router = self.app
        routes = []
        for route in router.routes:
            if include_default is False and route.path in FAST_API_DEFAULT_ROUTES_PATHS:
                continue
            if type(route) is Mount:
                if type(route.app) is WSGIMiddleware:       # todo: add better support for this mount (which is at the moment a Flask app which has a complete different route
                    methods = []                            # cloud be any (we just dont' know)
                elif type(route.app) is StaticFiles:
                    methods = ['GET', 'HEAD']
                else:
                    if expand_mounts:
                        mount_kwargs = dict(router          = route.app.router,
                                            include_default = include_default ,
                                            expand_mounts   = expand_mounts   ,
                                            route_prefix    = route.path      )
                        mount_routes = self.fastapi_routes(**mount_kwargs)
                        routes.extend(mount_routes)
                    continue
            else:
                methods = sorted(route.methods)
            route_path = route_prefix + route.path
            route_to_add = {"http_path": route_path, "method_name": route.name, "http_methods": methods}
            routes.append(route_to_add)
        return routes