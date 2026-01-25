import re
import sys
import pytest
from typing                                                          import List, Dict, Optional, Union, Set
from unittest                                                        import TestCase
from osbot_utils.testing.__                                          import __
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Set import Type_Safe__Set
from pydantic                                                        import BaseModel, ValidationError
from osbot_utils.testing.__helpers                                   import obj
from osbot_utils.type_safe.Type_Safe                                 import Type_Safe
from osbot_fast_api.api.transformers.Type_Safe__To__BaseModel        import Type_Safe__To__BaseModel, type_safe__to__basemodel
from osbot_utils.type_safe.primitives.core.Safe_Int                  import Safe_Int
from osbot_utils.type_safe.primitives.core.Safe_Str                  import Safe_Str


class test_Type_Safe__To__BaseModel(TestCase):

    def setUp(self):                                                                      # Initialize test environment
        self.converter = Type_Safe__To__BaseModel()
        self.converter.model_cache.clear()                                               # Clear cache for clean tests</

    def test__simple_conversion(self):                                                    # Test simple Type_Safe to BaseModel
        class SimpleClass(Type_Safe):
            name   : str
            age    : int
            active : bool = True

        BaseModelClass = self.converter.convert_class(SimpleClass)                        # Convert class

        assert issubclass(BaseModelClass, BaseModel)                                      # Verify it's a BaseModel subclass
        assert BaseModelClass.__name__ == "SimpleClass__BaseModel"

        instance = BaseModelClass(name="John", age=30)                                    # Create instance and verify fields
        assert instance.name   == "John"
        assert instance.age    == 30
        assert instance.active == True                                                    # Default value

        with pytest.raises(ValidationError):                                              # Verify Pydantic validation works
            BaseModelClass(name="John", age="not_an_int")

    def test__instance_conversion(self):                                                  # Test Type_Safe instance conversion
        class PersonClass(Type_Safe):
            name  : str
            age   : int
            email : Optional[str] = None

        person     = PersonClass(name="Alice", age=25, email="alice@example.com")         # Create Type_Safe instance
        base_model = self.converter.convert_instance(person)                              # Convert to BaseModel

        assert isinstance(base_model, BaseModel)                                          # Verify conversion
        assert base_model.name  == "Alice"
        assert base_model.age   == 25
        assert base_model.email == "alice@example.com"

        person_dict = base_model.dict()                                                   # Verify we can get dict and JSON
        person_json = base_model.json()

        assert person_dict       == {'name': 'Alice', 'age': 25, 'email': 'alice@example.com'}
        assert type(person_dict) is dict
        assert person_json       == '{"name":"Alice","age":25,"email":"alice@example.com"}'
        assert type(person_json) is str

    def test__nested_type_safe_classes(self):                                             # Test nested Type_Safe classes
        class Address(Type_Safe):
            street   : str
            city     : str
            zip_code : str

        class Person(Type_Safe):
            name    : str
            address : Address

        address    = Address(street="123 Main St", city="Boston", zip_code="02101")       # Create nested instances
        person     = Person(name="Bob", address=address)
        base_model = self.converter.convert_instance(person)                              # Convert to BaseModel

        assert base_model.name == "Bob"                                                   # Verify nested structure
        assert base_model.address.street   == "123 Main St"
        assert base_model.address.city     == "Boston"
        assert base_model.address.zip_code == "02101"

        person_dict = base_model.dict()                                                   # Verify dict maintains structure
        assert person_dict == { 'name'   : 'Bob'                     ,
                               'address' : { 'street'   : '123 Main St' ,
                                           'city'     : 'Boston'       ,
                                           'zip_code' : '02101'        }}

    def test__list_conversion(self):                                                      # Test List fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        class TeamMember(Type_Safe):
            name : str
            role : str

        class Team(Type_Safe):
            name    : str
            members : List[TeamMember]
            tags    : List[str]

        team = Team(name    = "Development"                              ,                # Create Type_Safe with lists
                   members = [ TeamMember(name="Alice", role="Lead")     ,
                              TeamMember(name="Bob", role="Developer")  ],
                   tags    = ["python", "backend"]                       )

        base_model = self.converter.convert_instance(team)                                # Convert to BaseModel

        assert base_model.name              == "Development"                              # Verify list conversion
        assert len(base_model.members)      == 2
        assert base_model.members[0].name   == "Alice"
        assert base_model.members[0].role   == "Lead"
        assert base_model.members[1].name   == "Bob"
        assert base_model.tags              == ["python", "backend"]

    def test__dict_conversion(self):                                                      # Test Dict fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        class Config(Type_Safe):
            settings : Dict[str, str]
            values   : Dict[str, int]

        config = Config(settings = {"env": "prod", "region": "us-east"} ,                 # Create Type_Safe with dicts
                       values   = {"timeout": 30, "retries": 3}        )

        base_model = self.converter.convert_instance(config)                              # Convert to BaseModel

        assert base_model.settings == {"env": "prod", "region": "us-east"}                # Verify dict conversion
        assert base_model.values   == {"timeout": 30, "retries": 3}

    def test__optional_and_union_types(self):                                            # Test Optional and Union types
        class FlexibleClass(Type_Safe):
            required    : str
            optional    : Optional[int]    = None
            union_field : Union[str, int] = "default"

        instance1  = FlexibleClass(required="test")                                       # Test with optional None
        base_model1 = self.converter.convert_instance(instance1)
        assert base_model1.optional    is None
        assert base_model1.union_field == "default"

        instance2  = FlexibleClass(required="test", optional=42, union_field=100)         # Test with values set
        base_model2 = self.converter.convert_instance(instance2)
        assert base_model2.optional    == 42
        assert base_model2.union_field == 100

    def test__caching(self):                                                              # Test model generation caching
        class CachedClass(Type_Safe):
            value : str

        model1 = self.converter.convert_class(CachedClass)                                # First conversion
        model2 = self.converter.convert_class(CachedClass)                                # Second should return cached

        assert model1 is model2                                                           # Should be same class
        assert CachedClass in self.converter.model_cache                                 # Verify cache contains class

    def test__fastapi_compatibility(self):                                                  # Test FastAPI pattern compatibility
        class APIRequest(Type_Safe):
            endpoint : str                                                                  # Type_Safe will assign the default value to endpoint (in this case '')
            method   : str                      = "GET"
            headers  : Optional[Dict[str, str]] = None

        RequestModel = self.converter.convert_class(APIRequest)                             # Convert to BaseModel
        schema       = RequestModel.model_json_schema()                                     # Test schema generation
        assert APIRequest().obj() == __(method='GET', headers=None, endpoint='')
        assert schema             == { 'properties': {'endpoint': { 'default': ''                                           ,
                                                                    'title'  : 'Endpoint'                                   ,
                                                                    'type'   : 'string'                                     },
                                                      'headers' : { 'anyOf'  : [{ 'additionalProperties': {'type': 'string' },
                                                                                  'type'                : 'object'          },
                                                                                {'type'                 : 'null'            }],
                                                                    'title'  : 'Headers'                                     ,
                                                                    'default': None,},
                                                      'method'  : { 'default': 'GET'                                         ,
                                                                    'title'  : 'Method'                                      ,
                                                                    'type'   : 'string'                                      }},
                                       'title'   : 'APIRequest__BaseModel'                                                     ,
                                       'type'    : 'object'                                                                    }

    def test__fastapi_compatibility__with_str_as_none(self):                                                # Test FastAPI pattern compatibility
        class APIRequest(Type_Safe):
            endpoint : str                      = None                                                      # now with endpoint explicitly set to None
            method   : str                      = "GET"
            headers  : Optional[Dict[str, str]] = None

        RequestModel = self.converter.convert_class(APIRequest)                                             # Convert to BaseModel
        schema       = RequestModel.model_json_schema()                                                     # Test schema generation
        assert APIRequest().obj() == __(method='GET', headers=None, endpoint=None)
        assert schema             == { 'properties': {'endpoint': { 'anyOf': [{'type': 'string'}, {'type': 'null'}],
                                                                    'title'  : 'Endpoint'                                   ,
                                                                    'default': None                                         },
                                                      'headers' : { 'anyOf'  : [{ 'additionalProperties': {'type': 'string' },
                                                                                  'type'                : 'object'          },
                                                                                {'type'                 : 'null'            }],
                                                                    'title'  : 'Headers'                                     ,
                                                                    'default': None                                          },
                                                      'method'  : { 'default': 'GET'                                         ,
                                                                    'title'  : 'Method'                                      ,
                                                                    'type'   : 'string'                                      }},
                                       'title'   : 'APIRequest__BaseModel'                                                     ,
                                       'type'    : 'object'                                                                    }


    def test__complex_nested_structure(self):                                             # Test complex nested structures
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

        customer = Customer(name   = "John"                                     ,         # Create complex structure
                           orders = [ Order(order_id = "001"                   ,
                                          items    = [ Item(id    = "1"        ,
                                                          name  = "Widget"    ,
                                                          price = 9.99)       ,
                                                     Item(id    = "2"        ,
                                                          name  = "Gadget"    ,
                                                          price = 19.99)     ],
                                          metadata = { "source"   : "web"       ,
                                                      "priority" : "high"      })])

        base_model = self.converter.convert_instance(customer)                            # Convert to BaseModel

        assert base_model.name                                == "John"                   # Verify complex structure
        assert len(base_model.orders)                         == 1
        assert base_model.orders[0].order_id                  == "001"
        assert len(base_model.orders[0].items)                == 2
        assert base_model.orders[0].items[0].name             == "Widget"
        assert base_model.orders[0].items[0].price            == 9.99
        assert base_model.orders[0].metadata.get('source'  )  == "web"
        assert base_model.orders[0].metadata.get('priority')  == "high"
        assert base_model.model_dump()                        == { 'name'  : 'John',
                                                                   'orders': [{ 'items'   : [{ 'id': '1', 'name': 'Widget', 'price': 9.99 },
                                                                                             { 'id': '2', 'name': 'Gadget', 'price': 19.99}],
                                                                                'metadata' : { 'priority': 'high', 'source': 'web'          },
                                                                                'order_id' :   '001'}                                       ]}

        assert base_model.model_dump()                           == customer.json()                 # confirm roundtrip and full compatibility with the original Type_Safe class
        assert Customer.from_json(base_model.model_dump()).obj() == customer.obj()
        assert Customer.from_json(base_model.model_dump()).obj() == __( name   = 'John',
                                                                        orders = [__( order_id = '001',
                                                                                      items    = [ __(id='1', name='Widget', price=9.99),
                                                                                                   __(id='2', name='Gadget', price=19.99)],
                                                                                      metadata  = __(source='web', priority='high'      ))])



    def test__singleton_instance(self):                                                   # Test singleton instance works
        class SingletonTest(Type_Safe):
            value : int

        model    = type_safe__to__basemodel.convert_class(SingletonTest)                  # Use singleton
        instance = model(value=42)                                                        # Verify it works
        assert instance.value == 42

    def test__validation_errors_propagate(self):                                          # Test Pydantic validation errors
        class ValidatedClass(Type_Safe):
            email : str                                                                   # In real scenario, might have validator
            age   : int

        ModelClass = self.converter.convert_class(ValidatedClass)

        valid = ModelClass(email="test@example.com", age=25)                              # Valid instance
        assert valid.email == "test@example.com"
        assert valid.age   == 25

        with pytest.raises(ValidationError) as exc_info:                                  # Invalid age type
            ModelClass(email="test@example.com", age="twenty-five")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error['loc'] == ('age',) for error in errors)

    def test__convert_class__check_type_safe_attribute(self):
        expected_error_1 = "Parameter 'type_safe_class' expected a type class but got <class 'str'>"
        with pytest.raises(ValueError, match=expected_error_1):
            assert self.converter.convert_class('aaa')                                  # should raise exception since 'aaa' is not a Type_Safe class

        expected_error_2 = "Parameter 'type_safe_class' expected a type class but got <class 'test_Type_Safe__To__BaseModel.test_Type_Safe__To__BaseModel.test__convert_class__check_type_safe_attribute.<locals>.Simple_Class'>"
        class Simple_Class(Type_Safe):
            an_str : str

        with pytest.raises(ValueError, match=expected_error_2):
            assert self.converter.convert_class(Simple_Class())                             # should raise exception since Simple_Class() is an Type_Safe instance not a Type_Safe class

        from pydantic._internal._model_construction import ModelMetaclass
        assert isinstance(self.converter.convert_class(Simple_Class), ModelMetaclass)         # confirm we get an internal pydantic ModelMetaclass when we pass a Type_Safe type

    def test__convert_instance__check_type_safe_attribute(self):
        expected_error_1 = "Parameter 'type_safe_instance' expected type <class 'osbot_utils.type_safe.Type_Safe.Type_Safe'>, but got <class 'str'>"
        with pytest.raises(ValueError, match=re.escape(expected_error_1)):
            assert self.converter.convert_instance('aaa')                                   # should raise exception since 'aaa' is not a Type_Safe instance

        expected_error_2 = "Parameter 'type_safe_instance' expected type <class 'osbot_utils.type_safe.Type_Safe.Type_Safe'>, but got <class 'type'>"
        class Simple_Class(Type_Safe):
            an_str : str

        with pytest.raises(ValueError, match=re.escape(expected_error_2)):
            assert self.converter.convert_instance(Simple_Class)                            # should raise exception since Simple_Class() is an Type_Safe class not a Type_Safe instance

        assert isinstance(self.converter.convert_instance(Simple_Class()), BaseModel)       # confirm we get a base model when we pass a Type_Safe instance

    def test__handle__none_return_values(self):

        class An_Class(Type_Safe):
            an_str     : Optional[str     ] = None
            an_safe_str: Optional[Safe_Str] = None
            an_safe_int: Optional[Safe_Int] = None



        result = self.converter.convert_instance(An_Class())
        assert obj(result.model_json_schema()) == __(properties = __(an_str      = __(anyOf   = [ __(type = 'string'),
                                                                                                  __(type = 'null')  ],
                                                                                      title   = 'An Str'              ,
                                                                                      default = None                  ),
                                                                     an_safe_str = __(anyOf   = [ __(type = 'string') ,
                                                                                                  __(type = 'null')   ],
                                                                                      title   = 'An Safe Str'          ,
                                                                                      default = None                   ),
                                                                     an_safe_int = __(anyOf   = [ __(type = 'integer'),
                                                                                                  __(type = 'null')   ],
                                                                                      title   = 'An Safe Int',
                                                                                      default = None                  )),
                                                     title      = 'An_Class__BaseModel'                              ,
                                                     type       = 'object')

    def test__set_conversion(self):                                                          # Test set field conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")


        class TaggedItem(Type_Safe):
            name : str
            tags : Set[str]

        item       = TaggedItem(name="Widget", tags={"red", "large", "sale"})                 # Create with set
        base_model = self.converter.convert_instance(item)

        assert base_model.name == "Widget"                                                    # Set converted to list
        assert set(base_model.tags) == {"red", "large", "sale"}                               # verify values (order may vary)

    def test__get_default_value(self):                                                        # Test get_default_value method
        class DefaultsClass(Type_Safe):
            with_default    : str = "hello"
            without_default : int

        result_with    = self.converter.get_default_value(DefaultsClass, 'with_default')
        result_without = self.converter.get_default_value(DefaultsClass, 'without_default')
        result_missing = self.converter.get_default_value(DefaultsClass, 'nonexistent')

        assert result_with    == "hello"                                                      # has default
        assert result_without == 0                                                            # Type_Safe assigns default for int
        assert result_missing is None                                                         # nonexistent field

    def test__untyped_collections(self):                                                      # Test untyped list/dict/set handling
        class UntypedCollections(Type_Safe):
            items    : list = None
            mapping  : dict = None

        ModelClass = self.converter.convert_class(UntypedCollections)
        instance   = ModelClass(items=[1, 2, 3], mapping={"a": 1})

        assert instance.items   == [1, 2, 3]
        assert instance.mapping == {"a": 1}

    def test__convert_type__with_set_no_args(self):                                           # Test set without type args
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        result = self.converter.convert_type(Set)                                             # Set without element type
        assert result == list                                                                 # falls back to list

    def test__normalize_default_value__with_type_safe_set(self):                              # Test normalizing Type_Safe__Set
        ts_set = Type_Safe__Set(expected_type=int, initial_data={1, 2, 3})                    # Type_Safe__Set requires expected_type
        result = self.converter.normalize_default_value(ts_set)

        assert isinstance(result, list)                                                       # converted to list
        assert set(result) == {1, 2, 3}                                                       # values preserved



