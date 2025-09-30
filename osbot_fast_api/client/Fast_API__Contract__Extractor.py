import inspect
from typing                                                          import Dict, List, Any, Optional

from osbot_fast_api.schemas.routes.Schema__Fast_API__Route import Schema__Fast_API__Route
from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from osbot_fast_api.client.Fast_API__Route__Extractor import Fast_API__Route__Extractor
from osbot_fast_api.schemas.for_osbot_utils.enums.Enum__Http__Method import Enum__Http__Method
from osbot_utils.type_safe.Type_Safe                                 import Type_Safe
from osbot_utils.helpers.ast                                         import Ast_Module
from osbot_utils.helpers.ast.Ast_Visit                               import Ast_Visit
from osbot_fast_api.api.Fast_API                                     import Fast_API
from osbot_fast_api.client.schemas.Schema__Endpoint__Contract        import Schema__Endpoint__Contract
from osbot_fast_api.client.schemas.Schema__Endpoint__Param           import Schema__Endpoint__Param
from osbot_fast_api.client.schemas.Schema__Routes__Module            import Schema__Routes__Module
from osbot_fast_api.client.schemas.Schema__Service__Contract         import Schema__Service__Contract
from osbot_fast_api.client.schemas.enums.Enum__Param__Location       import Enum__Param__Location


class Fast_API__Contract__Extractor(Type_Safe):
    fast_api        : Fast_API                                                                      # Fast_API instance to extract from

    @cache_on_self
    def route_extractor(self):
        return Fast_API__Route__Extractor(app             = self.fast_api.app(),
                                          include_default = False              ,                    # todo: see if we need to have these values as configurable defaults
                                          expand_mounts   = False              )
    def extract_contract(self) -> Schema__Service__Contract:                                        # Extract contract from Fast_API instance using routes + AST analysis
                                                                                                    # Create base contract
        contract = Schema__Service__Contract(service_name    = self.fast_api.name       ,
                                             version          = self.fast_api.version   ,
                                             base_path        = self.fast_api.base_path ,
                                             service_version  = self.fast_api.version   )
                                                                                               # Get all routes from FastAPI
        #all_routes = self.fast_api.routes()
        all_routes = self.route_extractor().extract_routes().routes
                                                                                            # Organize routes by module/class
        routes_by_module = self._organize_routes_by_module(all_routes)
                                                                                            # Process each module
        for module_name, route_info in routes_by_module.items():
            module = Schema__Routes__Module(module_name   = module_name          ,
                                            route_classes = route_info['classes'],
                                            endpoints     = []                   )
                                                                                        # Process each route in the module
            for route_data in route_info['routes']:
                endpoint = self._extract_endpoint_contract(route_data)
                if endpoint:
                    endpoint.route_module = module_name
                    module.endpoints.append(endpoint)
                    contract.endpoints.append(endpoint)

            if module.endpoints:                                                   # Only add modules with endpoints
                contract.modules.append(module)

        return contract

    def _organize_routes_by_module(self, routes: List[Schema__Fast_API__Route]                        # List of route dictionaries
                                    ) -> Dict[str, Dict]:                          # Organize routes by module based on class names and paths

        routes_by_module = {}

        for route in routes:
            method_name = route.method_name
            http_path   = route.http_path
                                                                                    # Extract module from path or method name
            module_name = self._extract_module_name(http_path, method_name)
            route_class = self._extract_route_class(method_name)

            if module_name not in routes_by_module:
                routes_by_module[module_name] = {'classes': []    ,
                                                'routes' : []    }

            if route_class and route_class not in routes_by_module[module_name]['classes']:
                routes_by_module[module_name]['classes'].append(route_class)

            routes_by_module[module_name]['routes'].append(route)

        return routes_by_module

    def _extract_module_name(self, path        : str ,                             # HTTP path
                                   method_name   : str                               # Method name
                              ) -> str:                                               # Extract module name from path or method name
                                                                                    # Try to extract from path first
        if path and path != '/':
            parts = path.strip('/').split('/')                                     # Common modules based on path
            if parts[0] in ['admin', 'file', 'data', 'zip', 'config', 'auth']:
                return parts[0]
                                                                                    # Try to extract from method name if it follows Routes__Module__Operation pattern
        if '__' in method_name:                                                    # Look for Routes__ pattern in the FastAPI app
            for route_obj in self.fast_api.app().routes:
                if hasattr(route_obj, 'endpoint'):
                    if route_obj.endpoint.__name__ == method_name:
                        qualname = route_obj.endpoint.__qualname__
                        if 'Routes__' in qualname:                                 # Extract module from Routes__Module__Operation
                            parts = qualname.split('.')
                            for part in parts:
                                if part.startswith('Routes__'):
                                    module_parts = part.replace('Routes__', '').split('__')
                                    if len(module_parts) > 0:
                                        return module_parts[0].lower()

        return 'root'                                                              # Default module for unclassified routes

    def _extract_route_class(self, method_name: str                                # Method name to extract class from
                           ) -> Optional[str]:                                     # Extract the Routes__* class name from method
                                                                                    # Try to find the actual route class
        for route_obj in self.fast_api.app().routes:
            if hasattr(route_obj, 'endpoint'):
                if route_obj.endpoint.__name__ == method_name:
                    qualname = route_obj.endpoint.__qualname__
                    if '.' in qualname:
                        class_name = qualname.split('.')[0]
                        if class_name.startswith('Routes__'):
                            return class_name

        return None

    def _extract_endpoint_contract(self, route_data: Schema__Fast_API__Route                          # Route data dictionary
                                 ) -> Optional[Schema__Endpoint__Contract]:       # Extract endpoint contract from route data

        method_name  = route_data.method_name
        http_path    = route_data.http_path
        http_methods = route_data.http_methods

        if not method_name or not http_path:
            return None
                                                                                    # Create base endpoint contract
        endpoint = Schema__Endpoint__Contract(operation_id = method_name                                                                    ,
                                              path_pattern = http_path                                                                     ,
                                              method       = Enum__Http__Method(http_methods[0]) if http_methods else Enum__Http__Method.GET,
                                              route_method = method_name)
                                                                                    # Find the actual endpoint function
        endpoint_func = None
        for route_obj in self.fast_api.app().routes:
            if hasattr(route_obj, 'endpoint'):
                if route_obj.endpoint.__name__ == method_name:
                    endpoint_func = route_obj.endpoint
                                                                                    # Extract route class
                    qualname = route_obj.endpoint.__qualname__
                    if '.' in qualname:
                        endpoint.route_class = qualname.split('.')[0]
                                                                                    # Extract path parameters from route
                    if hasattr(route_obj, 'path_regex'):                           # Extract {param} patterns
                        import re
                        param_pattern = r'\{(\w+)\}'
                        path_params   = re.findall(param_pattern, http_path)
                        for param_name in path_params:
                            endpoint.path_params.append(Schema__Endpoint__Param(
                                name       = param_name                        ,
                                location   = Enum__Param__Location.PATH        ,
                                param_type = 'str'                               # Default to str, will be enhanced
                            ))
                    break
                                                                                    # Enhance with function signature analysis
        if endpoint_func:
            self._enhance_with_signature(endpoint, endpoint_func)                  # Try AST analysis for error codes
            self._enhance_with_ast_analysis(endpoint, endpoint_func)

        return endpoint

    def _enhance_with_signature(self, endpoint : Schema__Endpoint__Contract ,      # Endpoint to enhance
                                     func      : callable                           # Function to analyze
                              ):                                                   # Enhance endpoint with function signature information

        try:
            sig = inspect.signature(func)

            for param_name, param in sig.parameters.items():                      # Skip self, request, response
                if param_name in ['self', 'request', 'response']:
                    continue
                                                                                    # Check if it's a path parameter
                is_path_param = any(p.name == param_name for p in endpoint.path_params)
                                                                                    # Get type annotation
                param_type = 'Any'
                if param.annotation != inspect.Parameter.empty:
                    param_type = self._type_to_string(param.annotation)
                                                                                    # Determine if it's a body parameter (Type_Safe class)
                if self._is_type_safe_class(param.annotation):
                    endpoint.request_schema = param_type
                    continue
                                                                                    # Add as query parameter if not a path parameter
                if not is_path_param:
                    endpoint.query_params.append(Schema__Endpoint__Param(
                        name       = param_name                                                                         ,
                        location   = Enum__Param__Location.QUERY                                                       ,
                        param_type = param_type                                                                        ,
                        required   = param.default == inspect.Parameter.empty                                          ,
                        default    = None if param.default == inspect.Parameter.empty else str(param.default)
                    ))
                else:                                                               # Update path parameter type
                    for p in endpoint.path_params:
                        if p.name == param_name:
                            p.param_type = param_type
                            break
                                                                                    # Get return type
            if sig.return_annotation != inspect.Parameter.empty:
                return_type = self._type_to_string(sig.return_annotation)
                if return_type not in ['None', 'Any']:
                    endpoint.response_schema = return_type

        except Exception:
            pass                                                                    # Continue without signature enhancement

    def _enhance_with_ast_analysis(self, endpoint : Schema__Endpoint__Contract ,   # Endpoint to enhance
                                        func      : callable                       # Function to analyze
                                 ):                                                # Use AST to find error codes raised in the function

        try:                                                                       # Get source code and parse with AST
            source     = inspect.getsource(func)
            ast_module = Ast_Module(source)

            with Ast_Visit(ast_module) as visitor:
                visitor.capture('Ast_Raise')
                visitor.visit()

                for raise_node in visitor.captured_nodes().get('Ast_Raise', []):   # Look for HTTPException with status codes
                    status_code = self._extract_status_code_from_raise(raise_node)
                    if status_code and status_code not in [400, 422]:              # Exclude validation errors
                        if status_code not in endpoint.error_codes:
                            endpoint.error_codes.append(status_code)

        except Exception:
            pass                                                                    # Continue without AST enhancement

    def _extract_status_code_from_raise(self, raise_node                           # AST raise node
                                      ) -> Optional[int]:                          # Extract status code from a raise node
                                                                                    # This would need more sophisticated AST analysis
                                                                                    # For now, return common error codes found in the raise
                                                                                    # In a full implementation, we'd parse the HTTPException arguments

        node_info = raise_node.info()
        if 'HTTPException' in str(node_info):                                      # Look for common status codes in the node
            for code in [401, 403, 404, 409, 410, 500, 502, 503]:
                if str(code) in str(node_info):
                    return code

        return None

    def _type_to_string(self, type_hint: Any                                       # Type hint to convert
                      ) -> str:                                                    # Convert type hint to string representation

        if type_hint is None:
            return 'None'

        if hasattr(type_hint, '__name__'):
            return type_hint.__name__
                                                                                    # Handle typing module types
        type_str = str(type_hint)
                                                                                    # Clean up common patterns
        type_str = type_str.replace('typing.', '')
        type_str = type_str.replace('<class ', '').replace('>', '')
        type_str = type_str.replace("'", "")

        return type_str

    def _is_type_safe_class(self, type_hint: Any                                   # Type hint to check
                          ) -> bool:                                               # Check if type hint is a Type_Safe class

        if type_hint is None or type_hint == inspect.Parameter.empty:
            return False

        try:                                                                       # Check if it's a class and inherits from Type_Safe
            if inspect.isclass(type_hint):
                from osbot_utils.type_safe.Type_Safe import Type_Safe
                return issubclass(type_hint, Type_Safe)
        except:
            pass

        return False