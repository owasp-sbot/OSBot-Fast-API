from typing                                                                      import Callable
from fastapi                                                                     import APIRouter, FastAPI
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix       import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag          import Safe_Str__Fast_API__Route__Tag
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.decorators.lists.index_by                                       import index_by
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                   import type_safe
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Registration          import Type_Safe__Route__Registration


class Fast_API__Routes(Type_Safe):                                       # Base class for defining FastAPI route collections with Type_Safe support
    router             : APIRouter
    app                : FastAPI                           = None
    prefix             : Safe_Str__Fast_API__Route__Prefix = None
    tag                : Safe_Str__Fast_API__Route__Tag
    filter_tag         : bool                             = True
    route_registration : Type_Safe__Route__Registration                  # Unified route registration system

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.prefix:                                              # Auto-generate prefix from tag
            self.prefix = Safe_Str__Fast_API__Route__Prefix(self.tag)

    # -------------------- Core Route Registration Methods --------------------

    @type_safe
    def add_route(self, function : Callable,                            # Function to register
                        methods   : list                                # HTTP methods
                      ):                                                 # Register route with specified methods
        self.route_registration.register_route(self.router, function, methods)
        return self

    @type_safe
    def add_route_get(self, function : Callable                         # Function to register as GET
                       ):                                               # Register GET route with Type_Safe support
        return self.add_route(function, methods=['GET'])

    @type_safe
    def add_route_patch(self, function : Callable                        # Function to register as POST
                        ):                                              # Register POST route with Type_Safe support
        return self.add_route(function, methods=['PATCH'])


    @type_safe
    def add_route_post(self, function : Callable                        # Function to register as POST
                        ):                                              # Register POST route with Type_Safe support
        return self.add_route(function, methods=['POST'])

    @type_safe
    def add_route_put(self, function : Callable                         # Function to register as PUT
                       ):                                               # Register PUT route with Type_Safe support
        return self.add_route(function, methods=['PUT'])

    @type_safe
    def add_route_delete(self, function : Callable                      # Function to register as DELETE
                          ):                                            # Register DELETE route with Type_Safe support
        return self.add_route(function, methods=['DELETE'])

    @type_safe
    def add_route_any(self, function : Callable                        ,# Function to register
                           path      : str             = None          # Optional explicit path
                       ):                                              # Register route accepting ANY HTTP method
        self.route_registration.register_route_any(self.router, function, path)
        return self

    # -------------------- Batch Route Registration --------------------

    def add_routes_get(self, *functions):                                # Register multiple GET routes
        for function in functions:
            self.add_route_get(function)
        return self

    def add_routes_post(self, *functions):                               # Register multiple POST routes
        for function in functions:
            self.add_route_post(function)
        return self

    def add_routes_put(self, *functions):                                # Register multiple PUT routes
        for function in functions:
            self.add_route_put(function)
        return self

    def add_routes_delete(self, *functions):                             # Register multiple DELETE routes
        for function in functions:
            self.add_route_delete(function)
        return self

    # -------------------- Route Inspection --------------------

    def fast_api_utils(self):                                            # Get utility helper for route inspection
        from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils
        return Fast_API_Utils(self.app)

    @index_by
    def routes(self):                                                    # Get all routes in this router
        return self.fast_api_utils().fastapi_routes(router=self.router)

    def routes_methods(self):                                            # Get list of route method names
        return list(self.routes(index_by='method_name'))

    def routes_paths(self):                                              # Get sorted list of route paths
        return sorted(list(self.routes(index_by='http_path')))

    # -------------------- Setup and Lifecycle --------------------

    def setup(self):                                                     # Setup routes and register with app
        self.setup_routes()

        if self.prefix == '/':                                           # Root-level routes
            self.app.include_router(self.router, tags=[self.tag])
        else:                                                            # Prefixed routes
            self.app.include_router(self.router, prefix=self.prefix, tags=[self.tag])

        return self

    def setup_routes(self):                                              # Override this to define routes
        pass