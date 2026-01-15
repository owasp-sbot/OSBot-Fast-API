import re
import inspect
from typing                                                                                 import List, Any, Optional
from osbot_fast_api.api.schemas.Schema__Fast_API__Tag__Classes_And_Routes                   import Schema__Fast_API__Tag__Classes_And_Routes
from osbot_fast_api.api.schemas.Schema__Fast_API__Tags__Classes_And_Routes                  import Schema__Fast__API_Tags__Classes_And_Routes
from osbot_fast_api.api.schemas.routes.Schema__Fast_API__Route                              import Schema__Fast_API__Route
from osbot_utils.decorators.methods.cache_on_self                                           import cache_on_self
from osbot_fast_api.client.Fast_API__Route__Extractor                                       import Fast_API__Route__Extractor
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.helpers.ast                                                                import Ast_Module
from osbot_utils.helpers.ast.Ast_Visit                                                      import Ast_Visit
from osbot_fast_api.api.Fast_API                                                            import Fast_API
from osbot_fast_api.client.schemas.Schema__Endpoint__Contract                               import Schema__Endpoint__Contract
from osbot_fast_api.client.schemas.Schema__Endpoint__Param                                  import Schema__Endpoint__Param
from osbot_fast_api.client.schemas.Schema__Routes__Module                                   import Schema__Routes__Module
from osbot_fast_api.client.schemas.Schema__Service__Contract                                import Schema__Service__Contract
from osbot_fast_api.client.schemas.enums.Enum__Param__Location                              import Enum__Param__Location
from osbot_utils.type_safe.primitives.domains.http.enums.Enum__Http__Method                 import Enum__Http__Method
from osbot_utils.type_safe.primitives.domains.python.safe_str.Safe_Str__Python__Module      import Safe_Str__Python__Module


class Fast_API__Contract__Extractor(Type_Safe):
    fast_api        : Fast_API                                                                      # Fast_API instance to extract from

    @cache_on_self
    def route_extractor(self):
        return Fast_API__Route__Extractor(app             = self.fast_api.app(),
                                          include_default = False              ,                    # todo: see if we need to have these values as configurable defaults
                                          expand_mounts   = False              )

    def fast_api__all_routes(self) -> List[Schema__Fast_API__Route]:
        return self.route_extractor().extract_routes().routes

    def extract_contract(self) -> Schema__Service__Contract:
        contract = Schema__Service__Contract(service_name    = self.fast_api.config.name       ,
                                             version         = self.fast_api.config.version    ,
                                             base_path       = self.fast_api.config.base_path  ,
                                             service_version = self.fast_api.config.version    )

        all_routes       = self.fast_api__all_routes()
        routes_by_module = self.organize_routes__by_tag(all_routes)

        for route_tag, route_info in routes_by_module.by_tag.items():
            module_name = Safe_Str__Python__Module(route_tag)                                   # we need to convert the route_tag into an module name
            route_classes = list(route_info.classes)                                            # we need to convert to list because route_info.classes is a 'set' (more specifically Type_Safe__Set)
            module      = Schema__Routes__Module(module_name   = module_name            ,
                                                 route_classes = route_classes          ,       # note: Schema__Routes__Module will convert the list into Type_Safe__List
                                                 endpoints     = []                     )
            for route_data in route_info.routes:                                 # Now returns a list of contracts
                endpoint_contracts = self.extract_endpoint_contracts(route_data)
                for endpoint in endpoint_contracts:
                    if endpoint:
                        endpoint.route_module = module_name
                        module.endpoints.append(endpoint)
                        contract.endpoints.append(endpoint)

            if module.endpoints:
                contract.modules.append(module)

        return contract

    def organize_routes__by_tag(self, routes: List[Schema__Fast_API__Route]  # List of route dictionaries
                                 ) -> Schema__Fast__API_Tags__Classes_And_Routes:      # Organize routes by tag based on class names and paths

        routes_by_tag = Schema__Fast__API_Tags__Classes_And_Routes()
        for route in routes:
            route_tags  = route.route_tags or ['root']
            for route_tag in route_tags:
                route_class = route.route_class

                if route_tag in routes_by_tag.by_tag:
                    classes_and_routes = routes_by_tag.by_tag[route_tag]
                else:
                    classes_and_routes = Schema__Fast_API__Tag__Classes_And_Routes()
                    routes_by_tag.by_tag[route_tag] = classes_and_routes

                with classes_and_routes as _:
                    _.classes.add(route_class)
                    _.routes.append(route)

        return routes_by_tag


    def extract_endpoint_contracts(self, route_data: Schema__Fast_API__Route
                                   ) -> List[Schema__Endpoint__Contract]:                   # Now returns a List
        method_name  = route_data.method_name
        http_path    = route_data.http_path
        http_methods = route_data.http_methods

        if not method_name or not http_path:
            return []

        contracts = []

        for http_method in (http_methods or [Enum__Http__Method.GET]):                      # Create one contract per HTTP method
            operation_id = f"{http_method.value.lower()}__{method_name}"                    # Create operation_id with HTTP method prefix

            endpoint = Schema__Endpoint__Contract(operation_id = operation_id            ,
                                                  path_pattern = http_path               ,
                                                  method       = http_method             ,
                                                  route_method = method_name             ,
                                                  path_params  = route_data.path_params  ,      # Copy extracted params
                                                  query_params = route_data.query_params )      # Copy extracted params

            endpoint_func = None                                                            # Find the actual endpoint function (same for all methods)
            for route_obj in self.fast_api.app().routes:
                if hasattr(route_obj, 'endpoint'):
                    if route_obj.endpoint.__name__ == method_name:
                        endpoint_func = route_obj.endpoint

                        qualname = route_obj.endpoint.__qualname__                          # Extract route class
                        if '.' in qualname:
                            endpoint.route_class = qualname.split('.')[0]

            # Enhance with function signature analysis (same for all methods)
            if endpoint_func:
                self._enhance_with_signature(endpoint, endpoint_func)
                self._enhance_with_ast_analysis(endpoint, endpoint_func)

            contracts.append(endpoint)
        return contracts


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