import inspect
from typing                                                                     import List, Union
from pydantic_core                                                              import PydanticUndefined
from osbot_fast_api.api.schemas.routes.Schema__Fast_API__Route                  import Schema__Fast_API__Route
from osbot_fast_api.api.schemas.routes.Schema__Fast_API__Routes__Collection     import Schema__Fast_API__Routes__Collection
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag         import Safe_Str__Fast_API__Route__Tag
from osbot_utils.type_safe.primitives.domains.http.enums.Enum__Http__Method     import Enum__Http__Method
from osbot_utils.utils.Http                                                     import url_join_safe
from osbot_fast_api.client.schemas.Schema__Endpoint__Param                      import Schema__Endpoint__Param
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List           import Type_Safe__List
from osbot_fast_api.api.schemas.consts.consts__Fast_API                         import FAST_API_DEFAULT_ROUTES_PATHS
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from fastapi                                                                    import FastAPI
from fastapi.routing                                                            import APIWebSocketRoute, APIRoute, APIRouter
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from starlette.middleware.wsgi                                                  import WSGIMiddleware
from starlette.routing                                                          import Mount, Route
from starlette.staticfiles                                                      import StaticFiles
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix      import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.api.schemas.enums.Enum__Fast_API__Route__Type               import Enum__Fast_API__Route__Type

class Fast_API__Route__Extractor(Type_Safe):                              # Dedicated class for route extraction
    app               : FastAPI
    include_default   : bool = False
    expand_mounts     : bool = False

    @type_safe
    def create_api_route(self, route : Union[APIRoute, Route]             ,     # FastAPI route object
                               path  : Safe_Str__Fast_API__Route__Prefix
                          ) -> Schema__Fast_API__Route:                         # Returns route schema
        http_methods = []                                                       # Convert methods to enum
        for method in sorted(route.methods):
            http_methods.append(Enum__Http__Method(method))
        method_name  = Safe_Str__Id(route.name)
        route_class  = self.extract__route_class(route)                           # Determine route class if from Routes__* pattern
        is_default   = self.is_default_route(str(path))
        description  = None
        path_params  = None
        query_params = None
        body_params  = None
        return_type  = None
        route_tags   = None

        if type(route) is APIRoute:                                              # only the APIRoute class has the
            description  = route.description
            path_params  = self.extract__path_params(route)
            query_params = self.extract__query_params(route)
            body_params  = self.extract__body_params(route)
            return_type  = self.extract__return_type(route)
            route_tags   = route.tags
            route_type   = Enum__Fast_API__Route__Type.API_ROUTE
        else:
            route_type   = Enum__Fast_API__Route__Type.ROUTE

        return Schema__Fast_API__Route(body_params  = body_params ,
                                       description  = description ,
                                       is_default   = is_default  ,
                                       http_path    = path        ,
                                       method_name  = method_name ,
                                       http_methods = http_methods,
                                       path_params  = path_params ,
                                       query_params = query_params,
                                       return_type  = return_type ,
                                       route_type   = route_type  ,
                                       route_tags   = route_tags  ,
                                       route_class  = route_class )

    @type_safe
    def combine_paths(self, prefix : Safe_Str__Fast_API__Route__Prefix,     # Prefix path
                            path   : Safe_Str__Fast_API__Route__Tag                   # Path to append
                       ) -> Safe_Str__Fast_API__Route__Prefix:              # Returns combined path
        prefix_str = str(prefix).rstrip('/')
        path_str   = path.lstrip('/')

        if prefix_str == '':
            combined = '/' + path_str
        else:
            combined = url_join_safe(prefix_str, path_str)

        return Safe_Str__Fast_API__Route__Prefix(combined)

    @type_safe
    def extract_routes(self) -> Schema__Fast_API__Routes__Collection:      # Main extraction method
        routes = self.extract_routes_from_router(router       = self.app.router                       ,
                                                 route_prefix = Safe_Str__Fast_API__Route__Prefix('/'))

        return Schema__Fast_API__Routes__Collection(routes         = routes,
                                                    total_routes   = len(routes),
                                                    has_mounts     = any(r.is_mount for r in routes),
                                                    has_websockets = any(r.route_type == Enum__Fast_API__Route__Type.WEBSOCKET for r in routes))

    @type_safe
    def extract_routes_from_router(self, router : APIRouter                                   ,              # FastAPI to extract routes from
                                         route_prefix : Safe_Str__Fast_API__Route__Prefix
                                    ) -> List[Schema__Fast_API__Route]:                                 # Returns list of route schemas
        routes = []

        for route in router.routes:                                                                     # Skip default routes if requested
            if not self.include_default and self.is_default_route(route.path):
                continue

            full_path = self.combine_paths(route_prefix, route.path)                                   # Build safe route path

            if isinstance(route, Mount):                                                                # Extract based on route type
                mount_routes = self.extract_mount_routes(route, full_path)
                routes.extend(mount_routes)
            elif isinstance(route, APIWebSocketRoute):
                websocket_route = self.create_websocket_route(route, full_path)
                routes.append(websocket_route)
            else:
                api_route = self.create_api_route(route, full_path)
                routes.append(api_route)

        return routes

    @type_safe
    def extract_mount_routes(self, mount: Mount                             ,   # Mount object
                                   path  : Safe_Str__Fast_API__Route__Prefix
                              ) -> List[Schema__Fast_API__Route]:               # Returns route schemas
        routes = Type_Safe__List(expected_type=Schema__Fast_API__Route)

        # Determine mount type
        if isinstance(mount.app, WSGIMiddleware):
            route = Schema__Fast_API__Route(http_path    = path                    ,
                                            method_name  = Safe_Str__Id("wsgi_app"),
                                            http_methods = []                      ,  # Unknown methods for WSGI
                                            route_type   = Enum__Fast_API__Route__Type.WSGI  ,
                                            is_mount     = True                    )
            routes.append(route)

        elif isinstance(mount.app, StaticFiles):
            route = Schema__Fast_API__Route(http_path    = path                                             ,
                                            method_name  = Safe_Str__Id("static_files")                     ,
                                            http_methods = [Enum__Http__Method.GET, Enum__Http__Method.HEAD],
                                            route_type   = Enum__Fast_API__Route__Type.STATIC                         ,
                                            is_mount     = True                                             )
            routes.append(route)

        elif self.expand_mounts and hasattr(mount.app, 'router'):                           # Recursively extract routes from mounted app
            mount_routes = self.extract_routes_from_router(router       = mount.app.router,
                                                           route_prefix = path)
            routes.extend(mount_routes)
        else:                                                                               # Generic mount
            route = Schema__Fast_API__Route(http_path    = path                     ,
                                            method_name  = Safe_Str__Id("mount")    ,
                                            http_methods = []                       ,
                                            route_type   = Enum__Fast_API__Route__Type.MOUNT  ,
                                            is_mount     = True                     )
            routes.append(route)

        return routes

    @type_safe
    def extract__path_params(self, route: APIRoute):
        path_params = []
        for param in route.dependant.path_params:
            path_params.append(Schema__Endpoint__Param(name        = param.name                   ,
                                                       description = param.field_info.description ,
                                                       param_type  = param.type_                  ))
        return path_params

    @type_safe
    def extract__query_params(self, route: APIRoute):
        query_params = []
        for param in route.dependant.query_params:
            if param.default is PydanticUndefined:
                default_value = None
            else:
                default_value = param.default
            query_params.append(Schema__Endpoint__Param(default     = default_value                ,
                                                        name        = param.name                   ,
                                                        param_type  = param.type_                  ,
                                                        required    = param.required               ,
                                                        description = param.field_info.description))
        return query_params

    @type_safe
    def extract__body_params(self, route: APIRoute):
        body_params = []
        original_types = getattr(route.endpoint, '__original_param_types__', {})                                        # todo: find a better way to communicate these mappings

        for param in route.dependant.body_params:

            param_type = original_types.get(param.name, param.type_)                                                   # Use original type if available, otherwise fall back to current behavior

            body_params.append(Schema__Endpoint__Param(name        = param.name,
                                                       param_type  = param_type,                                       # Now the original Type_Safe class!
                                                       required    = param.required,
                                                       description = param.field_info.description))
        return body_params

    @type_safe
    def extract__return_type(self, route: APIRoute):                                                # Get return type from endpoint callable
        if hasattr(route, 'endpoint') and route.endpoint:
            if hasattr(route.endpoint, '__original_return_type__'):                                 # check if Type_Safe__Route__Wrapper added the __original_return_type__
                return route.endpoint.__original_return_type__
            sig = inspect.signature(route.endpoint)
            if sig.return_annotation != inspect.Parameter.empty:
                return sig.return_annotation
        return None

    @type_safe
    def create_websocket_route(self, route : APIWebSocketRoute                            ,          # WebSocket route
                                     path  : Safe_Str__Fast_API__Route__Prefix
                                ) -> Schema__Fast_API__Route:                               # Returns route schema
        return Schema__Fast_API__Route(http_path    = path                       ,
                                       method_name  = Safe_Str__Id(route.name)   ,          # if route.name else Safe_Str__Id("websocket"),
                                       http_methods = []                         ,          # WebSockets don't use HTTP methods
                                       route_type   = Enum__Fast_API__Route__Type.WEBSOCKET)


    def extract__route_class(self, route) -> Safe_Str__Id:                                          # Extract class name (in most cases it will be something like Routes__* )
        route_class = None
        if hasattr(route, 'endpoint'):
            if hasattr(route.endpoint, '__self__'):                                                 # first try to get the class name (if inside a class)
                route_class = Safe_Str__Id(route.endpoint.__self__.__class__.__name__)
            elif hasattr(route.endpoint, '__qualname__'):                                           # then if that is not available use __qualname__
                qualname = route.endpoint.__qualname__
                if '.' in qualname:                                                                 # todo: see if there is a better way to do this and find the base class name
                    route_class = qualname.split('.')[0]
        return Safe_Str__Id(route_class)

    def is_default_route(self, path: str) -> bool:                                              # Check if default route
        return path in FAST_API_DEFAULT_ROUTES_PATHS