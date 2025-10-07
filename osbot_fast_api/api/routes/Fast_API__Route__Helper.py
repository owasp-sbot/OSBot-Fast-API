from typing                                                               import Callable
from fastapi                                                              import FastAPI
from osbot_utils.type_safe.Type_Safe                                      import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe            import type_safe
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Registration   import Type_Safe__Route__Registration


class Fast_API__Route__Helper(Type_Safe):                               # Helper class to add route registration methods to Fast_API
    route_registration : Type_Safe__Route__Registration

    @type_safe
    def add_route(self, app       : FastAPI ,                           # FastAPI app instance
                        function  : Callable,                           # Function to register
                        methods   : list                                # HTTP methods
                     ):                                                 # Register route on app router
        self.route_registration.register_route(app.router, function, methods)

    @type_safe
    def add_route_get(self, app       : FastAPI ,                       # FastAPI app instance
                            function  : Callable                        # Function to register
                         ):                                             # Register GET route
        self.add_route(app, function, methods=['GET'])

    @type_safe
    def add_route_post(self, app       : FastAPI ,                      # FastAPI app instance
                             function  : Callable                       # Function to register
                          ):                                             # Register POST route
        self.add_route(app, function, methods=['POST'])

    @type_safe
    def add_route_put(self, app       : FastAPI ,                       # FastAPI app instance
                            function  : Callable                        # Function to register
                         ):                                             # Register PUT route
        self.add_route(app, function, methods=['PUT'])

    @type_safe
    def add_route_delete(self, app       : FastAPI ,                    # FastAPI app instance
                               function  : Callable                     # Function to register
                            ):                                          # Register DELETE route
        self.add_route(app, function, methods=['DELETE'])

    @type_safe
    def add_route_any(self, app       : FastAPI  ,                       # FastAPI app instance
                            function  : Callable ,                       # Function to register
                            path      : str      = None                  # Optional explicit path   # todo: replace str with a Safe_Str__* class
                         ):                                              # Register route accepting ANY HTTP method
        self.route_registration.register_route_any(app.router, function, path)