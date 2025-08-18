import json
import re
import sys
from tomllib import TOMLDecodeError
from typing import List, Dict, Optional, Any
from unittest                                                 import TestCase

import pytest
from osbot_utils.testing.Temp_File                            import Temp_File
from osbot_utils.type_safe.Type_Safe                          import Type_Safe
from osbot_utils.utils.Files                                  import file_contents
from osbot_utils.utils.Json                                   import json_load_file
from osbot_utils.utils.Toml                                   import toml_dict_from_file
from osbot_fast_api.api.Fast_API                              import Fast_API
from osbot_fast_api.api.transformers.Type_Safe__To__OpenAPI   import Type_Safe__To__OpenAPI, type_safe__to__openapi


class test_Type_Safe__To__OpenAPI(TestCase):

    def setUp(self):                                                                      # Initialize test environment
        self.converter = Type_Safe__To__OpenAPI()
        self.converter.components_cache.clear()                                          # Clear cache for clean tests

    def test__simple_conversion(self):                                                   # Test simple Type_Safe to OpenAPI
        class SimpleClass(Type_Safe):
            name   : str
            age    : int
            active : bool = True

        schema_ref = self.converter.convert_class(SimpleClass)                           # Convert to OpenAPI schema

        assert schema_ref == {'$ref': '#/components/schemas/SimpleClass'}                # Verify reference created

        cached_schema = self.converter.components_cache['SimpleClass']                   # Check cached schema

        assert cached_schema == { 'additionalProperties': False     ,
                                  'properties'          : { 'active': { 'type': 'boolean'},
                                                            'age'   : { 'type': 'integer'},
                                                            'name'  : { 'type': 'string'}},
                                  'required'            : []            ,
                                  'type'                : 'object'      }

    def test__with_custom_component_name(self):                                          # Test custom component naming
        class UserClass(Type_Safe):
            username : str
            email    : str

        schema_ref = self.converter.convert_class(UserClass, component_name='User')      # Use custom name

        assert schema_ref == {'$ref': '#/components/schemas/User'}                       # Verify custom name used
        assert 'User' in self.converter.components_cache
        assert 'UserClass' not in self.converter.components_cache

    def test__with_example(self):                                                        # Test adding examples
        class PersonClass(Type_Safe):
            name : str
            age  : int

        example         = {'name': 'John Doe', 'age': 30}
        schema_ref      = self.converter.convert_class(PersonClass, example=example)          # Add example
        cached_schema   = self.converter.components_cache['PersonClass']

        assert schema_ref    == {'$ref': '#/components/schemas/PersonClass'}
        assert cached_schema == { 'additionalProperties': False,
                                  'example'             : {'age' : 30                ,
                                                           'name': 'John Doe'        },
                                  'properties'          : {'age': { 'type': 'integer'},
                                                          'name': { 'type': 'string'}},
                                  'required'            : [],
                                  'type'                : 'object'}

    def test__create_operation(self):                                                    # Test operation creation
        class RequestBody(Type_Safe):
            title   : str
            content : str

        class ResponseBody(Type_Safe):
            id      : int
            message : str

        operation = self.converter.create_operation(                                     # Create operation
            method_name  = 'createPost'                ,
            summary      = 'Create a new post'         ,
            description  = 'Creates a new blog post'   ,
            request_body = RequestBody                 ,
            response     = ResponseBody                ,
            tags         = ['posts']
        )

        assert operation['operationId'] == 'createPost'                                  # Verify operation structure
        assert operation['summary'     ] == 'Create a new post'
        assert operation['description' ] == 'Creates a new blog post'
        assert operation['tags'        ] == ['posts']

        assert operation['requestBody']['required'] == True                              # Verify request body
        request_schema = operation['requestBody']['content']['application/json']['schema']
        assert request_schema == {'$ref': '#/components/schemas/RequestBody'}

        assert '200' in operation['responses']                                           # Verify responses
        response_schema = operation['responses']['200']['content']['application/json']['schema']
        assert response_schema == {'$ref': '#/components/schemas/ResponseBody'}

        assert operation['responses']['400']['description'] == 'Bad request'             # Default error responses
        assert operation['responses']['500']['description'] == 'Internal server error'

    def test__create_parameter(self):                                                    # Test parameter creation
        param = self.converter.create_parameter(                                         # Create query parameter
            name        = 'limit'                          ,
            location    = 'query'                          ,
            param_type  = int                              ,
            required    = False                            ,
            description = 'Number of items to return'      ,
            example     = 10
        )

        assert param['name'       ] == 'limit'                                           # Verify parameter structure
        assert param['in'         ] == 'query'
        assert param['required'   ] == False
        assert param['description'] == 'Number of items to return'
        assert param['schema'     ] == {'type': 'integer'}
        assert param['example'    ] == 10


    def test__regression__type_safe__list_dict_param__not_supported(self):
        from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe
        @type_safe
        def create_openapi_spec(servers     : List[Dict[str, str]]):
            return servers[0]['url']
        # error_message = "Validation for list items with subscripted type 'typing.Dict[str, str]' is not yet supported in parameter 'servers'."
        # with pytest.raises(NotImplementedError, match=re.escape(error_message)):
        #     create_openapi_spec(servers     = [{'url': 'https://api.example.com'}])
        assert create_openapi_spec(servers=[{'url': 'https://api.example.com'}]) == 'https://api.example.com'

    def test__create_openapi_spec(self):                                                 # Test full spec creation
        spec = self.converter.create_openapi_spec( title       = 'Test API'                                 ,
                                                   version     = '1.0.0'                                    ,
                                                   description = 'Test API Description'                     ,
                                                   servers     = [{'url': 'https://api.example.com'}])
        assert spec == { 'components': { 'schemas'    : {}                    },
                         'info'      : { 'description': 'Test API Description',
                                         'title'      : 'Test API'            ,
                                         'version'    : '1.0.0'               },
                         'openapi'   : '3.0.0'                                ,
                         'paths'     : {}                                     ,
                         'servers'   : [{'url': 'https://api.example.com'     }]}

        assert spec['openapi'              ] == '3.0.0'                                   # Verify spec structure
        assert spec['info']['title'        ] == 'Test API'
        assert spec['info']['version'      ] == '1.0.0'
        assert spec['info']['description'  ] == 'Test API Description'
        assert spec['servers'              ] == [{'url': 'https://api.example.com'}]
        assert spec['paths'                ] == {}
        assert spec['components']['schemas'] == self.converter.components_cache

    def test__add_path(self):                                                            # Test adding paths to spec
        spec = self.converter.create_openapi_spec(
            title   = 'Test API'  ,
            version = '1.0.0'
        )

        operation = {
            'operationId': 'getUser'                          ,
            'summary'    : 'Get user by ID'                   ,
            'responses'  : {'200': {'description': 'Success'}}
        }

        self.converter.add_path(spec, '/users/{id}', 'GET', operation)                   # Add path operation

        assert '/users/{id}' in spec['paths']                                            # Verify path added
        assert spec['paths']['/users/{id}']['get'] == operation

    def test__export_to_file(self):                                       # Test file export
        if sys.version_info < (3, 11):
            pytest.skip("TOML parsing is not supported in Python versions earlier than 3.11")

        spec  = self.converter.create_openapi_spec(title   = 'Export Test API',  version = '2.0.0')
        assert spec == { 'components': {'schemas': {}},
                         'info'      : {'title': 'Export Test API', 'version': '2.0.0'},
                         'openapi'   : '3.0.0',
                         'paths'     : {},
                         'servers'   : [{'url': '/'}]}

        # Test JSON export
        with Temp_File(file_name='openapi.json', return_file_path=True) as json_file:
            self.converter.export_to_file(spec, json_file, format='json')

            assert json_load_file(json_file) == spec
            with open(json_file, 'r') as f:
                loaded_spec = json.load(f)
            assert loaded_spec['info']['title'] == 'Export Test API'

        # Test TOML export
        with Temp_File(extension='toml', return_file_path=True) as toml_file:
            self.converter.export_to_file(spec, toml_file, format='toml')
            assert file_contents(toml_file) == """\
openapi = '3.0.0'
[info]
    title = 'Export Test API'
    version = '2.0.0'
[paths]
[components]
[components.schemas]
[[servers]]
    url = '/'
"""
            assert toml_dict_from_file(toml_file) == spec
            loaded_spec = toml_dict_from_file(toml_file)
            assert loaded_spec['info']['title'] == 'Export Test API'
            assert loaded_spec['info']['version'] == '2.0.0'
            assert loaded_spec['openapi'] == '3.0.0'
            assert loaded_spec['paths'] == {}
            assert loaded_spec['servers'] == [{'url': '/'}]

    def test__nested_type_safe_classes(self):                                            # Test nested Type_Safe in OpenAPI
        class Address(Type_Safe):
            street : str
            city   : str

        class Person(Type_Safe):
            name    : str
            address : Address

        schema_ref = self.converter.convert_class(Person)                                # Convert nested structure

        assert schema_ref == {'$ref': '#/components/schemas/Person'}


        assert 'Person'      in self.converter.components_cache                               # Both classes in cache
        assert 'Address'     in self.converter.components_cache

        person_schema = self.converter.components_cache['Person']
        assert person_schema == { 'additionalProperties': False,
                                  'properties'          : { 'address': {'$ref': '#/components/schemas/Address'},
                                                            'name'   : {'type': 'string'}},
                                  'required'            : []        ,
                                  'type'                : 'object'}

        assert person_schema['properties']['address'] == {'$ref': '#/components/schemas/Address'}

    # todo: QUESTION: Why do we need this, isn't this what FastAPI already creates?
    def test__generate_from_fast_api_routes(self):                                       # Test generating from Fast_API
        class TestAPI(Fast_API):
            name        = 'Test API'
            version     = 'v1.0.0'
            description = 'Test Description'

            def setup_routes(self):
                def get_status():
                    return {'status': 'ok'}

                def create_item():
                    return {'id': 1}

                self.add_route_get(get_status)
                self.add_route_post(create_item)

        api = TestAPI().setup()
        spec = self.converter.generate_from_fast_api_routes(api)                         # Generate spec from API

        assert spec['info']['title'      ] == 'Test API'                                 # Verify spec generated
        assert spec['info']['version'    ] == 'v1.0.0'
        assert spec['info']['description'] == 'Test Description'

        assert '/get-status' in spec['paths']                                            # Verify routes added
        assert 'get' in spec['paths']['/get-status']
        assert spec['paths']['/get-status']['get']['operationId'] == 'get_status'

        assert '/create-item' in spec['paths']
        assert 'post' in spec['paths']['/create-item']
        assert spec['paths']['/create-item']['post']['operationId'] == 'create_item'

    def test__caching(self):                                                             # Test component caching
        class CachedClass(Type_Safe):
            value : str

        ref1 = self.converter.convert_class(CachedClass)                                 # First conversion
        ref2 = self.converter.convert_class(CachedClass)                                 # Second should return ref

        assert ref1 == ref2                                                              # Same reference
        assert ref1 == {'$ref': '#/components/schemas/CachedClass'}
        assert len(self.converter.components_cache) == 1                                 # Only one entry in cache




    def test__complex_operation(self):                                                   # Test complex operation with params
        class QueryParams(Type_Safe):
            search : str
            limit  : int = 10

        class RequestData(Type_Safe):
            data : Dict[str, str]

        class ResponseData(Type_Safe):
            results : List[Dict[str, str]]
            total   : int

        parameters = [
            self.converter.create_parameter('search', 'query', str, required=True)  ,
            self.converter.create_parameter('limit' , 'query', int, required=False) ,
            self.converter.create_parameter('id'    , 'path' , str, required=True)
        ]

        operation = self.converter.create_operation(method_name  = 'searchItems'                           ,
                                                    summary      = 'Search items'                          ,
                                                    description  = 'Search for items with filters'         ,
                                                    request_body = RequestData                             ,
                                                    response     = ResponseData                            ,
                                                    parameters   = parameters                              ,
                                                    tags         = ['search', 'items'])

        assert operation['operationId'] == 'searchItems'                                 # Verify complex operation
        assert len(operation['parameters']) == 3
        assert operation['parameters'][0]['name'] == 'search'
        assert operation['parameters'][1]['name'] == 'limit'
        assert operation['parameters'][2]['name'] == 'id'
        assert operation['tags'] == ['search', 'items']

    def test__singleton_instance(self):                                                  # Test singleton works
        class TestClass(Type_Safe):
            value : int

        ref = type_safe__to__openapi.convert_class(TestClass)                            # Use singleton
        assert ref == {'$ref': '#/components/schemas/TestClass'}
        assert 'TestClass' in type_safe__to__openapi.components_cache

    def test__nullable_field_conversion(self):                                           # Test nullable field handling
        class NullableClass(Type_Safe):
            required : str
            optional : Optional[str] = None

        schema_ref = self.converter.convert_class(NullableClass)                         # Convert with nullable

        schema = self.converter.components_cache['NullableClass']
        assert schema['properties']['optional']['nullable'] == True                      # Verify nullable preserved
        assert 'nullable' not in schema['properties']['required']                        # Required not nullable