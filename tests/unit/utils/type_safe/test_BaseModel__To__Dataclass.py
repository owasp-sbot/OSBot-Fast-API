import re
import sys
import pytest
from dataclasses import fields, is_dataclass, asdict, MISSING
from typing                                                  import List, Dict, Optional, Union, Set
from unittest                                                import TestCase
from pydantic                                                import BaseModel, Field
from osbot_fast_api.utils.type_safe.BaseModel__To__Dataclass import BaseModel__To__Dataclass, basemodel__to__dataclass


class test_BaseModel__To__Dataclass(TestCase):

    def setUp(self):                                                                      # Initialize test environment
        self.converter = BaseModel__To__Dataclass()
        self.converter.class_cache.clear()                                                # Clear cache for clean tests

    def test__simple_conversion(self):                                                    # Test simple BaseModel to dataclass
        class SimpleModel(BaseModel):
            name   : str
            age    : int
            active : bool = True

        DataclassType = self.converter.convert_class(SimpleModel)                         # Convert class

        assert is_dataclass(DataclassType)                                                # Verify it's a dataclass
        assert DataclassType.__name__ == "SimpleModel__Dataclass"

        instance = DataclassType(name="John", age=30)                                     # Create instance and verify fields
        assert instance.name   == "John"
        assert instance.age    == 30
        assert instance.active == True                                                    # Default value preserved

        # Verify dataclass features work
        assert asdict(instance) == {'name': 'John', 'age': 30, 'active': True}
        assert repr(instance)   == "SimpleModel__Dataclass(name='John', age=30, active=True)"

    def test__instance_conversion(self):                                                  # Test BaseModel instance conversion
        class PersonModel(BaseModel):
            name  : str
            age   : int
            email : Optional[str] = None

        person_model = PersonModel(name="Alice", age=25, email="alice@example.com")       # Create BaseModel instance
        person_dc    = self.converter.convert_instance(person_model)                      # Convert to dataclass

        assert is_dataclass(person_dc)                                                    # Verify it's a dataclass instance
        assert person_dc.name  == "Alice"
        assert person_dc.age   == 25
        assert person_dc.email == "alice@example.com"

        person_dict = asdict(person_dc)                                                   # Verify dataclass methods work
        assert person_dict == {'name': 'Alice', 'age': 25, 'email': 'alice@example.com'}

    def test__nested_basemodel_classes(self):                                             # Test nested BaseModel classes
        class AddressModel(BaseModel):
            street   : str
            city     : str
            zip_code : str

        class PersonModel(BaseModel):
            name    : str
            address : AddressModel

        address_model = AddressModel(street="123 Main St", city="Boston", zip_code="02101")
        person_model  = PersonModel(name="Bob", address=address_model)                    # Create nested BaseModel

        person_dc = self.converter.convert_instance(person_model)                         # Convert to dataclass

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

        class TeamMemberModel(BaseModel):
            name : str
            role : str

        class TeamModel(BaseModel):
            name    : str
            members : List[TeamMemberModel]
            tags    : List[str]

        team_model = TeamModel(name    = "Development"                                ,   # Create BaseModel with lists
                              members = [ TeamMemberModel(name="Alice", role="Lead")    ,
                                        TeamMemberModel(name="Bob", role="Developer")  ],
                              tags    = ["python", "backend"]                          )

        team_dc = self.converter.convert_instance(team_model)                             # Convert to dataclass

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

        class ConfigModel(BaseModel):
            settings : Dict[str, str]
            values   : Dict[str, int]

        config_model = ConfigModel(settings = {"env": "prod", "region": "us-east"} ,      # Create BaseModel with dicts
                                  values   = {"timeout": 30, "retries": 3}        )

        config_dc = self.converter.convert_instance(config_model)                         # Convert to dataclass

        assert is_dataclass(config_dc)                                                    # Verify dataclass
        assert config_dc.settings == {"env": "prod", "region": "us-east"}                 # Verify dict conversion
        assert config_dc.values   == {"timeout": 30, "retries": 3}

    def test__set_conversion(self):                                                       # Test Set fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        class TagsModel(BaseModel):
            required_tags : Set[str]
            optional_tags : Optional[Set[str]] = None

        tags_model = TagsModel(required_tags = {"python", "backend", "api"}  ,            # Create BaseModel with sets
                              optional_tags = {"testing", "documentation"}  )

        tags_dc = self.converter.convert_instance(tags_model)                             # Convert to dataclass

        assert is_dataclass(tags_dc)                                                      # Verify dataclass
        assert tags_dc.required_tags == {"python", "backend", "api"}                      # Verify set conversion
        assert tags_dc.optional_tags == {"testing", "documentation"}

    def test__optional_and_union_types(self):                                            # Test Optional and Union types
        class FlexibleModel(BaseModel):
            required    : str
            optional    : Optional[int]    = None
            union_field : Union[str, int] = "default"

        model1 = FlexibleModel(required="test")                                           # Test with optional None
        dc1    = self.converter.convert_instance(model1)
        assert dc1.optional    is None
        assert dc1.union_field == "default"

        model2 = FlexibleModel(required="test", optional=42, union_field=100)             # Test with values set
        dc2    = self.converter.convert_instance(model2)
        assert dc2.optional    == 42
        assert dc2.union_field == 100

    def test__field_with_default_factory(self):                                           # Test fields with default_factory
        class ModelWithFactory(BaseModel):
            id    : str
            items : List[str] = Field(default_factory=list)
            config: Dict[str, str] = Field(default_factory=lambda: {"debug": "false"})

        model = ModelWithFactory(id="test")                                               # Create with defaults
        dc    = self.converter.convert_instance(model)

        assert is_dataclass(dc)                                                           # Verify dataclass
        assert dc.id     == "test"
        assert dc.items  == []                                                            # Default factory worked
        assert dc.config == {"debug": "false"}                                            # Lambda factory worked

        # Verify dataclass field has default_factory
        field_map = {f.name: f for f in fields(dc)}
        assert field_map['items'].default_factory is not MISSING                          # Has factory

    def test__caching(self):                                                              # Test class conversion caching
        class CachedModel(BaseModel):
            value : str

        class1 = self.converter.convert_class(CachedModel)                                # First conversion
        class2 = self.converter.convert_class(CachedModel)                                # Second should return cached

        assert class1 is class2                                                           # Should be same class
        assert CachedModel in self.converter.class_cache                                  # Verify cache contains class

    def test__complex_nested_structure(self):                                             # Test complex nested structures
        class ItemModel(BaseModel):
            id    : str
            name  : str
            price : float

        class OrderModel(BaseModel):
            order_id : str
            items    : List[ItemModel]
            metadata : Dict[str, str]

        class CustomerModel(BaseModel):
            name   : str
            orders : List[OrderModel]

        customer_model = CustomerModel(                                                   # Create complex BaseModel
            name   = "John",
            orders = [ OrderModel(order_id = "001"                              ,
                                items    = [ ItemModel(id="1", name="Widget", price=9.99)   ,
                                           ItemModel(id="2", name="Gadget", price=19.99)  ],
                                metadata = {"source": "web", "priority": "high"}           )]
        )

        customer_dc = self.converter.convert_instance(customer_model)                     # Convert to dataclass

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
        class EqualModel(BaseModel):
            value : int
            name  : str

        model1 = EqualModel(value=42, name="test")
        model2 = EqualModel(value=42, name="test")
        model3 = EqualModel(value=43, name="test")

        dc1 = self.converter.convert_instance(model1)
        dc2 = self.converter.convert_instance(model2)
        dc3 = self.converter.convert_instance(model3)

        assert dc1 == dc2                                                                 # Equal values = equal
        assert dc1 != dc3                                                                 # Different values = not equal

    def test__convert_class__check_type_validation(self):                                 # Test type validation
        expected_error = "Parameter 'basemodel_class' expected a type class but got <class 'str'>"
        with pytest.raises(ValueError, match=expected_error):
            self.converter.convert_class('not_a_class')                                   # Should fail

        class SimpleModel(BaseModel):
            value : str

        expected_error = "Parameter 'basemodel_class' expected a type class but got"
        with pytest.raises(ValueError, match=expected_error):
            self.converter.convert_class(SimpleModel(value='abc'))                                   # Instance, not class

    def test__convert_instance__check_type_validation(self):                              # Test instance validation
        expected_error = "Parameter 'basemodel_instance' expected type <class 'pydantic.main.BaseModel'>, but got <class 'str'>"
        with pytest.raises(ValueError, match=re.escape(expected_error)):
            self.converter.convert_instance('not_a_model')                                # Should fail

        class SimpleModel(BaseModel):
            value : str

        expected_error = "Parameter 'basemodel_instance' expected type <class 'pydantic.main.BaseModel'>, but got <class 'pydantic._internal._model_construction.ModelMetaclass'>"
        with pytest.raises(ValueError, match=re.escape(expected_error)):
            self.converter.convert_instance(SimpleModel)                                  # Class, not instance

    def test__singleton_instance(self):                                                   # Test singleton works
        class TestModel(BaseModel):
            value : int

        DataclassType = basemodel__to__dataclass.convert_class(TestModel)                 # Use singleton
        instance = DataclassType(value=42)
        assert instance.value == 42
        assert is_dataclass(instance)

    def test__empty_collections(self):                                                    # Test empty collection handling
        class EmptyModel(BaseModel):
            empty_list : List[str]      = []
            empty_dict : Dict[str, int] = {}
            empty_set  : Set[str]       = set()

        model = EmptyModel()
        dc    = self.converter.convert_instance(model)

        assert is_dataclass(dc)
        assert dc.empty_list == []
        assert dc.empty_dict == {}
        assert dc.empty_set  == set()

    def test__pydantic_to_dataclass_field_mapping(self):                                  # Test field metadata preserved
        class ConstrainedModel(BaseModel):
            name  : str = Field(..., min_length=3, max_length=50)
            age   : int = Field(..., ge=0, le=150)
            email : str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

        DataclassType = self.converter.convert_class(ConstrainedModel)

        # Verify fields exist (constraints not preserved in basic dataclass)
        field_names = {f.name for f in fields(DataclassType)}
        assert field_names == {'name', 'age', 'email'}

        # Can still create instances
        instance = DataclassType(name="John", age=30, email="john@example.com")
        assert instance.name  == "John"
        assert instance.age   == 30
        assert instance.email == "john@example.com"