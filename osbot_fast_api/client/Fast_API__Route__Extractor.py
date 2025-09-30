from typing                                                                     import List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from fastapi                                                                    import FastAPI
from fastapi.routing                                                            import APIWebSocketRoute
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from starlette.middleware.wsgi                                                  import WSGIMiddleware
from starlette.routing                                                          import Mount
from starlette.staticfiles                                                      import StaticFiles
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Prefix                   import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.schemas.for_osbot_utils.enums.Enum__Http__Method            import Enum__Http__Method
from osbot_fast_api.schemas.routes.Schema__Fast_API__Route                      import Schema__Fast_API__Route
from osbot_fast_api.schemas.routes.Schema__Fast_API__Routes__Collection         import Schema__Fast_API__Routes__Collection
from osbot_fast_api.schemas.routes.enums.Enum__Route__Type                      import Enum__Route__Type


class Fast_API__Route__Extractor(Type_Safe):                              # Dedicated class for route extraction
    app               : FastAPI
    include_default   : bool = False
    expand_mounts     : bool = False

    @type_safe
    def extract_routes(self) -> Schema__Fast_API__Routes__Collection:      # Main extraction method
        routes = self.extract_routes_from_router(router       = self.app                              ,
                                                 route_prefix = Safe_Str__Fast_API__Route__Prefix('/'))

        return Schema__Fast_API__Routes__Collection(routes         = routes,
                                                    total_routes   = len(routes),
                                                    has_mounts     = any(r.is_mount for r in routes),
                                                    has_websockets = any(r.route_type == Enum__Route__Type.WEBSOCKET for r in routes))

    def extract_routes_from_router(self, router                                           ,   # Router to extract from
                                         route_prefix : Safe_Str__Fast_API__Route__Prefix
                                    ) -> List[Schema__Fast_API__Route]:                                 # Returns list of route schemas
        routes = []

        for route in router.routes:                                                                     # Skip default routes if requested
            if not self.include_default and self._is_default_route(route.path):
                continue

            # Build safe route path
            full_path = self._combine_paths(route_prefix, route.path)

            # Extract based on route type
            if isinstance(route, Mount):
                mount_routes = self._extract_mount_routes(route, full_path)
                routes.extend(mount_routes)
            elif isinstance(route, APIWebSocketRoute):
                websocket_route = self._create_websocket_route(route, full_path)
                routes.append(websocket_route)
            else:
                api_route = self._create_api_route(route, full_path)
                routes.append(api_route)

        return routes

    def _create_api_route(self, route                                   ,  # FastAPI route object
                               path  : Safe_Str__Fast_API__Route__Prefix
                         ) -> Schema__Fast_API__Route:                     # Returns route schema
        # Convert methods to enum
        http_methods = []
        if hasattr(route, 'methods') and route.methods:
            for method in sorted(route.methods):
                try:
                    http_methods.append(Enum__Http__Method(method))
                except ValueError:
                    pass  # Skip unknown methods

        # Extract method name safely
        method_name = Safe_Str__Id(route.name) if route.name else Safe_Str__Id("unnamed")

        # Determine route class if from Routes__* pattern
        route_class = self.extract_route_class(route)

        return Schema__Fast_API__Route(http_path    = path                              ,
                                       method_name  = method_name                       ,
                                       http_methods = http_methods                      ,
                                       route_type   = Enum__Route__Type.API_ROUTE       ,
                                       route_class  = route_class                       ,
                                       is_default   = self._is_default_route(str(path)  ))

    def _extract_mount_routes(self, mount                              ,   # Mount object
                                   path  : Safe_Str__Fast_API__Route__Prefix
                             ) -> List[Schema__Fast_API__Route]:           # Returns route schemas
        routes = []

        # Determine mount type
        if isinstance(mount.app, WSGIMiddleware):
            route = Schema__Fast_API__Route(
                http_path    = path,
                method_name  = Safe_Str__Id("wsgi_app"),
                http_methods = [],  # Unknown methods for WSGI
                route_type   = Enum__Route__Type.WSGI,
                is_mount     = True
            )
            routes.append(route)

        elif isinstance(mount.app, StaticFiles):
            route = Schema__Fast_API__Route(
                http_path    = path,
                method_name  = Safe_Str__Id("static_files"),
                http_methods = [Enum__Http__Method.GET, Enum__Http__Method.HEAD],
                route_type   = Enum__Route__Type.STATIC,
                is_mount     = True
            )
            routes.append(route)

        elif self.expand_mounts and hasattr(mount.app, 'router'):
            # Recursively extract routes from mounted app
            mount_routes = self.extract_routes_from_router(
                router       = mount.app.router,
                route_prefix = path
            )
            routes.extend(mount_routes)
        else:
            # Generic mount
            route = Schema__Fast_API__Route(
                http_path    = path,
                method_name  = Safe_Str__Id("mount"),
                http_methods = [],
                route_type   = Enum__Route__Type.MOUNT,
                is_mount     = True
            )
            routes.append(route)

        return routes

    def _create_websocket_route(self, route                            ,   # WebSocket route
                                      path  : Safe_Str__Fast_API__Route__Prefix
                               ) -> Schema__Fast_API__Route:               # Returns route schema
        return Schema__Fast_API__Route(
            http_path    = path,
            method_name  = Safe_Str__Id(route.name) if route.name else Safe_Str__Id("websocket"),
            http_methods = [],  # WebSockets don't use HTTP methods
            route_type   = Enum__Route__Type.WEBSOCKET
        )

    def _combine_paths(self, prefix : Safe_Str__Fast_API__Route__Prefix,   # Prefix path
                            path   : str                                   # Path to append
                      ) -> Safe_Str__Fast_API__Route__Prefix:             # Returns combined path
        # Handle path combination safely
        prefix_str = str(prefix).rstrip('/')
        path_str   = path.lstrip('/')

        if prefix_str == '':
            combined = '/' + path_str
        else:
            combined = f"{prefix_str}/{path_str}"

        return Safe_Str__Fast_API__Route__Prefix(combined)

    def _is_default_route(self, path: str) -> bool:                       # Check if default route
        # Import here to avoid circular dependency
        from osbot_fast_api.schemas.consts__Fast_API import FAST_API_DEFAULT_ROUTES_PATHS
        return path in FAST_API_DEFAULT_ROUTES_PATHS

    def extract_route_class(self, route) -> Safe_Str__Id:                                   # Extract class name (in most cases it will be something like Routes__* )
        route_class = None
        if hasattr(route, 'endpoint'):
            if hasattr(route.endpoint, '__self__'):                                         # first try to get the class name (if inside a class)
                route_class = Safe_Str__Id(route.endpoint.__self__.__class__.__name__)
            elif hasattr(route.endpoint, '__qualname__'):                                   # then if that is not available use __qualname__
                qualname = route.endpoint.__qualname__
                if '.' in qualname:                                                     # todo: see if there is a better way to do this and find the base class name
                    route_class = qualname.split('.')[0]
        return Safe_Str__Id(route_class)