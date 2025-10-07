from typing                                                             import Callable, List
from starlette.routing                                                  import Router
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe          import type_safe
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Analyzer     import Type_Safe__Route__Analyzer
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Converter    import Type_Safe__Route__Converter
from osbot_fast_api.api.routes.type_safe.Type_Safe__Route__Wrapper      import Type_Safe__Route__Wrapper
from osbot_fast_api.api.routes.Fast_API__Route__Parser                  import Fast_API__Route__Parser


class Type_Safe__Route__Registration(Type_Safe):                        # Unified system for registering routes with Type_Safe support
    analyzer       : Type_Safe__Route__Analyzer
    converter      : Type_Safe__Route__Converter
    wrapper_creator: Type_Safe__Route__Wrapper
    route_parser   : Fast_API__Route__Parser

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wrapper_creator.converter = self.converter              # Wire up dependencies

    @type_safe
    def register_route(self, router    : Router   ,                         # FastAPI router to register on
                             function  : Callable ,                         # Function to register
                             methods   : List[str]                          # HTTP methods (GET, POST, etc)
                         ):                                                 # Register a route with full Type_Safe support

        signature = self.analyzer.analyze_function                  (function           )   # Analyze function signature
        signature = self.converter.enrich_signature_with_conversions(signature          )   # Add conversion metadata
        wrapper   = self.wrapper_creator.create_wrapper             (function, signature)   # Create wrapper function
        if hasattr(function, '__route_path__'):                                             # if @route_path has been used
            path = function.__route_path__
        else:                                                                               # If not, use parser to generate from function name
            path  = self.route_parser.parse_route_path              (function           )   # Parse route path from function name

        router.add_api_route(path     = path    ,                       # Register with FastAPI
                            endpoint = wrapper  ,
                            methods  = methods  )

    @type_safe
    def register_route_any(self, router   : Router   ,                  # FastAPI router
                                 function : Callable ,                  # Function to register
                                 path     : str      = None             # Optional explicit path
                           ):                                           # Register route accepting ANY HTTP method

        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']

        if path:                                                         # Use explicit path if provided
            signature = self.analyzer.analyze_function(function)
            signature = self.converter.enrich_signature_with_conversions(signature)
            wrapper   = self.wrapper_creator.create_wrapper(function, signature)

            router.add_api_route(path     = path    ,
                                endpoint = wrapper  ,
                                methods  = methods  )
        else:
            self.register_route(router, function, methods)               # Use standard path parsing