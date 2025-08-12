import sys
import pytest
from dataclasses                                             import dataclass, field
from typing                                                  import List, Dict, Optional, Union, Set
from unittest                                                import TestCase
from pydantic                                                import BaseModel, ValidationError
from osbot_fast_api.utils.type_safe.BaseModel__To__Dataclass import basemodel__to__dataclass
from osbot_fast_api.utils.type_safe.Dataclass__To__BaseModel import Dataclass__To__BaseModel, dataclass__to__basemodel


class test_Dataclass__To__BaseModel(TestCase):

    def setUp(self):                                                                      # Initialize test environment
        self.converter = Dataclass__To__BaseModel()
        self.converter.class_cache.clear()                                                # Clear cache for clean tests

    def test__simple_conversion(self):                                                    # Test simple dataclass to BaseModel
        @dataclass
        class SimpleDataclass:
            name   : str
            age    : int
            active : bool = True

        BaseModelClass = self.converter.convert_class(SimpleDataclass)                    # Convert class

        assert issubclass(BaseModelClass, BaseModel)                                      # Verify it's a BaseModel subclass
        assert BaseModelClass.__name__ == "SimpleDataclass__BaseModel"

        instance = BaseModelClass(name="John", age=30)                                    # Create instance and verify fields
        assert instance.name   == "John"
        assert instance.age    == 30
        assert instance.active == True                                                    # Default value preserved

        # Verify Pydantic validation works
        with pytest.raises(ValidationError):
            BaseModelClass(name="John", age="not_an_int")

    def test__instance_conversion(self):                                                  # Test dataclass instance conversion
        @dataclass
        class PersonDataclass:
            name  : str
            age   : int
            email : Optional[str] = None

        person_dc  = PersonDataclass(name="Alice", age=25, email="alice@example.com")     # Create dataclass instance
        base_model = self.converter.convert_instance(person_dc)                           # Convert to BaseModel

        assert isinstance(base_model, BaseModel)                                          # Verify conversion
        assert base_model.name  == "Alice"
        assert base_model.age   == 25
        assert base_model.email == "alice@example.com"

        model_dict = base_model.model_dump()                                              # Verify BaseModel methods work
        assert model_dict == {'name': 'Alice', 'age': 25, 'email': 'alice@example.com'}

        model_json = base_model.model_dump_json()
        assert model_json == '{"name":"Alice","age":25,"email":"alice@example.com"}'

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

        base_model = self.converter.convert_instance(person_dc)                           # Convert to BaseModel

        assert isinstance(base_model, BaseModel)                                          # Verify BaseModel structure
        assert base_model.name == "Bob"
        assert base_model.address.street   == "123 Main St"
        assert base_model.address.city     == "Boston"
        assert base_model.address.zip_code == "02101"

        assert base_model.model_dump() == { 'name'    : 'Bob'                         ,   # Verify dict structure
                                            'address' : { 'street'   : '123 Main St'  ,
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

        base_model = self.converter.convert_instance(team_dc)                             # Convert to BaseModel

        assert isinstance(base_model, BaseModel)                                          # Verify BaseModel
        assert base_model.name              == "Development"                              # Verify list conversion
        assert len(base_model.members)      == 2
        assert base_model.members[0].name   == "Alice"
        assert base_model.members[0].role   == "Lead"
        assert base_model.members[1].name   == "Bob"
        assert base_model.tags              == ["python", "backend"]

    def test__dict_conversion(self):                                                      # Test Dict fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        @dataclass
        class ConfigDataclass:
            settings : Dict[str, str]
            values   : Dict[str, int]

        config_dc = ConfigDataclass(settings = {"env": "prod", "region": "us-east"} ,     # Create dataclass with dicts
                                   values   = {"timeout": 30, "retries": 3}        )

        base_model = self.converter.convert_instance(config_dc)                           # Convert to BaseModel

        assert isinstance(base_model, BaseModel)                                          # Verify BaseModel
        assert base_model.settings == {"env": "prod", "region": "us-east"}                # Verify dict conversion
        assert base_model.values   == {"timeout": 30, "retries": 3}

    def test__set_conversion(self):                                                       # Test Set fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        @dataclass
        class TagsDataclass:
            required_tags : Set[str]
            optional_tags : Optional[Set[str]] = None

        tags_dc = TagsDataclass(required_tags = {"python", "backend", "api"}  ,           # Create dataclass with sets
                               optional_tags = {"testing", "documentation"}  )

        base_model = self.converter.convert_instance(tags_dc)                             # Convert to BaseModel

        assert isinstance(base_model, BaseModel)                                          # Verify BaseModel
        assert base_model.required_tags == {"python", "backend", "api"}                   # Verify set conversion
        assert base_model.optional_tags == {"testing", "documentation"}

    def test__optional_and_union_types(self):                                            # Test Optional and Union types
        @dataclass
        class FlexibleDataclass:
            required    : str
            optional    : Optional[int]    = None
            union_field : Union[str, int] = "default"

        dc1        = FlexibleDataclass(required="test")                                   # Test with optional None
        base_model1 = self.converter.convert_instance(dc1)
        assert base_model1.optional    is None
        assert base_model1.union_field == "default"

        dc2        = FlexibleDataclass(required="test", optional=42, union_field=100)     # Test with values set
        base_model2 = self.converter.convert_instance(dc2)
        assert base_model2.optional    == 42
        assert base_model2.union_field == 100

    def test__field_with_default_factory(self):                                           # Test fields with default_factory
        @dataclass
        class DataclassWithFactory:
            id    : str
            items : List[str] = field(default_factory=list)
            config: Dict[str, str] = field(default_factory=lambda: {"debug": "false"})

        dc = DataclassWithFactory(id="test")                                              # Create with defaults
        base_model = self.converter.convert_instance(dc)

        assert isinstance(base_model, BaseModel)                                          # Verify BaseModel
        assert base_model.id     == "test"
        assert base_model.items  == []                                                    # Default factory worked
        assert base_model.config == {"debug": "false"}                                    # Lambda factory worked

    def test__caching(self):                                                              # Test class conversion caching
        @dataclass
        class CachedDataclass:
            value : str

        class1 = self.converter.convert_class(CachedDataclass)                            # First conversion
        class2 = self.converter.convert_class(CachedDataclass)                            # Second should return cached

        assert class1 is class2                                                           # Should be same class
        assert CachedDataclass in self.converter.class_cache                              # Verify cache contains class

    def test__round_trip_conversion(self):                                                # Test BaseModel → Dataclass → BaseModel
        class OriginalModel(BaseModel):
            name    : str
            age     : int
            scores  : List[float]
            metadata: Dict[str, str]

        original = OriginalModel(name     = "Test"              ,                         # Create original BaseModel
                                age      = 30                   ,
                                scores   = [95.5, 87.3, 92.0]   ,
                                metadata = {"level": "advanced"} )

        dataclass_obj = basemodel__to__dataclass.convert_instance(original)               # Convert to dataclass
        back_to_model = self.converter.convert_instance(dataclass_obj)                    # Convert back to BaseModel

        assert back_to_model.model_dump() == original.model_dump()                        # Verify round-trip fidelity

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

        base_model = self.converter.convert_instance(customer_dc)                         # Convert to BaseModel

        assert isinstance(base_model, BaseModel)                                          # Verify complex structure
        assert base_model.name                         == "John"
        assert len(base_model.orders)                  == 1
        assert base_model.orders[0].order_id           == "001"
        assert len(base_model.orders[0].items)         == 2
        assert base_model.orders[0].items[0].name      == "Widget"
        assert base_model.orders[0].items[0].price     == 9.99
        assert base_model.orders[0].metadata["source"] == "web"

    def test__validation_errors_propagate(self):                                          # Test Pydantic validation
        @dataclass
        class ValidatedDataclass:
            email : str
            age   : int

        ModelClass = self.converter.convert_class(ValidatedDataclass)

        valid = ModelClass(email="test@example.com", age=25)                              # Valid instance
        assert valid.email == "test@example.com"
        assert valid.age   == 25

        with pytest.raises(ValidationError) as exc_info:                                  # Invalid age type
            ModelClass(email="test@example.com", age="twenty-five")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error['loc'] == ('age',) for error in errors)

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

        BaseModelClass = dataclass__to__basemodel.convert_class(TestDataclass)            # Use singleton
        instance = BaseModelClass(value=42)
        assert instance.value == 42
        assert isinstance(instance, BaseModel)

    def test__empty_collections(self):                                                    # Test empty collection handling
        @dataclass
        class EmptyDataclass:
            empty_list : List[str]     = field(default_factory=list)
            empty_dict : Dict[str, int] = field(default_factory=dict)
            empty_set  : Set[str]       = field(default_factory=set)

        dc = EmptyDataclass()
        base_model = self.converter.convert_instance(dc)

        assert isinstance(base_model, BaseModel)
        assert base_model.empty_list == []
        assert base_model.empty_dict == {}
        assert base_model.empty_set  == set()