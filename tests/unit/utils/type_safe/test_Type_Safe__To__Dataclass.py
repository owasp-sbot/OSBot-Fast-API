import re
import sys
import pytest
from dataclasses                                             import is_dataclass, asdict, fields
from typing                                                  import List, Dict, Optional, Union, Set
from unittest                                                import TestCase
from osbot_utils.type_safe.Type_Safe                         import Type_Safe
from osbot_fast_api.utils.type_safe.Type_Safe__To__Dataclass import Type_Safe__To__Dataclass, type_safe__to__dataclass


class test_Type_Safe__To__Dataclass(TestCase):

    def setUp(self):                                                                      # Initialize test environment
        self.converter = Type_Safe__To__Dataclass()
        self.converter.class_cache.clear()                                                # Clear cache for clean tests

    def test__simple_conversion(self):                                                    # Test simple Type_Safe to dataclass
        class SimpleClass(Type_Safe):
            name   : str
            age    : int
            active : bool = True

        DataclassType = self.converter.convert_class(SimpleClass)                         # Convert class

        assert is_dataclass(DataclassType)                                                # Verify it's a dataclass
        assert DataclassType.__name__ == "SimpleClass__Dataclass"

        instance = DataclassType(name="John", age=30)                                     # Create instance and verify fields
        assert instance.name   == "John"
        assert instance.age    == 30
        assert instance.active == True                                                    # Default value preserved

        # Verify dataclass features work
        assert asdict(instance) == {'name': 'John', 'age': 30, 'active': True}

    def test__instance_conversion(self):                                                  # Test Type_Safe instance conversion
        class PersonClass(Type_Safe):
            email : Optional[str] = None
            name  : str
            age   : int

        person     = PersonClass(name="Alice", age=25, email="alice@example.com")         # Create Type_Safe instance
        person_dc  = self.converter.convert_instance(person)                              # Convert to dataclass

        assert is_dataclass(person_dc)                                                    # Verify it's a dataclass instance
        assert person_dc.name  == "Alice"
        assert person_dc.age   == 25
        assert person_dc.email == "alice@example.com"

        person_dict = asdict(person_dc)                                                   # Verify dataclass methods work
        assert person_dict == {'name': 'Alice', 'age': 25, 'email': 'alice@example.com'}

    def test__nested_type_safe_classes(self):                                             # Test nested Type_Safe classes
        class Address(Type_Safe):
            street   : str
            city     : str
            zip_code : str

        class Person(Type_Safe):
            name    : str
            address : Address

        address   = Address(street="123 Main St", city="Boston", zip_code="02101")        # Create nested instances
        person    = Person(name="Bob", address=address)
        person_dc = self.converter.convert_instance(person)                               # Convert to dataclass

        assert is_dataclass(person_dc)                                                    # Verify dataclass structure
        assert person_dc.name == "Bob"
        assert is_dataclass(person_dc.address)                                            # Nested is also dataclass
        assert person_dc.address.street   == "123 Main St"
        assert person_dc.address.city     == "Boston"
        assert person_dc.address.zip_code == "02101"

        assert asdict(person_dc) == { 'name'   : 'Bob'                     ,              # Verify dict structure
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

        team_dc = self.converter.convert_instance(team)                                   # Convert to dataclass

        assert is_dataclass(team_dc)                                                      # Verify dataclass
        assert team_dc.name              == "Development"                                 # Verify list conversion
        assert len(team_dc.members)      == 2
        assert is_dataclass(team_dc.members[0])                                           # Items are dataclasses
        assert team_dc.members[0].name   == "Alice"
        assert team_dc.members[0].role   == "Lead"
        assert team_dc.members[1].name   == "Bob"
        assert team_dc.tags              == ["python", "backend"]

    def test__dict_conversion(self):                                                      # Test Dict fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        class Config(Type_Safe):
            settings : Dict[str, str]
            values   : Dict[str, int]

        config = Config(settings = {"env": "prod", "region": "us-east"} ,                 # Create Type_Safe with dicts
                       values   = {"timeout": 30, "retries": 3}        )

        config_dc = self.converter.convert_instance(config)                               # Convert to dataclass

        assert is_dataclass(config_dc)                                                    # Verify dataclass
        assert config_dc.settings == {"env": "prod", "region": "us-east"}                 # Verify dict conversion
        assert config_dc.values   == {"timeout": 30, "retries": 3}

    def test__optional_and_union_types(self):                                            # Test Optional and Union types
        class FlexibleClass(Type_Safe):
            optional    : Optional[int]    = None
            union_field : Union[str, int] = "default"
            required    : str

        instance1 = FlexibleClass(required="test")                                        # Test with optional None
        dc1       = self.converter.convert_instance(instance1)
        assert dc1.optional    is None
        assert dc1.union_field == "default"

        instance2 = FlexibleClass(required="test", optional=42, union_field=100)          # Test with values set
        dc2       = self.converter.convert_instance(instance2)
        assert dc2.optional    == 42
        assert dc2.union_field == 100

    def test__caching(self):                                                              # Test class conversion caching
        class CachedClass(Type_Safe):
            value : str

        class1 = self.converter.convert_class(CachedClass)                                # First conversion
        class2 = self.converter.convert_class(CachedClass)                                # Second should return cached

        assert class1 is class2                                                           # Should be same class
        assert CachedClass in self.converter.class_cache                                  # Verify cache contains class

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

        customer_dc = self.converter.convert_instance(customer)                           # Convert to dataclass

        assert is_dataclass(customer_dc)                                                  # Verify complex structure
        assert customer_dc.name                         == "John"
        assert len(customer_dc.orders)                  == 1
        assert is_dataclass(customer_dc.orders[0])                                        # Nested are dataclasses
        assert customer_dc.orders[0].order_id           == "001"
        assert len(customer_dc.orders[0].items)         == 2
        assert is_dataclass(customer_dc.orders[0].items[0])
        assert customer_dc.orders[0].items[0].name      == "Widget"
        assert customer_dc.orders[0].items[0].price     == 9.99
        assert customer_dc.orders[0].metadata["source"] == "web"

    def test__dataclass_equality(self):                                                   # Test dataclass equality works
        class EqualClass(Type_Safe):
            value : int
            name  : str

        instance1 = EqualClass(value=42, name="test")
        instance2 = EqualClass(value=42, name="test")
        instance3 = EqualClass(value=43, name="test")

        dc1 = self.converter.convert_instance(instance1)
        dc2 = self.converter.convert_instance(instance2)
        dc3 = self.converter.convert_instance(instance3)

        assert dc1 == dc2                                                                 # Equal values = equal
        assert dc1 != dc3                                                                 # Different values = not equal

    def test__convert_class__check_type_validation(self):                                 # Test type validation
        expected_error = "Parameter 'type_safe_class' expected a type class but got <class 'str'>"
        with pytest.raises(ValueError, match=expected_error):
            self.converter.convert_class('not_a_class')                                   # Should fail

        class SimpleClass(Type_Safe):
            value : str

        expected_error = "Parameter 'type_safe_class' expected a type class but got"
        with pytest.raises(ValueError, match=expected_error):
            self.converter.convert_class(SimpleClass())                                   # Instance, not class

    def test__convert_instance__check_type_validation(self):                              # Test instance validation
        expected_error = "Parameter 'type_safe_instance' expected type <class 'osbot_utils.type_safe.Type_Safe.Type_Safe'>, but got <class 'str'>"
        with pytest.raises(ValueError, match=re.escape(expected_error)):
            self.converter.convert_instance('not_type_safe')                              # Should fail

        class SimpleClass(Type_Safe):
            value : str

        expected_error = "Parameter 'type_safe_instance' expected type <class 'osbot_utils.type_safe.Type_Safe.Type_Safe'>, but got <class 'type'>"
        with pytest.raises(ValueError, match=re.escape(expected_error)):
            self.converter.convert_instance(SimpleClass)                                  # Class, not instance

    def test__singleton_instance(self):                                                   # Test singleton works
        class TestClass(Type_Safe):
            value : int

        DataclassType = type_safe__to__dataclass.convert_class(TestClass)                 # Use singleton
        instance = DataclassType(value=42)
        assert instance.value == 42
        assert is_dataclass(instance)

    def test__empty_collections(self):                                                    # Test empty collection handling
        class EmptyClass(Type_Safe):
            empty_list : List[str]
            empty_dict : Dict[str, int]
            empty_set  : Set[str]

        instance = EmptyClass()
        dc       = self.converter.convert_instance(instance)

        assert is_dataclass(dc)
        assert dc.empty_list == []
        assert dc.empty_dict == {}
        assert dc.empty_set  != set()                                                   # todo: see if this is a bug (or a side effect of the dual set conversion)
        assert dc.empty_set  == []                                                      # todo: see if this is a bug (or a side effect of the dual set conversion)