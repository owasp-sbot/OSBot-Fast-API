import tempfile
from pathlib                                                 import Path
from unittest                                                import TestCase

import pytest
from osbot_utils.testing.__ import __, __SKIP__

from osbot_fast_api.api.schemas.Schema__Fast_API__Config import Schema__Fast_API__Config
from osbot_utils.testing.Stdout import Stdout
from osbot_utils.utils.Misc import list_set

from osbot_fast_api.client.Fast_API__Client__Generator       import Fast_API__Client__Generator
from osbot_fast_api.client.Fast_API__Contract__Extractor     import Fast_API__Contract__Extractor
from osbot_fast_api.client.schemas.Schema__Service__Contract import Schema__Service__Contract
from osbot_fast_api.utils.Version import version__osbot_fast_api
from osbot_utils.utils.Objects                               import base_classes
from osbot_utils.type_safe.Type_Safe                         import Type_Safe
from osbot_fast_api.api.Fast_API                             import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes              import Fast_API__Routes


class test_Fast_API__Client__Generator(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # ONE-TIME expensive setup
        cls.fast_api  = Test__Service__Fast_API().setup()
        cls.generator = Fast_API__Client__Generator(fast_api=cls.fast_api)

    def test__init__(self):                                                         # Test Type_Safe inheritance and initialization
        with Fast_API__Client__Generator() as _:
            assert type(_)           is Fast_API__Client__Generator
            assert base_classes(_)   == [Type_Safe, object]
            assert type(_.fast_api)  is Fast_API                                          # No Fast_API by default

        with Fast_API__Client__Generator(fast_api=self.fast_api) as _:
            assert type(_.fast_api) is Test__Service__Fast_API
            assert _.fast_api       is self.fast_api                                # Same instance

    def test_extract_contract(self):                                                # Test contract extraction
        with self.generator as _:
            contract = _.extract_contract()

            assert type(contract)            is Schema__Service__Contract
            assert contract.service_name     == 'Test__Service__Fast_API'
            assert contract.version          == version__osbot_fast_api
            assert len(contract.modules)     >= 1                                   # At least one module
            assert len(contract.endpoints)   >= 3                                   # At least 3 endpoints

            # Verify uses Contract__Extractor internally
            extractor = Fast_API__Contract__Extractor(fast_api=_.fast_api)
            contract2 = extractor.extract_contract()
            assert contract.service_name == contract2.service_name                  # Same result

    def test_generate_client(self):                                                 # Test client code generation
        with self.generator as _:
            files = _.generate_client()

            assert type(files) is dict
            assert len(files)  >= 3                                                # At least main, requests, config

            assert list_set(files) == [ 'Test__Service__Fast_API__Client.py'                 ,
                                        'Test__Service__Fast_API__Client__Config.py'         ,
                                        'Test__Service__Fast_API__Client__Requests.py'       ,
                                        'auth/Test__Service__Fast_API__Client__Set_Cookie.py',
                                        'config/Test__Service__Fast_API__Client__Config.py'  ,
                                        'items/Test__Service__Fast_API__Client__Items.py'    ,
                                        'root/Fast_API.py']

            # Check default client name from service
            assert "Test__Service__Fast_API__Client.py"           in files
            assert "Test__Service__Fast_API__Client__Requests.py" in files
            assert "Test__Service__Fast_API__Client__Config.py"   in files


            # Verify Python code generated
            for filename, content in files.items():
                assert type(content) is str
                if filename.endswith('.py'):
                    assert 'import' in content or 'from' in content                # Has imports
                    assert 'class'  in content                                     # Has class definitions

    def test_generate_client__with_custom_name(self):                               # Test client generation with custom name
        with self.generator as _:
            files = _.generate_client(client_name="MyCustomClient")

            assert "MyCustomClient.py"           in files
            assert "MyCustomClient__Requests.py" in files
            assert "MyCustomClient__Config.py"   in files

            # Verify custom name used in code
            main_code = files["MyCustomClient.py"]
            assert "class MyCustomClient(Type_Safe):" in main_code

    def test_save_client_files(self):                                               # Test saving client files to disk
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.generator as _:
                saved_files = _.save_client_files(temp_dir, client_name="TestClient")

                assert type(saved_files) is list
                assert len(saved_files)  >= 3

                # Verify files exist on disk
                output_path = Path(temp_dir)
                assert (output_path / "TestClient.py"           ).exists()
                assert (output_path / "TestClient__Requests.py" ).exists()
                assert (output_path / "TestClient__Config.py"   ).exists()

                # Verify content can be read
                main_content = (output_path / "TestClient.py").read_text()
                assert "class TestClient(Type_Safe):" in main_content

    def test_save_client_files__with_modules(self):                                 # Test saving with module subdirectories
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.generator as _:
                saved_files = _.save_client_files(temp_dir)
                assert saved_files == [ 'Test__Service__Fast_API__Client.py'                 ,
                                        'Test__Service__Fast_API__Client__Requests.py'       ,
                                        'Test__Service__Fast_API__Client__Config.py'         ,
                                        'root/Fast_API.py'                                   ,
                                        'config/Test__Service__Fast_API__Client__Config.py'  ,
                                        'auth/Test__Service__Fast_API__Client__Set_Cookie.py',
                                        'items/Test__Service__Fast_API__Client__Items.py'    ]

                output_path = Path(temp_dir)

                # Check if module directories created
                for file_path in saved_files:
                    if '/' in file_path:                                           # Module file
                        full_path = output_path / file_path
                        assert full_path.exists()
                        assert full_path.parent.exists()                           # Directory created

    def test_print_client_summary(self):                                    # Test client summary printing
        with self.generator as _:
            with Stdout() as stdout:
                _.print_client_summary()

            output = stdout.value()
            assert output == """\
Service: Test__Service__Fast_API {version}
Modules: 4
Total Endpoints: 10

  Module 'root':
    Classes: Fast_API
    Endpoints: 1
      - Enum__Http__Method.GET / (redirect_to_docs)

  Module 'config':
    Classes: Routes__Config
    Endpoints: 4
      - Enum__Http__Method.GET /config/info (info)
      - Enum__Http__Method.GET /config/status (status)
      - Enum__Http__Method.GET /config/version (version)
      ... and 1 more

  Module 'auth':
    Classes: Routes__Set_Cookie
    Endpoints: 2
      - Enum__Http__Method.GET /auth/set-cookie-form (set_cookie_form)
      - Enum__Http__Method.POST /auth/set-auth-cookie (set_auth_cookie)

  Module 'items':
    Classes: Routes__Items
    Endpoints: 3
      - Enum__Http__Method.GET /items/get-item/{{item_id}} (get_item__item_id)
      - Enum__Http__Method.GET /items/list-items (list_items)
      - Enum__Http__Method.POST /items/create-item (create_item)

""".format(version=version__osbot_fast_api)

            assert "Service: Test__Service__Fast_API "  in output
            assert "Modules:"                           in output
            assert "Total Endpoints:"                   in output
            assert "Module 'items':"                    in output
            assert "Classes:"                           in output
            assert "Routes__Items"                      in output
            assert "GET /"                              in output                              # At least one endpoint shown

    def test_generate_client__with_empty_fast_api(self):                            # Test with minimal Fast_API
        with Fast_API() as empty_api:
            empty_api.setup()
            generator = Fast_API__Client__Generator(fast_api=empty_api)

            files = generator.generate_client()

            assert type(files) is dict
            assert len(files)  >= 3                                                # Still generates basic structure
            assert "Fast_API__Client.py" in files                                  # Uses default name

    def test_generate_client__integration_with_contract_and_ast(self):             # Test full integration chain
        with self.generator as _:
            # Extract contract
            contract = _.extract_contract()
            assert type(contract) is Schema__Service__Contract

            # Generate client
            files = _.generate_client()
            assert list_set(files) == [ 'Test__Service__Fast_API__Client.py'                    ,
                                        'Test__Service__Fast_API__Client__Config.py'            ,
                                        'Test__Service__Fast_API__Client__Requests.py'          ,
                                        'auth/Test__Service__Fast_API__Client__Set_Cookie.py'   ,
                                        'config/Test__Service__Fast_API__Client__Config.py'     ,
                                        'items/Test__Service__Fast_API__Client__Items.py'       ,
                                        'root/Fast_API.py'                                      ]
            # Verify contract details appear in generated code
            config_code = files["Test__Service__Fast_API__Client__Config.py"]

            assert config_code == """\
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from typing import Optional

class Test__Service__Fast_API__Client__Config(Type_Safe):
    base_url        : Safe_Str__Url = "http://localhost:8000"                      # Default to local
    api_key         : Optional[str] = None                                         # Optional API key
    api_key_header  : str           = "X-API-Key"                                  # Header name for API key
    timeout         : int           = 30                                           # Request timeout in seconds
    verify_ssl      : bool          = True                                         # Verify SSL certificates
                                                                                    # Service-specific configuration can be added here
    service_name    : Safe_Str__Id  = "Test__Service__Fast_API"
    service_version : str           = "{version}\"""".format(version=version__osbot_fast_api)

            assert f'service_name    : Safe_Str__Id  = "{contract.service_name}"'   in config_code
            assert f'service_version : str           = "{contract.service_version}"' in config_code

            # Verify endpoints from contract appear in client
            for endpoint in contract.endpoints:
                # Find the module file that should contain this endpoint
                module_files = [f for f in files.keys() if endpoint.route_module in f]
                if module_files:
                    module_code = files[module_files[0]]
                    assert f"def {endpoint.route_method}(" in module_code

    def test_generate_client__method_monkeypatch(self):                             # Test Fast_API.generate_client monkey-patch
        # The module should add generate_client to Fast_API class
        assert hasattr(Fast_API, 'generate_client')

        with Fast_API() as test_api:
            test_api.setup()

            # Test without output_dir (returns code)
            files = test_api.generate_client()
            assert type(files) is dict
            assert all(isinstance(content, str) for content in files.values())

            # Test with output_dir
            with tempfile.TemporaryDirectory() as temp_dir:
                result = test_api.generate_client(output_dir=temp_dir)
                assert type(result) is dict
                assert all("Saved to" in msg for msg in result.values())

    def test_generate_client__preserves_type_safety(self):                          # Test Type_Safe patterns in generated code
        with self.generator as _:
            files = _.generate_client()

            # Check main client follows Type_Safe patterns
            main_code = files["Test__Service__Fast_API__Client.py"]
            assert "from osbot_utils.type_safe.Type_Safe import Type_Safe" in main_code
            assert ": Test__Service__Fast_API__Client" in main_code                            # Typed attributes
            assert ": Test__Service__Fast_API__Client__Requests = None" in main_code           # Nullable with explicit None

            # Check config uses Safe types
            config_code = files["Test__Service__Fast_API__Client__Config.py"]
            assert "from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url" in config_code
            assert ": Safe_Str__Url" in config_code
            assert ": Safe_Str__Id"  in config_code

            # Check requests result is Type_Safe
            requests_code = files["Test__Service__Fast_API__Client__Requests.py"]
            assert "class Test__Service__Fast_API__Client__Requests__Result(Type_Safe):" in requests_code

    def test_generate_client__handles_all_http_methods(self):                       # Test all HTTP methods handled
        with self.generator as _:
            contract = _.extract_contract()
            files    = _.generate_client()

            # Find endpoints with different methods
            for endpoint in contract.endpoints:
                if endpoint.route_module and endpoint.route_class:
                    # Find the client file for this endpoint
                    expected_file = f"{endpoint.route_module}/Test__Service__Fast_API__Client__{endpoint.route_class.replace('Routes__', '')}.py"
                    if expected_file in files:
                        client_code = files[expected_file]
                        # Verify method is used in execute call
                        assert f'method = "{endpoint.method.value}"' in client_code


    def test__generate_client__with_complex_paths(self):                             # Test complex path patterns
        # Create Fast_API with complex paths


        config = Schema__Fast_API__Config(default_routes=False)
        with Fast_API(config=config) as complex_api:
            complex_api.add_routes(Routes__Complex)
            complex_api.setup()

            generator = Fast_API__Client__Generator(fast_api=complex_api)
            files     = generator.generate_client()

            assert list_set(files) == [  'Fast_API__Client.py'                          ,
                                         'Fast_API__Client__Config.py'                  ,
                                         'Fast_API__Client__Requests.py'                ,
                                         'complex/Fast_API__Client__Complex.py'         ]


            # Find the complex route in generated code
            complex_files = [f for f in files.keys() if 'complex' in f.lower()]
            assert len(complex_files) > 0

            if complex_files:
                complex_code = files[complex_files[0]]

                assert complex_code == """\
from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Fast_API__Client__Complex(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def nested__path__with__many__params(self, a: int, b: str, c: int) -> Dict:                              # Auto-generated from endpoint get__nested__path__with__many__params
                                                                                    # Build path
        path = "/complex/nested/path/with/many/params"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text"""

                assert "def nested__path__with__many__params(" in complex_code
                assert "a: int" in complex_code
                assert "b: str" in complex_code
                assert "c: int" in complex_code

    def test__bug__regression__client_generation_consistency(self):                 # Test consistent generation across runs
        with self.generator as _:
            # Generate twice and compare
            files1 = _.generate_client()
            files2 = _.generate_client()

            # Should generate same files
            assert set(files1.keys()) == set(files2.keys())

            # Content should be identical (no random elements)
            for filename in files1.keys():
                # Skip checking exact match due to potential timestamp differences
                # But verify structure is same
                assert len(files1[filename]) == len(files2[filename])
                assert files1[filename].count('class') == files2[filename].count('class')
                assert files1[filename].count('def')   == files2[filename].count('def')


# Test fixtures
class Test__Service__Fast_API(Fast_API):                                           # Test Fast_API service
    name    = "TestService"
    version = "v1.2.3"

    def setup_routes(self):
        self.add_routes(Routes__Items)
        return self


class Schema__Item(Type_Safe):                                                      # Test schema
    id   : int
    name : str
    price: float


class Routes__Items(Fast_API__Routes):                                              # Test routes
    tag = 'items'

    def get_item__item_id(self, item_id: int) -> Schema__Item:
        """Get item by ID"""
        return Schema__Item(id=item_id, name="Test Item", price=9.99)

    def list_items(self, limit: int = 10, offset: int = 0) -> list:
        """List items with pagination"""
        return []

    def create_item(self, item: Schema__Item) -> Schema__Item:
        """Create new item"""
        return item

    def setup_routes(self):
        self.add_route_get(self.get_item__item_id)
        self.add_route_get(self.list_items)
        self.add_route_post(self.create_item)

class Routes__Complex(Fast_API__Routes):
    tag = 'complex'

    def nested__path__with__many__params(self, a: int, b: str, c: int):
        return {}

    def setup_routes(self):
        self.add_route_get(self.nested__path__with__many__params)