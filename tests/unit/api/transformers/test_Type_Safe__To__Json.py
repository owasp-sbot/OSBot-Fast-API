import json
from typing                                                 import List, Dict, Optional, Union
from unittest                                               import TestCase
from osbot_utils.type_safe.Type_Safe                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str         import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_Int         import Safe_Int
from osbot_utils.type_safe.primitives.core.Safe_Float       import Safe_Float
from osbot_fast_api.api.transformers.Type_Safe__To__Json    import Type_Safe__To__Json, type_safe__to__json


class test_Type_Safe__To__Json(TestCase):

    def setUp(self):                                                                      # Initialize test environment
        self.converter = Type_Safe__To__Json()
        self.converter.schema_cache.clear()                                              # Clear cache for clean tests

    def test__simple_conversion(self):                                                  # Test simple Type_Safe to JSON Schema
        class SimpleClass(Type_Safe):
            name   : str                # note: Type_Safe will try to assigned default values for primitives
            age    : int                #       which in this case is name = '' and age = 0
            active : bool = True

        schema = self.converter.convert_class(SimpleClass)                               # Convert to JSON Schema

        assert schema== { '$schema'             : 'http://json-schema.org/draft-07/schema#',
                          'additionalProperties': False,
                          'properties'          : { 'active': {'default': True, 'type': 'boolean' },
                                                    'age'   : {'default': 0   , 'type': 'integer' },
                                                    'name'  : {'default': ''  , 'type': 'string'  }},
                          'title'               : 'SimpleClass'                                  ,
                          'type'                : 'object'                                       }

    def test__simple_conversion__with_no_required(self):                                                   # Test simple Type_Safe to JSON Schema
        class SimpleClass(Type_Safe):
            name   : str  = None
            age    : int  = None
            active : bool = True

        schema = self.converter.convert_class(SimpleClass)                               # Convert to JSON Schema

        assert schema== { '$schema'             : 'http://json-schema.org/draft-07/schema#',
                          'additionalProperties': False,
                          'properties'          : { 'active': {'default': True, 'type': 'boolean'},
                                                    'age'   : {'type'   : 'integer'              },
                                                    'name'  : {'type'   : 'string'               }},
                          'title'               : 'SimpleClass'                                  ,
                          'type'                : 'object'                                       }

    def test__with_safe_primitives(self):                                                # Test Safe_* primitive constraints
        class SafeStr_Custom(Safe_Str):
            max_length = 100

        class SafeInt_Custom(Safe_Int):
            min_value = 0
            max_value = 150

        class SafeFloat_Custom(Safe_Float):
            min_value = 0.0
            max_value = 100.0

        class SafeClass(Type_Safe):
            name  : SafeStr_Custom
            age   : SafeInt_Custom
            score : SafeFloat_Custom

        self.converter.strict_mode = True                                                # Enable strict mode for constraints
        schema = self.converter.convert_class(SafeClass)

        assert schema['properties']['name' ]['type'     ] == 'string'                    # Verify Safe_Str constraints
        assert schema['properties']['name' ]['maxLength'] == 100

        assert schema['properties']['age'  ]['type'    ] == 'integer'                    # Verify Safe_Int constraints
        assert schema['properties']['age'  ]['minimum' ] == 0
        assert schema['properties']['age'  ]['maximum' ] == 150

        assert schema['properties']['score']['type'    ] == 'number'                     # Verify Safe_Float constraints
        assert schema['properties']['score']['minimum' ] == 0.0
        assert schema['properties']['score']['maximum' ] == 100.0

    def test__nested_type_safe_classes(self):                                            # Test nested Type_Safe classes
        class Address(Type_Safe):
            street   : str
            city     : str
            zip_code : str

        class Person(Type_Safe):
            name    : str
            address : Address

        schema = self.converter.convert_class(Person)                                    # Convert to JSON Schema
        assert schema == { '$schema'             : 'http://json-schema.org/draft-07/schema#',
                           'additionalProperties': False,
                           'properties'          : { 'address': {  'additionalProperties': False,
                                                                   'properties'          : { 'city'    : {'default': '', 'type': 'string'},
                                                                                            'street'  : {'default': '', 'type': 'string'},
                                                                                            'zip_code': {'default': '', 'type': 'string'}},
                                                                   'title'               : 'Address',
                                                                   'type'                : 'object'},
                                                      'name'   : { 'default': '', 'type': 'string'}},
                           'title'             : 'Person',
                           'type'              : 'object' }

        assert schema['properties']['name']['type'] == 'string'                          # Verify nested schema structure

        address_schema = schema['properties']['address']
        assert address_schema['type'      ]                     == 'object'
        assert address_schema['properties']['street'  ]['type'] == 'string'
        assert address_schema['properties']['city'    ]['type'] == 'string'
        assert address_schema['properties']['zip_code']['type'] == 'string'

        assert '$schema' not in address_schema                                           # No $schema in nested objects

    def test__list_types(self):                                                          # Test List type conversion
        class TeamClass(Type_Safe):
            name    : str
            members : List[str]
            scores  : List[int]

        schema = self.converter.convert_class(TeamClass)                                 # Convert to JSON Schema

        assert schema['properties']['members'] == { 'type' : 'array'                ,    # Verify array schemas
                                                    'items': {'type': 'string'}      }
        assert schema['properties']['scores' ] == { 'type' : 'array'                ,
                                                    'items': {'type': 'integer'}     }

    def test__dict_types(self):                                                          # Test Dict type conversion
        class ConfigClass(Type_Safe):
            settings : Dict[str, str]
            values   : Dict[str, int]

        schema = self.converter.convert_class(ConfigClass)                               # Convert to JSON Schema

        assert schema['properties']['settings'] == { 'type'                 : 'object'              ,  # Verify object schemas
                                                     'additionalProperties': {'type': 'string'}      }
        assert schema['properties']['values'  ] == { 'type'                 : 'object'              ,
                                                     'additionalProperties': {'type': 'integer'}     }

    def test__optional_types(self):                                                      # Test Optional type conversion
        class OptionalClass(Type_Safe):
            required  : str
            optional  : Optional[str] = None
            maybe_int : Optional[int] = None

        schema = self.converter.convert_class(OptionalClass)                             # Convert to JSON Schema

        assert schema == { '$schema'             : 'http://json-schema.org/draft-07/schema#',
                           'additionalProperties': False    ,
                           'properties'          : { 'maybe_int': {'nullable': True, 'type': 'integer'},
                                                     'optional' : {'nullable': True, 'type': 'string' },
                                                     'required' : {'default': '', 'type': 'string'    }},
                           'title'               : 'OptionalClass'  ,
                           'type'                : 'object'         }


    def test__union_types(self):                                                         # Test Union type conversion
        class UnionClass(Type_Safe):
            str_or_int : Union[str, int]
            multi_type : Union[str, int, float]

        schema = self.converter.convert_class(UnionClass)                                # Convert to JSON Schema

        assert schema['properties']['str_or_int'] == { 'oneOf': [ {'type': 'string' } ,  # Verify oneOf schemas
                                                                  {'type': 'integer'} ]}
        assert schema['properties']['multi_type'] == { 'oneOf': [ {'type': 'string'} ,
                                                                  {'type': 'integer'},
                                                                  {'type': 'number' } ]}

    def test__set_types(self):                                                           # Test Set type conversion
        class SetClass(Type_Safe):
            tags    : set[str]
            numbers : set[int]

        schema = self.converter.convert_class(SetClass)                                  # Convert to JSON Schema

        assert schema['properties']['tags'   ] == { 'type'       : 'array'          ,    # Sets become arrays with uniqueItems
                                                    'uniqueItems': True              ,
                                                    'items'      : {'type': 'string'} }
        assert schema['properties']['numbers'] == { 'type'       : 'array'           ,
                                                    'uniqueItems': True               ,
                                                    'items'      : {'type': 'integer'} }

    def test__convert_to_json_schema_string(self):                                       # Test JSON string output
        class TestClass(Type_Safe):
            name  : str
            value : int

        json_string = self.converter.convert_to_json_schema_string(TestClass)            # Convert to JSON string
        schema_dict = json.loads(json_string)                                            # Parse back to verify

        assert isinstance(json_string, str)
        assert schema_dict['title'] == 'TestClass'
        assert schema_dict['properties']['name' ]['type'] == 'string'
        assert schema_dict['properties']['value']['type'] == 'integer'

    def test__caching(self):                                                             # Test schema caching
        class CachedClass(Type_Safe):
            value : str

        schema1 = self.converter.convert_class(CachedClass)                              # First conversion
        schema2 = self.converter.convert_class(CachedClass)                              # Second should return cached

        assert schema1 is schema2                                                        # Should be same object
        assert (CachedClass, False) in self.converter.schema_cache                                # Verify cache contains class

    def test__with_title_and_description(self):                                          # Test custom title and description
        class DocumentedClass(Type_Safe):
            field : str

        schema = self.converter.convert_class(DocumentedClass                  ,
                                              title       = "Custom Title"      ,
                                              description = "Custom description")

        assert schema['title'      ] == 'Custom Title'
        assert schema['description'] == 'Custom description'

    def test__complex_nested_structure(self):                                            # Test complex nested structures
        class Item(Type_Safe):
            id    : str
            name  : str
            price : float

        class Order(Type_Safe):
            order_id : str
            items    : List[Item]
            metadata : Dict[str, str]

        class Customer(Type_Safe):
            name   : str
            orders : List[Order]

        schema = self.converter.convert_class(Customer)                                  # Convert complex structure
        assert schema['$schema'   ] == 'http://json-schema.org/draft-07/schema#'
        assert schema['properties'] == { 'name'  : { 'default': '', 'type': 'string' },
                                         'orders': { 'items': {  'additionalProperties': False,
                                                                 'properties'          : { 'items'   : { 'items': { 'additionalProperties': False,
                                                                                                                    'properties'          : { 'id'   : { 'default': '', 'type': 'string' },
                                                                                                                                              'name' : { 'default': '', 'type': 'string' },
                                                                                                                                              'price': { 'default': 0.0, 'type': 'number' }},
                                                                                                                    'title'               : 'Item',
                                                                                                                    'type'                : 'object' },
                                                                                                         'type' : 'array' },
                                                                                          'metadata': { 'additionalProperties': { 'type': 'string' },
                                                                                                        'type'                : 'object' },
                                                                                          'order_id': { 'default': '', 'type': 'string' }},
                                                                'title'               : 'Order',
                                                                'type'                : 'object' },
                                                     'type' : 'array' }}

    def test__validate_against_schema(self):                                             # Test schema validation
        class ValidatedClass(Type_Safe):
            name : str
            age  : int

        instance = ValidatedClass(name="Alice", age=30)
        schema   = self.converter.convert_class(ValidatedClass)

        try:
            import jsonschema
            assert self.converter.validate_against_schema(instance, schema) == True       # Valid instance passes

            instance.age = "not_an_int"                                                  # This would fail Type_Safe validation
        except ImportError:
            pass                                                                          # Skip if jsonschema not installed

    def test__singleton_instance(self):                                                  # Test singleton works
        class TestClass(Type_Safe):
            value : int

        schema = type_safe__to__json.convert_class(TestClass)                            # Use singleton
        assert schema['title'] == 'TestClass'
        assert schema['properties']['value']['type'] == 'integer'

    def test__with_defaults_disabled(self):                                              # Test without including defaults
        class DefaultClass(Type_Safe):
            name  : str
            value : int = 42

        with self.converter as _:
            _.include_defaults = False
            schema = _.convert_class(DefaultClass)
            assert schema['properties'] == {'name' : {'type': 'string'},
                                            'value': {'type': 'integer'}}
            assert 'default' not in schema['properties']['name']                                # No default for required field
            assert 'default' not in schema['properties']['value']                               # Default excluded when disabled
            _.schema_cache.clear()
            _.include_defaults = True                                                           # Re-enable and test
            schema = _.convert_class(DefaultClass)                                              # clear cache
            assert schema['properties'] == {'name' : {'default': '', 'type': 'string' },        # Defaults included when enabled
                                            'value': {'default': 42, 'type': 'integer'}}