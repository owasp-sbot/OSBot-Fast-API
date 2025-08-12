import sys
import pytest
from dataclasses                                                import dataclass, field, is_dataclass
from typing                                                     import List, Dict, Optional, Union, Set
from unittest                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                            import Type_Safe
from osbot_fast_api.utils.type_safe.Dataclass__To__Type_Safe    import Dataclass__To__Type_Safe, dataclass__to__type_safe
from osbot_fast_api.utils.type_safe.Type_Safe__To__Dataclass    import type_safe__to__dataclass


class test_Dataclass__To__Type_Safe(TestCase):

    def setUp(self):                                                                      # Initialize test environment
        self.converter = Dataclass__To__Type_Safe()
        self.converter.class_cache.clear()                                                # Clear cache for clean tests

    def test__simple_conversion(self):                                                    # Test simple dataclass to Type_Safe
        @dataclass
        class SimpleDataclass:
            name   : str
            age    : int
            active : bool = True

        TypeSafeClass = self.converter.convert_class(SimpleDataclass)                     # Convert class

        assert issubclass(TypeSafeClass, Type_Safe)                                       # Verify it's a Type_Safe subclass
        assert TypeSafeClass.__name__ == "SimpleDataclass__Type_Safe"

        instance = TypeSafeClass(name="John", age=30)                                     # Create instance and verify fields
        assert instance.name   == "John"
        assert instance.age    == 30
        assert instance.active == True                                                    # Default value preserved

    def test__instance_conversion(self):                                                  # Test dataclass instance conversion
        @dataclass
        class PersonDataclass:
            name  : str
            age   : int
            email : Optional[str] = None

        person_dc  = PersonDataclass(name="Alice", age=25, email="alice@example.com")     # Create dataclass instance
        type_safe  = self.converter.convert_instance(person_dc)                           # Convert to Type_Safe

        assert isinstance(type_safe, Type_Safe)                                           # Verify conversion
        assert type_safe.name  == "Alice"
        assert type_safe.age   == 25
        assert type_safe.email == "alice@example.com"

        type_safe_dict = type_safe.json()                                                 # Verify Type_Safe methods work
        assert type_safe_dict == {'name': 'Alice', 'age': 25, 'email': 'alice@example.com'}

    def test__nested_dataclass_classes(self):                                             # Test nested dataclass classes
        @dataclass
        class AddressDataclass:
            street   : str
            city     : str
            zip_code : str

        @dataclass
        class PersonDataclass:
            name    : str
            address : AddressDataclass

        address_dc = AddressDataclass(street="123 Main St", city="Boston", zip_code="02101")
        person_dc  = PersonDataclass(name="Bob", address=address_dc)                      # Create nested dataclass

        type_safe = self.converter.convert_instance(person_dc)                            # Convert to Type_Safe

        assert isinstance(type_safe, Type_Safe)                                           # Verify Type_Safe structure
        assert type_safe.name == "Bob"
        assert isinstance(type_safe.address, Type_Safe)                                   # Nested is also Type_Safe
        assert type_safe.address.street   == "123 Main St"
        assert type_safe.address.city     == "Boston"
        assert type_safe.address.zip_code == "02101"

        assert type_safe.json() == { 'name'   : 'Bob'                     ,               # Verify JSON structure
                                     'address' : { 'street'   : '123 Main St' ,
                                                 'city'     : 'Boston'       ,
                                                 'zip_code' : '02101'        }}

    def test__list_conversion(self):                                                      # Test List fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        @dataclass
        class TeamMemberDataclass:
            name : str
            role : str

        @dataclass
        class TeamDataclass:
            name    : str
            members : List[TeamMemberDataclass]
            tags    : List[str]

        team_dc = TeamDataclass(name    = "Development"                                 , # Create dataclass with lists
                               members = [ TeamMemberDataclass(name="Alice", role="Lead")     ,
                                         TeamMemberDataclass(name="Bob", role="Developer")   ],
                               tags    = ["python", "backend"]                                )

        type_safe = self.converter.convert_instance(team_dc)                              # Convert to Type_Safe

        assert isinstance(type_safe, Type_Safe)                                           # Verify Type_Safe
        assert type_safe.name              == "Development"                               # Verify list conversion
        assert len(type_safe.members)      == 2
        assert type_safe.members[0].name   == "Alice"
        assert type_safe.members[0].role   == "Lead"
        assert type_safe.members[1].name   == "Bob"
        assert type_safe.tags              == ["python", "backend"]

    def test__dict_conversion(self):                                                      # Test Dict fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        @dataclass
        class ConfigDataclass:
            settings : Dict[str, str]
            values   : Dict[str, int]

        config_dc = ConfigDataclass(settings = {"env": "prod", "region": "us-east"} ,     # Create dataclass with dicts
                                   values   = {"timeout": 30, "retries": 3}        )

        type_safe = self.converter.convert_instance(config_dc)                            # Convert to Type_Safe

        assert isinstance(type_safe, Type_Safe)                                           # Verify Type_Safe
        assert type_safe.settings == {"env": "prod", "region": "us-east"}                 # Verify dict conversion
        assert type_safe.values   == {"timeout": 30, "retries": 3}

    def test__set_conversion(self):                                                       # Test Set fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        @dataclass
        class TagsDataclass:
            required_tags : Set[str]
            optional_tags : Optional[Set[str]] = None

        tags_dc = TagsDataclass(required_tags = {"python", "backend", "api"}  ,           # Create dataclass with sets
                               optional_tags = {"testing", "documentation"}  )

        type_safe = self.converter.convert_instance(tags_dc)                              # Convert to Type_Safe

        assert isinstance(type_safe, Type_Safe)                                           # Verify Type_Safe
        assert type_safe.required_tags == {"python", "backend", "api"}                    # Verify set conversion
        assert type_safe.optional_tags == {"testing", "documentation"}

    def test__optional_and_union_types(self):                                            # Test Optional and Union types
        @dataclass
        class FlexibleDataclass:
            required    : str
            optional    : Optional[int]    = None
            union_field : Union[str, int] = "default"

        dc1       = FlexibleDataclass(required="test")                                    # Test with optional None
        type_safe1 = self.converter.convert_instance(dc1)
        assert type_safe1.optional    is None
        assert type_safe1.union_field == "default"

        dc2       = FlexibleDataclass(required="test", optional=42, union_field=100)      # Test with values set
        type_safe2 = self.converter.convert_instance(dc2)
        assert type_safe2.optional    == 42
        assert type_safe2.union_field == 100

    def test__field_with_default_factory(self):                                           # Test fields with default_factory
        @dataclass
        class DataclassWithFactory:
            id    : str
            items : List[str] = field(default_factory=list)
            config: Dict[str, str] = field(default_factory=lambda: {"debug": "false"})

        dc        = DataclassWithFactory(id="test")                                       # Create with defaults
        type_safe = self.converter.convert_instance(dc)

        assert isinstance(type_safe, Type_Safe)                                           # Verify Type_Safe
        assert type_safe.id     == "test"
        assert type_safe.items  == []                                                     # Default factory worked
        assert type_safe.config == {"debug": "false"}                                     # Lambda factory worked

    def test__caching(self):                                                              # Test class conversion caching
        @dataclass
        class CachedDataclass:
            value : str

        class1 = self.converter.convert_class(CachedDataclass)                            # First conversion
        class2 = self.converter.convert_class(CachedDataclass)                            # Second should return cached

        assert class1 is class2                                                           # Should be same class
        assert CachedDataclass in self.converter.class_cache                              # Verify cache contains class

    def test__round_trip_conversion(self):                                                # Test Type_Safe → Dataclass → Type_Safe
        class OriginalClass(Type_Safe):
            name    : str
            age     : int
            scores  : List[float]
            metadata: Dict[str, str]

        original = OriginalClass(name     = "Test"              ,                         # Create original Type_Safe
                                age      = 30                   ,
                                scores   = [95.5, 87.3, 92.0]   ,
                                metadata = {"level": "advanced"} )

        dataclass_obj     = type_safe__to__dataclass.convert_instance(original)           # Convert to dataclass
        back_to_type_safe = self.converter.convert_instance(dataclass_obj)                # Convert back to Type_Safe

        assert back_to_type_safe.json() == original.json()                                # Verify round-trip fidelity

    def test__complex_nested_structure(self):                                             # Test complex nested structures
        @dataclass
        class ItemDataclass:
            id    : str
            name  : str
            price : float

        @dataclass
        class OrderDataclass:
            order_id : str
            items    : List[ItemDataclass]
            metadata : Dict[str, str]

        @dataclass
        class CustomerDataclass:
            name   : str
            orders : List[OrderDataclass]

        customer_dc = CustomerDataclass(                                                  # Create complex dataclass
            name   = "John",
            orders = [ OrderDataclass(order_id = "001"                              ,
                                    items    = [ ItemDataclass(id="1", name="Widget", price=9.99)   ,
                                               ItemDataclass(id="2", name="Gadget", price=19.99)  ],
                                    metadata = {"source": "web", "priority": "high"}                )]
        )

        type_safe = self.converter.convert_instance(customer_dc)                          # Convert to Type_Safe

        assert isinstance(type_safe, Type_Safe)                                           # Verify complex structure
        assert type_safe.name                         == "John"
        assert len(type_safe.orders)                  == 1
        assert type_safe.orders[0].order_id           == "001"
        assert len(type_safe.orders[0].items)         == 2
        assert type_safe.orders[0].items[0].name      == "Widget"
        assert type_safe.orders[0].items[0].price     == 9.99
        assert type_safe.orders[0].metadata["source"] == "web"

    def test__convert_class__check_type_validation(self):                                 # Test type validation
        expected_error = "Parameter 'dataclass_type' expected a type class but got <class 'str'>"
        with pytest.raises(ValueError, match=expected_error):
            self.converter.convert_class('not_a_dataclass')                               # Should fail

        class NotADataclass:
            value : str

        expected_error = "Expected a dataclass, but got"
        with pytest.raises(ValueError, match=expected_error):
            self.converter.convert_class(NotADataclass)                                   # Regular class, not dataclass

    def test__convert_instance__check_type_validation(self):                              # Test instance validation
        expected_error = "Expected a dataclass instance, but got <class 'str'>"
        with pytest.raises(ValueError, match=expected_error):
            self.converter.convert_instance('not_a_dataclass')                            # Should fail

        @dataclass
        class SimpleDataclass:
            value : str

        expected_error = "Expected a dataclass, but got <class 'type'>"
        with pytest.raises(ValueError, match=expected_error):
            self.converter.convert_instance(SimpleDataclass)                              # Class, not instance

    def test__singleton_instance(self):                                                   # Test singleton works
        @dataclass
        class TestDataclass:
            value : int

        TypeSafeClass = dataclass__to__type_safe.convert_class(TestDataclass)             # Use singleton
        instance = TypeSafeClass(value=42)
        assert instance.value == 42
        assert isinstance(instance, Type_Safe)

    def test__empty_collections(self):                                                    # Test empty collection handling
        @dataclass
        class EmptyDataclass:
            empty_list : List[str]     = field(default_factory=list)
            empty_dict : Dict[str, int] = field(default_factory=dict)
            empty_set  : Set[str]       = field(default_factory=set)

        dc        = EmptyDataclass()
        type_safe = self.converter.convert_instance(dc)

        assert isinstance(type_safe, Type_Safe)
        assert type_safe.empty_list == []
        assert type_safe.empty_dict == {}
        assert type_safe.empty_set  == set()