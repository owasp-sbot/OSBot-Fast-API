from unittest                                                                import TestCase
from osbot_utils.utils.Misc                                                  import list_set
from osbot_utils.utils.Objects                                               import base_classes
from osbot_fast_api.client.Client__Generator__AST                            import Client__Generator__AST
from osbot_fast_api.client.schemas.Schema__Endpoint__Contract                import Schema__Endpoint__Contract
from osbot_fast_api.client.schemas.Schema__Endpoint__Param                   import Schema__Endpoint__Param
from osbot_fast_api.client.schemas.Schema__Routes__Module                    import Schema__Routes__Module
from osbot_fast_api.client.schemas.Schema__Service__Contract                 import Schema__Service__Contract
from osbot_fast_api.client.schemas.enums.Enum__Param__Location               import Enum__Param__Location
from osbot_utils.type_safe.primitives.domains.http.enums.Enum__Http__Method  import Enum__Http__Method
from osbot_fast_api.client.testing.Test__Fast_API__With_Routes               import Schema__User, Schema__Product
from osbot_utils.type_safe.Type_Safe                                         import Type_Safe

class test_Client__Generator__AST(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # ONE-TIME expensive setup
        cls.test_contract = cls._create_test_contract()
        cls.generator = Client__Generator__AST(contract    = cls.test_contract,
                                              client_name = "TestService__Client")

    def test__init__(self):                                                         # Test initialization and Type_Safe inheritance
        with Client__Generator__AST(contract=self.test_contract) as _:
            assert type(_)           is Client__Generator__AST
            assert base_classes(_)   == [Type_Safe, object]
            assert type(_.contract)  is Schema__Service__Contract
            assert _.contract        is self.test_contract
            assert _.client_name     == 'TestService__Client'                       # Auto-generated from service name

        # Test with custom client name
        with Client__Generator__AST(contract=self.test_contract, client_name="CustomClient") as _:
            assert _.client_name == "CustomClient"

    def test_generate_client_files(self):                                          # Test complete client file generation
        with self.generator as _:
            files = _.generate_client_files()

            assert type(files)                                 is dict
            assert list_set(files)                             == ['TestService__Client.py'                   ,
                                                                   'TestService__Client__Config.py'           ,
                                                                   'TestService__Client__Requests.py'         ,
                                                                   'users/TestService__Client__Users__CRUD.py']
            assert len(files)                                  >= 3                 # At least main, requests, config
            assert f"{_.client_name}.py"                      in files
            assert f"{_.client_name}__Requests.py"            in files
            assert f"{_.client_name}__Config.py"              in files

            # Check module client files
            assert "users/TestService__Client__Users__CRUD.py" in files            # Module client created

            # Verify file content is Python code
            main_client_code = files[f"{_.client_name}.py"]
            assert "from osbot_utils.type_safe.Type_Safe import Type_Safe" in main_client_code
            assert f"class {_.client_name}(Type_Safe):"                    in main_client_code

    def test__generate_main_client(self):                                          # Test main client class generation
        with self.generator as _:
            code = _._generate_main_client()
            assert code == """\
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from .TestService__Client__Config import TestService__Client__Config
from .TestService__Client__Requests import TestService__Client__Requests
from .users.TestService__Client__Users import TestService__Client__Users

class TestService__Client(Type_Safe):
    config   : TestService__Client__Config
    _requests: TestService__Client__Requests = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)                                                 # Initialize request handler with config
        if not self._requests:
            self._requests = TestService__Client__Requests(config=self.config)

    @cache_on_self
    def requests(self) -> TestService__Client__Requests:                            # Access the unified request handler
        return self._requests

    @cache_on_self
    def users(self) -> TestService__Client__Users:                               # Access users operations
        return TestService__Client__Users(_client=self)"""

            assert type(code) is str
            assert "from osbot_utils.type_safe.Type_Safe import Type_Safe"                  in code
            assert "from osbot_utils.decorators.methods.cache_on_self import cache_on_self" in code
            assert f"class {_.client_name}(Type_Safe):"                                     in code
            assert "config   : TestService__Client__Config"                                 in code
            assert "_requests: TestService__Client__Requests = None"                        in code

            # Check module accessor methods
            assert "@cache_on_self" in code
            assert "def users(self) -> " in code                                   # Module accessor

    def test__generate_module_accessor_method(self):                               # Test module accessor method generation
        with self.generator as _:
            code = _._generate_module_accessor_method("users")
            assert code == """
    @cache_on_self
    def users(self) -> TestService__Client__Users:                               # Access users operations
        return TestService__Client__Users(_client=self)"""

            assert "@cache_on_self" in code
            assert "def users(self) -> TestService__Client__Users:" in code
            assert "return TestService__Client__Users(_client=self)" in code
            assert "# Access users operations" in code

    def test__generate_request_handler(self):                                      # Test request handler generation
        with self.generator as _:
            code = _._generate_request_handler()

            assert code == AUTO_GEN__CODE__GENERATE_REQUEST_HANDLER

            assert "class Enum__Fast_API__Service__Registry__Client__Mode(str, Enum):" in code
            assert "REMOTE       = \"remote\""            in code
            assert "IN_MEMORY    = \"in_memory\""         in code
            assert "LOCAL_SERVER = \"local_server\""      in code

            assert f"class {_.client_name}__Requests__Result(Type_Safe):" in code
            assert "status_code : int"                                    in code
            assert "json        : Optional[Dict] = None"                  in code

            assert f"class {_.client_name}__Requests(Type_Safe):"   in code
            assert "def execute(self,"                              in code
            assert "def _setup_mode(self):"                         in code
            assert "def _execute_remote(self,"                      in code
            assert "def _execute_in_memory(self,"                   in code
            assert "def _execute_local_server(self,"                in code

    def test__generate_config_class(self):                                         # Test config class generation
        with self.generator as _:
            code = _._generate_config_class()
            assert code == """\
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from typing import Optional

class TestService__Client__Config(Type_Safe):
    base_url        : Safe_Str__Url = "http://localhost:8000"                      # Default to local
    api_key         : Optional[str] = None                                         # Optional API key
    api_key_header  : str           = "X-API-Key"                                  # Header name for API key
    timeout         : int           = 30                                           # Request timeout in seconds
    verify_ssl      : bool          = True                                         # Verify SSL certificates
                                                                                    # Service-specific configuration can be added here
    service_name    : Safe_Str__Id  = "TestService"
    service_version : str           = "v1.0.0\""""

            assert f"class {_.client_name}__Config(Type_Safe):"                          in code
            assert "base_url        : Safe_Str__Url = \"http://localhost:8000\""         in code
            assert "api_key         : Optional[str] = None"                              in code
            assert "timeout         : int           = 30"                                in code
            assert f"service_name    : Safe_Str__Id  = \"{_.contract.service_name}\""    in code
            assert f"service_version : str           = \"{_.contract.service_version}\"" in code

    def test__generate_module_client_files(self):                                  # Test module client file generation
        with self.generator as _:
            module = _.contract.modules[0]                                          # Get first module
            files = _._generate_module_client_files(module)

            assert type(files)     is dict
            assert len(files)      >= 1                                                 # At least one client file
            assert list_set(files) == ['users/TestService__Client__Users__CRUD.py']
            for file_path, content in files.items():                                    # Check file paths and content
                assert module.module_name in file_path                                  # Module name in path
                assert "class TestService__Client__" in content                         # Client class generated
                assert "from osbot_utils.type_safe.Type_Safe import Type_Safe" in content

    def test__generate_route_client_class(self):                                   # Test route client class generation
        with self.generator as _:
            class_name  = "TestService__Client__Users"
            endpoints   = _.contract.modules[0].endpoints
            module_name = "users"

            code = _._generate_route_client_class(class_name, endpoints, module_name)

            assert code =="""\
from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe
from ..schemas import Schema__User

class TestService__Client__Users(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def get_user__user_id(self, user_id: int) -> Schema__User:                              # Auto-generated from endpoint get_user
                                                                                    # Build path
        path = f"/users/{{user_id}}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return typed response
            if result.json:
                return Schema__User.from_json(result.json)
            else:
                return Schema__User()

    def create_user(self, request: Schema__User) -> Schema__User:                              # Auto-generated from endpoint create_user
                                                                                    # Build path
        path = "/users"
        body = request.json() if hasattr(request, 'json') else request
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return typed response
            if result.json:
                return Schema__User.from_json(result.json)
            else:
                return Schema__User()"""

            assert f"class {class_name}(Type_Safe):" in code
            assert "_client: Any"                    in code                                          # Reference to main client
            assert "@property"                       in code
            assert "def requests(self):"             in code
            assert "return self._client.requests()"  in code

            # Check endpoint methods generated
            for endpoint in endpoints:
                assert f"def {endpoint.route_method}(self" in code

    def test__generate_endpoint_method(self):                                      # Test endpoint method generation
        with self.generator as _:
            endpoint = Schema__Endpoint__Contract(operation_id    = 'get_user',
                                                  path_pattern    = '/users/{user_id}',
                                                  method          = Enum__Http__Method.GET,
                                                  route_method    = 'get_user',
                                                  path_params     = [Schema__Endpoint__Param(name='user_id', param_type=int, location=Enum__Param__Location.PATH)],
                                                  response_schema = Schema__User)

            code = _._generate_endpoint_method(endpoint)
            assert code == """
    def get_user(self, user_id: int) -> Schema__User:                              # Auto-generated from endpoint get_user
                                                                                    # Build path
        path = f"/users/{{user_id}}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return typed response
            if result.json:
                return Schema__User.from_json(result.json)
            else:
                return Schema__User()"""

            assert "def get_user(self, user_id: int) -> Schema__User:"  in code
            assert "# Auto-generated from endpoint get_user"            in code
            assert "# Build path"                                       in code
            assert 'path = f"/users/{{user_id}}"'                       in code
            assert "# Execute request"                                  in code
            assert 'method = "GET"'                                     in code
            assert "# Return typed response"                            in code
            assert "return Schema__User.from_json(result.json)"         in code

    def test__build_method_params(self):                                           # Test method parameter building
        with self.generator as _:
            endpoint = Schema__Endpoint__Contract(operation_id   = 'test',
                                                  path_pattern   = '/test/{id}',
                                                  method         = Enum__Http__Method.GET,
                                                  path_params    = [Schema__Endpoint__Param(name='id'    , param_type=int,                              location=Enum__Param__Location.PATH)],
                                                  query_params   = [Schema__Endpoint__Param(name='limit' , param_type=int, required=True ,              location=Enum__Param__Location.QUERY),
                                                                    Schema__Endpoint__Param(name='offset', param_type=int, required=False, default='0', location=Enum__Param__Location.QUERY)],
                                                  request_schema = Schema__User)

            params = _._build_method_params(endpoint)
            assert type(params) == str
            assert params == ', id: int, limit: int, offset: Optional[int] = 0, request: Schema__User'
            assert ", id: int"                    in params                         # Path param
            assert ", limit: int"                 in params                         # Required query param
            assert ", offset: Optional[int] = 0"  in params                         # Optional with default
            assert ", request: Schema__User"      in params                         # Request body

    def test__build_path_construction(self):                                       # Test path construction code generation
        with self.generator as _:
            # Test with parameters
            endpoint_with_params = Schema__Endpoint__Contract(operation_id = 'test',
                                                              path_pattern = '/users/{user_id}/posts/{post_id}',
                                                              method       = Enum__Http__Method.GET,
                                                              path_params  = [Schema__Endpoint__Param(name='user_id', location=Enum__Param__Location.PATH),
                                                                              Schema__Endpoint__Param(name='post_id', location=Enum__Param__Location.PATH)])

            code = _._build_path_construction(endpoint_with_params)

            assert code == '\n        path = f"/users/{{user_id}}/posts/{{post_id}}"'


            assert 'path = f"/users/{{user_id}}/posts/{{post_id}}"' in code

            # Test static path
            endpoint_static = Schema__Endpoint__Contract(operation_id = 'test'                ,
                                                         path_pattern = '/users'              ,
                                                         method       = Enum__Http__Method.GET)

            code = _._build_path_construction(endpoint_static)
            assert code == '\n        path = "/users"'
            assert 'path = "/users"' in code

    def test__build_error_handling(self):                                          # Test error handling code generation
        with self.generator as _:
            endpoint = Schema__Endpoint__Contract(operation_id = 'test'                 ,
                                                  path_pattern = '/test'                ,
                                                  method       = Enum__Http__Method.GET ,
                                                  error_codes  = [404, 401, 403, 500]   )

            code = _._build_error_handling(endpoint)
            assert code == """\


                                                                                    # Handle errors
        if result.status_code == 404:
            raise Exception(f"Resource not found: {path}")
        if result.status_code == 401:
            raise Exception("Unauthorized")
        if result.status_code == 403:
            raise Exception("Forbidden")
        if result.status_code >= 500:
            raise Exception(f"Server error: {result.status_code}")"""


            assert "# Handle errors" in code
            assert "if result.status_code == 404:" in code
            assert 'raise Exception(f"Resource not found: {path}")' in code
            assert "if result.status_code == 401:" in code
            assert 'raise Exception("Unauthorized")' in code
            assert "if result.status_code == 403:" in code
            assert "if result.status_code >= 500:" in code

    def test__build_response_handling(self):                                       # Test response handling code generation
        with self.generator as _:
            # With schema
            endpoint_with_schema = Schema__Endpoint__Contract(operation_id    = 'test'                  ,
                                                              path_pattern    = '/test'                 ,
                                                              method          = Enum__Http__Method.GET  ,
                                                              response_schema = Schema__User            )

            code = _._build_response_handling(endpoint_with_schema, 'Schema__User')
            assert code =="""\

                                                                                    # Return typed response
            if result.json:
                return Schema__User.from_json(result.json)
            else:
                return Schema__User()"""

            assert "# Return typed response" in code
            assert "return Schema__User.from_json(result.json)" in code


            # Without schema
            endpoint_no_schema = Schema__Endpoint__Contract(operation_id = 'test',
                                                            path_pattern = '/test',
                                                            method       = Enum__Http__Method.GET)

            code = _._build_response_handling(endpoint_no_schema, 'Schema__User')

            assert code =="""\

                                                                                    # Return response data
        return result.json if result.json else result.text"""

            assert "# Return response data" in code
            assert "return result.json if result.json else result.text" in code

    def test__generate_module_aggregator(self):                                    # Test module aggregator generation
        with self.generator as _:
            module = Schema__Routes__Module(module_name   = "users",
                                            route_classes = ["Routes__Users__CRUD", "Routes__Users__Admin"])

            code = _._generate_module_aggregator(module, module.route_classes)

            assert code == """\
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from .TestService__Client__Users__CRUD import TestService__Client__Users__CRUD
from .TestService__Client__Users__Admin import TestService__Client__Users__Admin

class TestService__Client__Users(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @cache_on_self
    def crud(self) -> TestService__Client__Users__CRUD:                                  # Access crud operations
        return TestService__Client__Users__CRUD(_client=self._client)

    @cache_on_self
    def admin(self) -> TestService__Client__Users__Admin:                                  # Access admin operations
        return TestService__Client__Users__Admin(_client=self._client)

"""


            assert "class TestService__Client__Users(Type_Safe):" in code
            assert "_client: Any" in code                                          # Reference to main client
            assert "@cache_on_self" in code
            assert "def crud(self) -> TestService__Client__Users__CRUD:" in code
            assert "def admin(self) -> TestService__Client__Users__Admin:" in code

    def test__get_module_client_name(self):                                        # Test module client name generation
        with self.generator as _:
            assert _._get_module_client_name("users"   ) == "TestService__Client__Users"
            assert _._get_module_client_name("products") == "TestService__Client__Products"
            assert _._get_module_client_name("admin"   ) == "TestService__Client__Admin"

    def test__get_schema_imports(self):                                            # Test schema import extraction
        with self.generator as _:
            endpoints = [Schema__Endpoint__Contract(operation_id    = 'test1'                   ,
                                                    path_pattern    = '/test1'                  ,
                                                    method          = Enum__Http__Method.GET    ,
                                                    request_schema  = Schema__User              ,
                                                    response_schema = Schema__User              ),
                         Schema__Endpoint__Contract(operation_id    = 'test2'                   ,
                                                    path_pattern    = '/test2'                  ,
                                                    method          = Enum__Http__Method.POST   ,
                                                    request_schema  = Schema__Product           ,                           # Duplicate
                                                    response_schema = Schema__Product           )]

            imports = _._get_schema_imports(endpoints)

            # we can't do this comparison because the order is non-deterministic
#             assert imports == """\
# from ..schemas import Schema__Product
# from ..schemas import Schema__User"""
            assert "from ..schemas import Schema__Product"  in imports
            assert "from ..schemas import Schema__User"     in imports
            # No duplicates
            assert imports.count("Schema__Product") == 1

    def test_generate_client_files__comprehensive(self):                           # Test comprehensive file generation
        with self.generator as _:
            files = _.generate_client_files()

            # Verify all expected files exist
            expected_files = [ f"{_.client_name}.py"                     ,
                               f"{_.client_name}__Requests.py"           ,
                               f"{_.client_name}__Config.py"             ,
                              "users/TestService__Client__Users__CRUD.py"]

            for expected_file in expected_files:
                assert expected_file in files, f"Missing expected file: {expected_file}"


            # Verify main client imports module clients
            main_code = files[f"{_.client_name}.py"]

            assert main_code == """\
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from .TestService__Client__Config import TestService__Client__Config
from .TestService__Client__Requests import TestService__Client__Requests
from .users.TestService__Client__Users import TestService__Client__Users

class TestService__Client(Type_Safe):
    config   : TestService__Client__Config
    _requests: TestService__Client__Requests = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)                                                 # Initialize request handler with config
        if not self._requests:
            self._requests = TestService__Client__Requests(config=self.config)

    @cache_on_self
    def requests(self) -> TestService__Client__Requests:                            # Access the unified request handler
        return self._requests

    @cache_on_self
    def users(self) -> TestService__Client__Users:                               # Access users operations
        return TestService__Client__Users(_client=self)"""


    # Helper methods
    @staticmethod
    def _create_test_contract():                                                   # Create comprehensive test contract
        return Schema__Service__Contract(
            service_name    = 'TestService',
            version         = 'v1.0.0',
            base_path       = '/api',
            service_version = 'v1.0.0',
            modules         = [ Schema__Routes__Module( module_name   = 'users',
                                                        route_classes = ['Routes__Users__CRUD'],
                                                        endpoints     = [Schema__Endpoint__Contract( operation_id    = 'get_user'            ,
                                                                                                     path_pattern    = '/users/{user_id}'    ,
                                                                                                     method          = Enum__Http__Method.GET,
                                                                                                     route_method    = 'get_user__user_id'   ,
                                                                                                     route_class     = 'Routes__Users__CRUD' ,
                                                                                                     route_module    = 'users'               ,
                                                                                                     path_params     = [Schema__Endpoint__Param(name='user_id', param_type=int, location=Enum__Param__Location.PATH)],
                                                                                                     response_schema = Schema__User          ),
                                                                         Schema__Endpoint__Contract( operation_id    = 'create_user'          ,
                                                                                                     path_pattern    = '/users'               ,
                                                                                                     method          = Enum__Http__Method.POST,
                                                                                                     route_method    = 'create_user'          ,
                                                                                                     route_class     = 'Routes__Users__CRUD'  ,
                                                                                                     route_module    = 'users'                ,
                                                                                                     request_schema  = Schema__User           ,
                                                                                                     response_schema = Schema__User           )])],
            endpoints = []                                                          # Will be populated from modules
        )


AUTO_GEN__CODE__GENERATE_REQUEST_HANDLER = """\
from enum import Enum
from typing import Any, Optional, Dict
import requests
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Enum__Fast_API__Service__Registry__Client__Mode(str, Enum):
    REMOTE       = "remote"                                                        # HTTP calls to deployed service
    IN_MEMORY    = "in_memory"                                                     # FastAPI TestClient (same process)
    LOCAL_SERVER = "local_server"                                                  # Fast_API_Server (local HTTP)

class TestService__Client__Requests__Result(Type_Safe):
    status_code : int
    json        : Optional[Dict] = None
    text        : Optional[str]  = None
    content     : bytes          = b""
    headers     : Dict[str, str] = {}
    path        : str            = ""

class TestService__Client__Requests(Type_Safe):
    config       : Any                                                             # TestService__Client__Config
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
                self._session.headers['Authorization'] = f'Bearer {self.config.api_key}'

    def execute(self, method  : str              ,                                 # HTTP method (GET, POST, etc)
                     path     : str              ,                                 # Endpoint path
                     body     : Any        = None,                                 # Request body
                     headers  : Optional[Dict] = None                              # Additional headers
               ) -> TestService__Client__Requests__Result:                          # Execute request transparently based on mode
                                                                                    # Merge headers
        request_headers = {**self.auth_headers(), **(headers or {})}
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
        url         = f"{self._server.url()}{path}"
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
        url         = f"{self.config.base_url}{path}"
        method_func = getattr(self._session, method.lower())
        if body:
            return method_func(url, json=body, headers=headers)
        else:
            return method_func(url, headers=headers)

    def _build_result(self, response ,                                             # Response object
                           path                                                    # Path requested
                    ) -> TestService__Client__Requests__Result:                     # Convert any response type to unified result

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

        return TestService__Client__Requests__Result(
            status_code = response.status_code                                   ,
            json        = json_data                                             ,
            text        = text_data                                             ,
            content     = response.content if hasattr(response, 'content') else b"",
            headers     = dict(response.headers) if hasattr(response, 'headers') else {},
            path        = path
        )

    def auth_headers(self) -> Dict[str, str]:                                      # Get authentication headers from config
        headers = {}
                                                                                    # Add API key if configured
        if hasattr(self.config, 'api_key_header') and hasattr(self.config, 'api_key'):
            if self.config.api_key_header and self.config.api_key:
                headers[self.config.api_key_header] = self.config.api_key

        return headers"""
