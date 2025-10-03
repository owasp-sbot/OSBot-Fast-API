# import pytest
# from unittest                                                                        import TestCase
# from pathlib                                                                         import Path
# from osbot_utils.testing.__                                                          import __, __SKIP__
# from osbot_utils.utils.Objects                                                       import base_classes
# from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
# from osbot_fast_api.api.contracts.Client__Generator__AST                            import Client__Generator__AST
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Schema__Service__Contract
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Schema__Routes__Module
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Schema__Endpoint__Contract
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Schema__Endpoint__Param
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Enum__Http__Method
# from osbot_fast_api.api.contracts.Schema__Service__Contract                         import Enum__Param__Location
#
#
# class test_Client__Generator__AST(TestCase):
#
#     @classmethod
#     def setUpClass(cls):                                                            # ONE-TIME expensive setup
#         cls.test_contract = cls._create_test_contract()
#         cls.generator = Client__Generator__AST(contract    = cls.test_contract,
#                                               client_name = "TestService__Client")
#
#     def test__init__(self):                                                         # Test initialization and Type_Safe inheritance
#         with Client__Generator__AST(contract=self.test_contract) as _:
#             assert type(_)           is Client__Generator__AST
#             assert base_classes(_)   == [Type_Safe, object]
#             assert type(_.contract)  is Schema__Service__Contract
#             assert _.contract        is self.test_contract
#             assert _.client_name     == 'TestService__Client'                       # Auto-generated from service name
#
#         # Test with custom client name
#         with Client__Generator__AST(contract=self.test_contract, client_name="CustomClient") as _:
#             assert _.client_name == "CustomClient"
#
#     def test_generate_client_files(self):                                          # Test complete client file generation
#         with self.generator as _:
#             files = _.generate_client_files()
#
#             assert type(files)                                 is dict
#             assert len(files)                                  >= 3                 # At least main, requests, config
#             assert f"{_.client_name}.py"                      in files
#             assert f"{_.client_name}__Requests.py"            in files
#             assert f"{_.client_name}__Config.py"              in files
#
#             # Check module client files
#             assert "users/TestService__Client__Users__CRUD.py" in files            # Module client created
#
#             # Verify file content is Python code
#             main_client_code = files[f"{_.client_name}.py"]
#             assert "from osbot_utils.type_safe.Type_Safe import Type_Safe" in main_client_code
#             assert f"class {_.client_name}(Type_Safe):"                    in main_client_code
#
#     def test__generate_main_client(self):                                          # Test main client class generation
#         with self.generator as _:
#             code = _._generate_main_client()
#
#             assert type(code) is str
#             assert "from osbot_utils.type_safe.Type_Safe import Type_Safe" in code
#             assert "from osbot_utils.decorators.methods.cache_on_self import cache_on_self" in code
#             assert f"class {_.client_name}(Type_Safe):" in code
#             assert "config   : TestService__Client__Config" in code
#             assert "_requests: TestService__Client__Requests = None" in code
#
#             # Check module accessor methods
#             assert "@cache_on_self" in code
#             assert "def users(self) -> " in code                                   # Module accessor
#
#     def test__generate_module_accessor_method(self):                               # Test module accessor method generation
#         with self.generator as _:
#             code = _._generate_module_accessor_method("users")
#
#             assert "@cache_on_self" in code
#             assert "def users(self) -> TestService__Client__Users:" in code
#             assert "return TestService__Client__Users(_client=self)" in code
#             assert "# Access users operations" in code
#
#     def test__generate_request_handler(self):                                      # Test request handler generation
#         with self.generator as _:
#             code = _._generate_request_handler()
#
#             assert "class Enum__Client__Mode(str, Enum):" in code
#             assert "REMOTE       = \"remote\""            in code
#             assert "IN_MEMORY    = \"in_memory\""         in code
#             assert "LOCAL_SERVER = \"local_server\""      in code
#
#             assert f"class {_.client_name}__Requests__Result(Type_Safe):" in code
#             assert "status_code : int"                                    in code
#             assert "json        : Optional[Dict] = None"                  in code
#
#             assert f"class {_.client_name}__Requests(Type_Safe):" in code
#             assert "def execute(self," in code
#             assert "def _setup_mode(self):" in code
#             assert "def _execute_remote(self," in code
#             assert "def _execute_in_memory(self," in code
#             assert "def _execute_local_server(self," in code
#
#     def test__generate_config_class(self):                                         # Test config class generation
#         with self.generator as _:
#             code = _._generate_config_class()
#
#             assert f"class {_.client_name}__Config(Type_Safe):" in code
#             assert "base_url        : Safe_Str__Url = \"http://localhost:8000\"" in code
#             assert "api_key         : Optional[str]  = None"                     in code
#             assert "timeout         : int            = 30"                       in code
#             assert f"service_name    : Safe_Str__Id = \"{_.contract.service_name}\"" in code
#             assert f"service_version : str          = \"{_.contract.service_version}\"" in code
#
#     def test__generate_module_client_files(self):                                  # Test module client file generation
#         with self.generator as _:
#             module = _.contract.modules[0]                                          # Get first module
#             files = _._generate_module_client_files(module)
#
#             assert type(files) is dict
#             assert len(files)  >= 1                                                # At least one client file
#
#             # Check file paths and content
#             for file_path, content in files.items():
#                 assert module.module_name in file_path                             # Module name in path
#                 assert "class TestService__Client__" in content                    # Client class generated
#                 assert "from osbot_utils.type_safe.Type_Safe import Type_Safe" in content
#
#     def test__generate_route_client_class(self):                                   # Test route client class generation
#         with self.generator as _:
#             class_name = "TestService__Client__Users"
#             endpoints  = _.contract.modules[0].endpoints
#             module_name = "users"
#
#             code = _._generate_route_client_class(class_name, endpoints, module_name)
#
#             assert f"class {class_name}(Type_Safe):" in code
#             assert "_client: Any" in code                                          # Reference to main client
#             assert "@property" in code
#             assert "def requests(self):" in code
#             assert "return self._client.requests()" in code
#
#             # Check endpoint methods generated
#             for endpoint in endpoints:
#                 assert f"def {endpoint.route_method}(self" in code
#
#     def test__generate_endpoint_method(self):                                      # Test endpoint method generation
#         with self.generator as _:
#             endpoint = Schema__Endpoint__Contract(
#                 operation_id    = 'get_user',
#                 path_pattern    = '/users/{user_id}',
#                 method          = Enum__Http__Method.GET,
#                 route_method    = 'get_user',
#                 path_params     = [Schema__Endpoint__Param(name='user_id', param_type='int', location=Enum__Param__Location.PATH)],
#                 response_schema = 'Schema__User'
#             )
#
#             code = _._generate_endpoint_method(endpoint)
#
#             assert "def get_user(self, user_id: int) -> Schema__User:" in code
#             assert "# Auto-generated from endpoint get_user" in code
#             assert "# Build path" in code
#             assert 'path = f"/users/{user_id}"' in code
#             assert "# Execute request" in code
#             assert 'method = "GET"' in code
#             assert "# Return typed response" in code
#             assert "return Schema__User.from_json(result.json)" in code
#
#     def test__build_method_params(self):                                           # Test method parameter building
#         with self.generator as _:
#             endpoint = Schema__Endpoint__Contract(
#                 operation_id   = 'test',
#                 path_pattern   = '/test/{id}',
#                 method         = Enum__Http__Method.GET,
#                 path_params    = [Schema__Endpoint__Param(name='id', param_type='int', location=Enum__Param__Location.PATH)],
#                 query_params   = [Schema__Endpoint__Param(name='limit', param_type='int', required=True, location=Enum__Param__Location.QUERY),
#                                   Schema__Endpoint__Param(name='offset', param_type='int', required=False, default='0', location=Enum__Param__Location.QUERY)],
#                 request_schema = 'Schema__TestRequest'
#             )
#
#             params = _._build_method_params(endpoint)
#
#             assert ", id: int" in params                                           # Path param
#             assert ", limit: int" in params                                        # Required query param
#             assert ", offset: Optional[int] = 0" in params                         # Optional with default
#             assert ", request: Schema__TestRequest" in params                      # Request body
#
#     def test__build_path_construction(self):                                       # Test path construction code generation
#         with self.generator as _:
#             # Test with parameters
#             endpoint_with_params = Schema__Endpoint__Contract(
#                 operation_id = 'test',
#                 path_pattern = '/users/{user_id}/posts/{post_id}',
#                 method       = Enum__Http__Method.GET,
#                 path_params  = [Schema__Endpoint__Param(name='user_id', location=Enum__Param__Location.PATH),
#                                Schema__Endpoint__Param(name='post_id', location=Enum__Param__Location.PATH)]
#             )
#
#             code = _._build_path_construction(endpoint_with_params)
#             assert 'path = f"/users/{user_id}/posts/{post_id}"' in code
#
#             # Test static path
#             endpoint_static = Schema__Endpoint__Contract(
#                 operation_id = 'test',
#                 path_pattern = '/users',
#                 method       = Enum__Http__Method.GET
#             )
#
#             code = _._build_path_construction(endpoint_static)
#             assert 'path = "/users"' in code
#
#     def test__build_error_handling(self):                                          # Test error handling code generation
#         with self.generator as _:
#             endpoint = Schema__Endpoint__Contract(
#                 operation_id = 'test',
#                 path_pattern = '/test',
#                 method       = Enum__Http__Method.GET,
#                 error_codes  = [404, 401, 403, 500]
#             )
#
#             code = _._build_error_handling(endpoint)
#
#             assert "# Handle errors" in code
#             assert "if result.status_code == 404:" in code
#             assert 'raise Exception(f"Resource not found: {path}")' in code
#             assert "if result.status_code == 401:" in code
#             assert 'raise Exception("Unauthorized")' in code
#             assert "if result.status_code == 403:" in code
#             assert "if result.status_code >= 500:" in code
#
#     def test__build_response_handling(self):                                       # Test response handling code generation
#         with self.generator as _:
#             # With schema
#             endpoint_with_schema = Schema__Endpoint__Contract(
#                 operation_id    = 'test',
#                 path_pattern    = '/test',
#                 method          = Enum__Http__Method.GET,
#                 response_schema = 'Schema__Response'
#             )
#
#             code = _._build_response_handling(endpoint_with_schema)
#             assert "# Return typed response" in code
#             assert "return Schema__Response.from_json(result.json)" in code
#
#             # Without schema
#             endpoint_no_schema = Schema__Endpoint__Contract(
#                 operation_id = 'test',
#                 path_pattern = '/test',
#                 method       = Enum__Http__Method.GET
#             )
#
#             code = _._build_response_handling(endpoint_no_schema)
#             assert "# Return response data" in code
#             assert "return result.json if result.json else result.text" in code
#
#     def test__generate_module_aggregator(self):                                    # Test module aggregator generation
#         with self.generator as _:
#             module = Schema__Routes__Module(
#                 module_name   = "users",
#                 route_classes = ["Routes__Users__CRUD", "Routes__Users__Admin"]
#             )
#
#             code = _._generate_module_aggregator(module, module.route_classes)
#
#             assert "class TestService__Client__Users(Type_Safe):" in code
#             assert "_client: Any" in code                                          # Reference to main client
#             assert "@cache_on_self" in code
#             assert "def crud(self) -> TestService__Client__Users__CRUD:" in code
#             assert "def admin(self) -> TestService__Client__Users__Admin:" in code
#
#     def test__get_module_client_name(self):                                        # Test module client name generation
#         with self.generator as _:
#             assert _._get_module_client_name("users")    == "TestService__Client__Users"
#             assert _._get_module_client_name("products") == "TestService__Client__Products"
#             assert _._get_module_client_name("admin")    == "TestService__Client__Admin"
#
#     def test__get_schema_imports(self):                                            # Test schema import extraction
#         with self.generator as _:
#             endpoints = [
#                 Schema__Endpoint__Contract(
#                     operation_id    = 'test1',
#                     path_pattern    = '/test1',
#                     method          = Enum__Http__Method.GET,
#                     request_schema  = 'Schema__Request',
#                     response_schema = 'Schema__Response'
#                 ),
#                 Schema__Endpoint__Contract(
#                     operation_id    = 'test2',
#                     path_pattern    = '/test2',
#                     method          = Enum__Http__Method.POST,
#                     request_schema  = 'Schema__Request',                           # Duplicate
#                     response_schema = 'Schema__Other'
#                 )
#             ]
#
#             imports = _._get_schema_imports(endpoints)
#
#             assert type(imports) is str
#             # Should have comments for missing imports
#             assert "# from ..schemas import Schema__Request" in imports
#             assert "# from ..schemas import Schema__Response" in imports
#             assert "# from ..schemas import Schema__Other" in imports
#             # No duplicates
#             assert imports.count("Schema__Request") == 1
#
#     def test_generate_client_files__comprehensive(self):                           # Test comprehensive file generation
#         with self.generator as _:
#             files = _.generate_client_files()
#
#             # Verify all expected files exist
#             expected_files = [
#                 f"{_.client_name}.py",
#                 f"{_.client_name}__Requests.py",
#                 f"{_.client_name}__Config.py",
#                 "users/TestService__Client__Users__CRUD.py"
#             ]
#
#             for expected_file in expected_files:
#                 assert expected_file in files, f"Missing expected file: {expected_file}"
#
#             # Verify main client imports module clients
#             main_code = files[f"{_.client_name}.py"]
#             assert "from .users.TestService__Client__Users__CRUD import TestService__Client__Users__CRUD" in main_code
#
#             # Verify request handler has all modes
#             request_code = files[f"{_.client_name}__Requests.py"]
#             assert "Enum__Client__Mode.REMOTE" in request_code
#             assert "Enum__Client__Mode.IN_MEMORY" in request_code
#             assert "Enum__Client__Mode.LOCAL_SERVER" in request_code
#
#     # Helper methods
#     @staticmethod
#     def _create_test_contract():                                                   # Create comprehensive test contract
#         return Schema__Service__Contract(
#             service_name    = 'TestService',
#             version         = '1.0.0',
#             base_path       = '/api',
#             service_version = '1.0.0',
#             modules         = [
#                 Schema__Routes__Module(
#                     module_name   = 'users',
#                     route_classes = ['Routes__Users__CRUD'],
#                     endpoints     = [
#                         Schema__Endpoint__Contract(
#                             operation_id    = 'get_user',
#                             path_pattern    = '/users/{user_id}',
#                             method          = Enum__Http__Method.GET,
#                             route_method    = 'get_user__user_id',
#                             route_class     = 'Routes__Users__CRUD',
#                             route_module    = 'users',
#                             path_params     = [Schema__Endpoint__Param(name='user_id', param_type='int', location=Enum__Param__Location.PATH)],
#                             response_schema = 'Schema__User'
#                         ),
#                         Schema__Endpoint__Contract(
#                             operation_id   = 'create_user',
#                             path_pattern   = '/users',
#                             method         = Enum__Http__Method.POST,
#                             route_method   = 'create_user',
#                             route_class    = 'Routes__Users__CRUD',
#                             route_module   = 'users',
#                             request_schema = 'Schema__User__Create',
#                             response_schema = 'Schema__User'
#                         )
#                     ]
#                 )
#             ],
#             endpoints = []                                                          # Will be populated from modules
#         )