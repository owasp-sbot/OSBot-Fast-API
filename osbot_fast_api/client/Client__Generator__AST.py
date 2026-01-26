from typing                                                     import Dict, List, Any
from osbot_utils.type_safe.type_safe_core.decorators.type_safe  import type_safe
from osbot_fast_api.client.schemas.Schema__Endpoint__Contract   import Schema__Endpoint__Contract
from osbot_fast_api.client.schemas.Schema__Routes__Module       import Schema__Routes__Module
from osbot_fast_api.client.schemas.Schema__Service__Contract    import Schema__Service__Contract
from osbot_utils.type_safe.Type_Safe                            import Type_Safe


class Client__Generator__AST(Type_Safe):
    contract    : Schema__Service__Contract                                        # Contract to generate client from
    client_name : str = None                                                       # Base name for client (e.g., "Cache__Client")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.client_name:                                                   # Generate client name from service name
            service_name     = self.contract.service_name.replace('-', '_').replace(' ', '_')
            self.client_name = f"{service_name}__Client"

    def generate_client_files(self) -> Dict[str, str]:                             # Generate all client files from contract

        files = {}
                                                                                    # Generate main client class
        main_client_code = self._generate_main_client()
        files[f"{self.client_name}.py"] = main_client_code
                                                                                    # Generate request handler
        request_handler_code = self._generate_request_handler()
        files[f"{self.client_name}__Requests.py"] = request_handler_code
                                                                                    # Generate config class
        config_code = self._generate_config_class()
        files[f"{self.client_name}__Config.py"] = config_code
                                                                                    # Generate module clients
        for module in self.contract.modules:
            module_files = self._generate_module_client_files(module)
            files.update(module_files)

        return files

    @type_safe
    def _type_to_string(self, type_hint: Any) -> str:                                       #  Convert a type object to a usable string for code generation. Handles Type_Safe classes, primitives, and built-in types.

        if type_hint is None:
            return 'None'

        if isinstance(type_hint, type):                                                     # Handle Type objects - extract the class name
            if hasattr(type_hint, '__name__'):                                              # For Type_Safe classes, use just the class name
                return type_hint.__name__

        if isinstance(type_hint, str):                                                      # Handle string annotations (already strings)
            return type_hint

        type_str = str(type_hint)                                                           # Handle typing module types (Optional, List, etc.)
        type_str = type_str.replace('typing.', '')                                          # todo: check if there is a better way to do this
        type_str = type_str.replace('<class ', '').replace('>', '')
        type_str = type_str.replace("'", "")

        return type_str

# todo: see if we can fix this AST generation since it was causing a problem where the methods were not pad alligned with 4 spaces
#       I think this is because the AST parser was creating them at the root of the code (i.e. aligned left)
#       The _generate_main_client version (after this one, does the concat correctly)

#     def _generate_main_client(self) -> str:                                        # Generate the main client class with module accessors
#                                                                                     # Start with imports
#         imports = f'''from osbot_utils.type_safe.Type_Safe import Type_Safe
# from osbot_utils.decorators.methods.cache_on_self import cache_on_self
# from .{self.client_name}__Config import {self.client_name}__Config
# from .{self.client_name}__Requests import {self.client_name}__Requests'''
#                                                                                     # Add imports for module clients
#         for module in self.contract.modules:
#             module_client_name = self._get_module_client_name(module.module_name)
#             imports += f'\nfrom .{module.module_name}.{module_client_name} import {module_client_name}'
#                                                                                     # Create class template
#         class_template = f'''
#
# class {self.client_name}(Type_Safe):
#     config   : {self.client_name}__Config
#     _requests: {self.client_name}__Requests = None
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)                                                 # Initialize request handler with config
#         if not self._requests:
#             self._requests = {self.client_name}__Requests(config=self.config)
#
#     @cache_on_self
#     def requests(self) -> {self.client_name}__Requests:                            # Access the unified request handler
#         return self._requests'''
#                                                                                     # Parse template and add module accessors
#         ast_module = Ast_Module(imports + class_template)
#                                                                                     # Add module accessor methods
#         module_methods = []
#         for module in self.contract.modules:
#             method_code = self._generate_module_accessor_method(module.module_name)
#             module_methods.append(method_code)
#                                                                                     # Merge all code
#         merger = Ast_Merge()
#         merger.merge_module(ast_module)
#
#         for method_code in module_methods:
#             method_module = Ast_Module(method_code)
#             merger.merge_module(method_module)
#
#         return merger.source_code()

    def _generate_main_client(self) -> str:
        # Imports
        imports = f'''from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from .{self.client_name}__Config import {self.client_name}__Config
from .{self.client_name}__Requests import {self.client_name}__Requests'''

        # Add imports for module clients
        for module in self.contract.modules:
            module_client_name = self._get_module_client_name(module.module_name)
            imports += f'\nfrom .{module.module_name}.{module_client_name} import {module_client_name}'

        # Class definition with requests method
        class_code = f'''

class {self.client_name}(Type_Safe):
    config   : {self.client_name}__Config
    _requests: {self.client_name}__Requests = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)                                                 # Initialize request handler with config
        if not self._requests:
            self._requests = {self.client_name}__Requests(config=self.config)

    @cache_on_self
    def requests(self) -> {self.client_name}__Requests:                            # Access the unified request handler
        return self._requests'''

        # Add module accessor methods
        for module in self.contract.modules:
            method_code = self._generate_module_accessor_method(module.module_name)
            class_code += '\n' + method_code  # Just concatenate with newline

        return imports + class_code

    def _generate_module_accessor_method(self, module_name: str) -> str:           # Generate a @cache_on_self method to access a module client

        module_client_name = self._get_module_client_name(module_name)

        return f'''
    @cache_on_self
    def {module_name}(self) -> {module_client_name}:                               # Access {module_name} operations
        return {module_client_name}(_client=self)'''

    def _generate_request_handler(self) -> str:                                    # Generate the request handler with three execution modes

        return f'''from enum import Enum
from typing import Any, Optional, Dict
import requests
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Enum__Fast_API__Service__Registry__Client__Mode(str, Enum):
    REMOTE       = "remote"                                                        # HTTP calls to deployed service
    IN_MEMORY    = "in_memory"                                                     # FastAPI TestClient (same process)
    LOCAL_SERVER = "local_server"                                                  # Fast_API_Server (local HTTP)

class {self.client_name}__Requests__Result(Type_Safe):
    status_code : int
    json        : Optional[Dict] = None
    text        : Optional[str]  = None
    content     : bytes          = b""
    headers     : Dict[str, str] = {{}}
    path        : str            = ""

class {self.client_name}__Requests(Type_Safe):
    config       : Any                                                             # {self.client_name}__Config
    mode         : Enum__Fast_API__Service__Registry__Client__Mode         = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE
    _app         : Optional[Any]              = None                               # FastAPI app for in-memory
    _server      : Optional[Any]              = None                               # Fast_API_Server for local
    _test_client : Optional[Any]              = None                               # TestClient for in-memory
    _session     : Optional[requests.Session] = None                               # Session for remote

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_mode()

    def _setup_mode(self):                                                         # Initialize the appropriate execution backend

        if self._app:                                                              # In-memory mode with TestClient
            self.mode = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY
            from fastapi.testclient import TestClient
            self._test_client = TestClient(self._app)

        elif self._server:                                                         # Local server mode
            self.mode = Enum__Fast_API__Service__Registry__Client__Mode.LOCAL_SERVER
            from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server
            if not isinstance(self._server, Fast_API_Server):
                self._server = Fast_API_Server(app=self._server)
                self._server.start()

        else:                                                                      # Remote mode
            self.mode     = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE
            self._session = requests.Session()
            self._configure_session()

    def _configure_session(self):                                                  # Configure session for remote calls
        if self._session:                                                          # Add any auth headers from config
            if hasattr(self.config, 'api_key') and self.config.api_key:
                self._session.headers['Authorization'] = f'Bearer {{self.config.api_key}}'

    def execute(self, method  : str              ,                                 # HTTP method (GET, POST, etc)
                     path     : str              ,                                 # Endpoint path
                     body     : Any        = None,                                 # Request body
                     headers  : Optional[Dict] = None                              # Additional headers
               ) -> {self.client_name}__Requests__Result:                          # Execute request transparently based on mode
                                                                                    # Merge headers
        request_headers = {{**self.auth_headers(), **(headers or {{}})}}
                                                                                    # Execute based on mode
        if self.mode == Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY:
            response = self._execute_in_memory(method, path, body, request_headers)
        elif self.mode == Enum__Fast_API__Service__Registry__Client__Mode.LOCAL_SERVER:
            response = self._execute_local_server(method, path, body, request_headers)
        else:
            response = self._execute_remote(method, path, body, request_headers)
                                                                                    # Convert to unified result
        return self._build_result(response, path)

    def _execute_in_memory(self, method  : str  ,                                  # HTTP method
                                path     : str  ,                                  # Endpoint path
                                body     : Any  ,                                  # Request body
                                headers  : Dict                                    # Headers
                         ):                                                        # Execute using FastAPI TestClient
        method_func = getattr(self._test_client, method.lower())
        if body:
            return method_func(path, json=body, headers=headers)
        else:
            return method_func(path, headers=headers)

    def _execute_local_server(self, method  : str  ,                               # HTTP method
                                   path     : str  ,                               # Endpoint path
                                   body     : Any  ,                               # Request body
                                   headers  : Dict                                 # Headers
                            ):                                                     # Execute using local Fast_API_Server
        url         = f"{{self._server.url()}}{{path}}"
        method_func = getattr(requests, method.lower())
        if body:
            return method_func(url, json=body, headers=headers)
        else:
            return method_func(url, headers=headers)

    def _execute_remote(self, method  : str  ,                                     # HTTP method
                             path     : str  ,                                     # Endpoint path
                             body     : Any  ,                                     # Request body
                             headers  : Dict                                       # Headers
                      ):                                                           # Execute using requests to remote service
        url         = f"{{self.config.base_url}}{{path}}"
        method_func = getattr(self._session, method.lower())
        if body:
            return method_func(url, json=body, headers=headers)
        else:
            return method_func(url, headers=headers)

    def _build_result(self, response ,                                             # Response object
                           path                                                    # Path requested
                    ) -> {self.client_name}__Requests__Result:                     # Convert any response type to unified result

        json_data = None
        text_data = None
                                                                                    # Try to extract JSON
        try:
            json_data = response.json()
        except:
            pass
                                                                                    # Try to extract text
        try:
            text_data = response.text
        except:
            pass

        return {self.client_name}__Requests__Result(
            status_code = response.status_code                                   ,
            json        = json_data                                             ,
            text        = text_data                                             ,
            content     = response.content if hasattr(response, 'content') else b"",
            headers     = dict(response.headers) if hasattr(response, 'headers') else {{}},
            path        = path
        )

    def auth_headers(self) -> Dict[str, str]:                                      # Get authentication headers from config
        headers = {{}}
                                                                                    # Add API key if configured
        if hasattr(self.config, 'api_key_header') and hasattr(self.config, 'api_key'):
            if self.config.api_key_header and self.config.api_key:
                headers[self.config.api_key_header] = self.config.api_key

        return headers'''

    def _generate_config_class(self) -> str:                                       # Generate configuration class for the client

        return f'''from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from typing import Optional

class {self.client_name}__Config(Type_Safe):
    base_url        : Safe_Str__Url = "http://localhost:8000"                      # Default to local
    api_key         : Optional[str] = None                                         # Optional API key
    api_key_header  : str           = "X-API-Key"                                  # Header name for API key
    timeout         : int           = 30                                           # Request timeout in seconds
    verify_ssl      : bool          = True                                         # Verify SSL certificates
                                                                                    # Service-specific configuration can be added here
    service_name    : Safe_Str__Id  = "{self.contract.service_name}"
    service_version : str           = "{self.contract.service_version}"'''

    def _generate_module_client_files(self, module: Schema__Routes__Module         # Module to generate clients for
                                     ) -> Dict[str, str]:                          # Generate client files for a specific module

        files = {}
                                                                                   # Group endpoints by route class
        endpoints_by_class = {}
        for endpoint in module.endpoints:
            route_class = endpoint.route_class or f"Routes__{module.module_name.title()}"
            if route_class not in endpoints_by_class:
                endpoints_by_class[route_class] = []
            endpoints_by_class[route_class].append(endpoint)
                                                                                   # Generate a client class for each route class
        for route_class, endpoints in endpoints_by_class.items():
            client_class_name = route_class.replace('Routes__', f'{self.client_name}__')
            client_code       = self._generate_route_client_class(client_class_name, endpoints, module.module_name)
                                                                                   # Determine file path
            file_path         = f"{module.module_name}/{client_class_name}.py"
            files[file_path]  = client_code
                                                                                   # If module has multiple route classes, create a module aggregator
        if len(endpoints_by_class) > 1:
            aggregator_code = self._generate_module_aggregator(module, endpoints_by_class.keys())
            files[f"{module.module_name}/{self._get_module_client_name(module.module_name)}.py"] = aggregator_code

        return files

    def _generate_route_client_class(self, class_name   : str                    ,  # Name for the client class
                                          endpoints     : List[Schema__Endpoint__Contract], # Endpoints to generate methods for
                                          module_name   : str                        # Module name for context
                                    ) -> str:                                        # Generate a client class for specific route endpoints
                                                                                     # Start with imports
        imports = f'''from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe'''
                                                                                     # Add specific imports for schemas used by endpoints
        schema_imports = self._get_schema_imports(endpoints)
        if schema_imports:
            imports += f'\n{schema_imports}'
                                                                                     # Create class template
        class_template = f'''

class {class_name}(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()'''
                                                                                     # Generate methods for each endpoint
        methods_code = []
        for endpoint in endpoints:
            method_code = self._generate_endpoint_method(endpoint)
            methods_code.append(method_code)
                                                                                     # Combine everything
        full_code = imports + class_template
        for method in methods_code:
            full_code += f'\n{method}'

        return full_code

    def _generate_endpoint_method(self, endpoint: Schema__Endpoint__Contract       # Endpoint to generate method for
                                 ) -> str:                                         # Generate a method for a specific endpoint
                                                                                   # Build method signature
        method_name  = endpoint.route_method
        params       = self._build_method_params(endpoint)
        if endpoint.response_schema:
            return_type = self._type_to_string(endpoint.response_schema)
        else:
            return_type = 'Dict'

        path_construction = self._build_path_construction(endpoint)
        # body_handling     = self._build_body_handling(endpoint)
        error_handling    = self._build_error_handling(endpoint)
        response_handling = self._build_response_handling(endpoint, return_type)  # Pass clean string
                                                                                       # Build path construction

                                                                                   # Build request body handling
        if endpoint.request_schema:
            body_handling = f"\n        body = request.json() if hasattr(request, 'json') else request"
        else:
            body_handling = "\n        body = None"
                                                                                   # Build error handling
        # error_handling = self._build_error_handling(endpoint)
        #                                                                            # Build response handling
        # response_handling = self._build_response_handling(endpoint)

        method_code = f'''
    def {method_name}(self{params}) -> {return_type}:                              # Auto-generated from endpoint {endpoint.operation_id}
                                                                                    # Build path{path_construction}{body_handling}
                                                                                    # Execute request
        result = self.requests.execute(
            method = "{endpoint.method.value}",
            path   = path,
            body   = body
        ){error_handling}{response_handling}'''

        return method_code

    @type_safe
    def _build_method_params(self, endpoint: Schema__Endpoint__Contract) -> str:       # Build method parameters
        params = []

        for param in endpoint.path_params:                                              # Add path parameters
            param_type_str = self._type_to_string(param.param_type)                     # Convert type
            param_str = f", {param.name}: {param_type_str}"
            params.append(param_str)

        # Add query parameters
        for param in endpoint.query_params:
            param_type_str = self._type_to_string(param.param_type)                     # Convert type
            if param.required:
                param_str = f", {param.name}: {param_type_str}"
            else:
                default_val = param.default if param.default else "None"
                param_str = f", {param.name}: Optional[{param_type_str}] = {default_val}"
            params.append(param_str)

        if endpoint.request_schema:                                                     # Add request body if present
            request_type_str = self._type_to_string(endpoint.request_schema)            # Convert type
            params.append(f", request: {request_type_str}")

        return ''.join(params)

    def _build_path_construction(self, endpoint: Schema__Endpoint__Contract      # Endpoint to build path for
                               ) -> str:                                         # Build path construction code

        if '{' in endpoint.path_pattern:                                        # Path has parameters
            path_template = endpoint.path_pattern                               # Replace {param} with {{{param}}} for f-string
            for param in endpoint.path_params:
                path_template = path_template.replace(f'{{{param.name}}}', f'{{{{{param.name}}}}}')

            return f'''
        path = f"{path_template}"'''
        else:                                                                    # Static path
            return f'''
        path = "{endpoint.path_pattern}"'''

    def _build_error_handling(self, endpoint: Schema__Endpoint__Contract        # Endpoint to build error handling for
                            ) -> str:                                           # Build error handling based on endpoint error codes

        if not endpoint.error_codes:
            return ""

        handling = "\n\n                                                                                    # Handle errors"

        for code in endpoint.error_codes:
            if code == 404:
                handling += f'''
        if result.status_code == 404:
            raise Exception(f"Resource not found: {{path}}")'''
            elif code == 401:
                handling += f'''
        if result.status_code == 401:
            raise Exception("Unauthorized")'''
            elif code == 403:
                handling += f'''
        if result.status_code == 403:
            raise Exception("Forbidden")'''
            elif code >= 500:
                handling += f'''
        if result.status_code >= 500:
            raise Exception(f"Server error: {{result.status_code}}")'''

        return handling

    @type_safe
    def _build_response_handling(self, endpoint: Schema__Endpoint__Contract,
                                       return_type: str) -> str:                        # Build response handling with clean type string
        if endpoint.response_schema:
            # return_type is already a clean string now
            return f'''
                                                                                    # Return typed response
            if result.json:
                return {return_type}.from_json(result.json)
            else:
                return {return_type}()'''
        else:
            return '''
                                                                                    # Return response data
        return result.json if result.json else result.text'''

    def _generate_module_aggregator(self, module        : Schema__Routes__Module,  # Module to generate aggregator for
                                         route_classes  : List[str]                # Route classes to aggregate
                                   ) -> str:                                       # Generate aggregator class for modules with multiple route classes

        module_client_name = self._get_module_client_name(module.module_name)
                                                                                   # Build imports
        imports = "from osbot_utils.type_safe.Type_Safe import Type_Safe\n"
        imports += "from osbot_utils.decorators.methods.cache_on_self import cache_on_self\n"

        for route_class in route_classes:
            client_class = route_class.replace('Routes__', f'{self.client_name}__')
            imports += f"from .{client_class} import {client_class}\n"
                                                                                   # Build class
        class_code = f"\nclass {module_client_name}(Type_Safe):\n"
        class_code += "    _client: Any                                                                    # Reference to main client\n\n"
                                                                                   # Add accessor methods
        for route_class in route_classes:
            client_class = route_class.replace('Routes__', f'{self.client_name}__')
                                                                                   # Extract operation name from Routes__Module__Operation
            parts = route_class.replace('Routes__', '').split('__')
            if len(parts) > 1:
                operation_name = parts[-1].lower()
            else:
                operation_name = parts[0].lower()

            class_code += f'''    @cache_on_self
    def {operation_name}(self) -> {client_class}:                                  # Access {operation_name} operations
        return {client_class}(_client=self._client)

'''

        return imports + class_code

    def _get_module_client_name(self, module_name: str                          # Module name to generate client name for
                              ) -> str:                                         # Get the client name for a module
        return f"{self.client_name}__{module_name.title()}"

    @type_safe
    def _get_schema_imports(self, endpoints: List[Schema__Endpoint__Contract]) -> str:      # Get import statements for schemas
        schemas = set()

        for endpoint in endpoints:
            if endpoint.request_schema:
                schema_name = self._type_to_string(endpoint.request_schema)                 # Convert type
                schemas.add(schema_name)
            if endpoint.response_schema:
                schema_name = self._type_to_string(endpoint.response_schema)                # Convert type
                schemas.add(schema_name)

        if not schemas:
            return ""

        imports = []                                                                    # Generate proper imports (you'll need to figure out the import path)
        for schema in schemas:
            imports.append(f"from ..schemas import {schema}")                           # Clean schema name!

        return '\n'.join(imports)