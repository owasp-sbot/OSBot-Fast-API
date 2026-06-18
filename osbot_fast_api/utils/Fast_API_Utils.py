from fastapi.routing                                import APIWebSocketRoute
from starlette.middleware.wsgi                      import WSGIMiddleware
from starlette.routing                              import Mount
from starlette.staticfiles                          import StaticFiles
from osbot_fast_api.api.schemas.consts.consts__Fast_API import FAST_API_DEFAULT_ROUTES_PATHS


class Fast_API_Utils:

    def __init__(self, app):
        self.app = app

    def fastapi_routes(self, router=None, include_default=False, expand_mounts=False, route_prefix=''):
        if router is None:
            router = self.app
        routes = []
        for route in router.routes:
            # FastAPI >= 0.137: include_router() no longer flattens child routes into
            # app.routes; it inserts an _IncludedRouter wrapper (a BaseRoute with no .path).
            # Expand it into its effective routes so introspection keeps working.
            if route.__class__.__name__ == '_IncludedRouter':
                routes.extend(self.fastapi_routes__from_included(route,
                                                                 include_default=include_default,
                                                                 expand_mounts=expand_mounts,
                                                                 route_prefix=route_prefix))
                continue

            if include_default is False and route.path in FAST_API_DEFAULT_ROUTES_PATHS:
                continue
            if type(route) is Mount:
                if type(route.app) is WSGIMiddleware:       # todo: add better support for this mount (which is at the moment a Flask app which has a complete different route
                    methods = []                            # cloud be any (we just don't know)
                elif type(route.app) is StaticFiles:
                    methods = ['GET', 'HEAD']
                else:
                    if expand_mounts:
                        mount_route_prefix = route_prefix + route.path
                        mount_kwargs = dict(router          = route.app.router   ,
                                            include_default = include_default    ,
                                            expand_mounts   = expand_mounts      ,
                                            route_prefix    = mount_route_prefix )
                        mount_routes = self.fastapi_routes(**mount_kwargs)
                        routes.extend(mount_routes)
                    continue
            elif type(route) is APIWebSocketRoute:
                methods = []                                # todo: add support for websocket routes
            else:
                methods = sorted(route.methods)
            route_path = route_prefix + route.path
            route_to_add = {"http_path": route_path, "method_name": route.name, "http_methods": methods}
            routes.append(route_to_add)
        return routes

    def fastapi_routes__from_included(self, included, include_default, expand_mounts, route_prefix):
        routes = []
        for candidate in included.effective_candidates():
            if candidate.__class__.__name__ == '_IncludedRouter':                       # nested include_router
                routes.extend(self.fastapi_routes__from_included(candidate,
                                                                 include_default = include_default,
                                                                 expand_mounts   = expand_mounts,
                                                                 route_prefix    = route_prefix))
                continue
            path = candidate.path                                                        # effective, prefix already applied
            if include_default is False and path in FAST_API_DEFAULT_ROUTES_PATHS:
                continue
            methods = sorted(candidate.methods) if getattr(candidate, 'methods', None) else []   # websocket → []
            routes.append({"http_path"   : route_prefix + path,
                           "method_name" : candidate.name,
                           "http_methods": methods})
        return routes