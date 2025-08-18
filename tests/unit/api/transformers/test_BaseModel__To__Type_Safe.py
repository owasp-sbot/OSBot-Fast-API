import re
import sys
import pytest
from typing                                                      import List, Dict, Optional, Union, Set, Any
from unittest                                                    import TestCase
from osbot_utils.utils.Objects                                   import __
from pydantic                                                    import BaseModel, Field
from osbot_utils.type_safe.Type_Safe                             import Type_Safe
from osbot_fast_api.api.transformers.BaseModel__To__Type_Safe     import BaseModel__To__Type_Safe, basemodel__to__type_safe
from osbot_fast_api.api.transformers.Type_Safe__To__BaseModel     import type_safe__to__basemodel


class test_BaseModel__To__Type_Safe(TestCase):

    def setUp(self):                                                                      # Initialize test environment
        self.converter = BaseModel__To__Type_Safe()
        self.converter.class_cache.clear()                                                # Clear cache for clean tests

    def test__simple_conversion(self):                                                    # Test simple BaseModel to Type_Safe
        class SimpleModel(BaseModel):
            name   : str
            age    : int
            active : bool = True

        TypeSafeClass = self.converter.convert_class(SimpleModel)                         # Convert class

        assert issubclass(TypeSafeClass, Type_Safe)                                       # Verify it's a Type_Safe subclass
        assert TypeSafeClass.__name__ == "SimpleModel__Type_Safe"

        instance = TypeSafeClass(name="John", age=30)                                     # Create instance and verify fields
        assert instance.name   == "John"
        assert instance.age    == 30
        assert instance.active == True                                                    # Default value preserved
        assert instance.json() == {'active': True, 'age': 30, 'name': 'John'}
        assert instance.obj () == __(active=True, name='John', age=30)
        assert instance.json() == SimpleModel(name="John", age=30).model_dump()           # confirm full compatibility between the two data types

    def test__instance_conversion(self):                                                  # Test BaseModel instance conversion
        class PersonModel(BaseModel):
            name  : str
            age   : int
            email : Optional[str] = None

        person_model = PersonModel(name="Alice", age=25, email="alice@example.com")       # Create BaseModel instance
        type_safe    = self.converter.convert_instance(person_model)                      # Convert to Type_Safe

        assert isinstance(type_safe, Type_Safe)                                           # Verify conversion
        assert type_safe.name  == "Alice"
        assert type_safe.age   == 25
        assert type_safe.email == "alice@example.com"

        type_safe_dict = type_safe.json()                                                 # Verify Type_Safe methods work
        assert type_safe_dict == {'name': 'Alice', 'age': 25, 'email': 'alice@example.com'}
        assert type_safe_dict == person_model.model_dump()

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

        type_safe = self.converter.convert_instance(person_model)                         # Convert to Type_Safe

        assert type_safe.name == "Bob"                                                    # Verify nested structure
        assert type_safe.address.street   == "123 Main St"
        assert type_safe.address.city     == "Boston"
        assert type_safe.address.zip_code == "02101"

        assert type_safe.json() == { 'name'    : 'Bob'                        ,           # Verify JSON structure
                                     'address' : { 'street'   : '123 Main St' ,
                                                   'city'     : 'Boston'      ,
                                                   'zip_code' : '02101'       }}

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

        type_safe = self.converter.convert_instance(team_model)                           # Convert to Type_Safe

        assert type_safe.name              == "Development"                               # Verify list conversion
        assert len(type_safe.members)      == 2
        assert type_safe.members[0].name   == "Alice"
        assert type_safe.members[0].role   == "Lead"
        assert type_safe.members[1].name   == "Bob"
        assert type_safe.tags              == [ "python", "backend"]
        assert type_safe.json()            == { 'members': [ {'name' : 'Alice', 'role': 'Lead'      },
                                                             {'name' : 'Bob'  , 'role': 'Developer'}],
                                                'name'   : 'Development',
                                                'tags'   : ['python', 'backend']}
        assert type_safe.obj()             == __(name    = 'Development',
                                                 members =  [__(name='Alice', role='Lead'     ),
                                                             __(name='Bob'  , role='Developer')],
                                                 tags    = ['python', 'backend' ])

    def test__dict_conversion(self):                                                      # Test Dict fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        class ConfigModel(BaseModel):
            settings : Dict[str, str]
            values   : Dict[str, int]

        config_model = ConfigModel(settings = {"env": "prod", "region": "us-east"} ,      # Create BaseModel with dicts
                                  values   = {"timeout": 30, "retries": 3}        )

        type_safe = self.converter.convert_instance(config_model)                         # Convert to Type_Safe

        assert type_safe.settings == {"env": "prod", "region": "us-east"}                 # Verify dict conversion
        assert type_safe.values   == {"timeout": 30, "retries": 3}

    def test__set_conversion(self):                                                       # Test Set fields conversion
        if sys.version_info < (3, 10):
            pytest.skip("Skipping test that doesn't work on 3.9 or lower")

        class TagsModel(BaseModel):
            required_tags : Set[str]
            optional_tags : Optional[Set[str]] = None

        tags_model = TagsModel(required_tags = {"python", "backend", "api"}  ,            # Create BaseModel with sets
                               optional_tags = {"testing", "documentation"}  )

        type_safe = self.converter.convert_instance(tags_model)                           # Convert to Type_Safe

        assert type_safe.required_tags == {"python", "backend", "api"}                    # Verify set conversion
        assert type_safe.optional_tags == {"testing", "documentation"}

    def test__optional_and_union_types(self):                                            # Test Optional and Union types
        class FlexibleModel(BaseModel):
            required    : str
            optional    : Optional[int]    = None
            union_field : Union[str, int] = "default"

        model1    = FlexibleModel(required="test")                                        # Test with optional None
        type_safe1 = self.converter.convert_instance(model1)
        assert type_safe1.optional    is None
        assert type_safe1.union_field == "default"

        model2    = FlexibleModel(required="test", optional=42, union_field=100)          # Test with values set
        type_safe2 = self.converter.convert_instance(model2)
        assert type_safe2.optional    == 42
        assert type_safe2.union_field == 100

    def test__caching(self):                                                              # Test class conversion caching
        class CachedModel(BaseModel):
            value : str

        class1 = self.converter.convert_class(CachedModel)                                # First conversion
        class2 = self.converter.convert_class(CachedModel)                                # Second should return cached

        assert class1 is class2                                                           # Should be same class
        assert CachedModel in self.converter.class_cache                                  # Verify cache contains class

    def test__round_trip_conversion(self):                                                # Test Type_Safe → BaseModel → Type_Safe
        class OriginalClass(Type_Safe):
            name    : str
            age     : int
            scores  : List[float]
            metadata: Dict[str, str]

        original = OriginalClass(name     = "Test"              ,                         # Create original Type_Safe
                                 age      = 30                   ,
                                 scores   = [95.5, 87.3, 92.0]   ,
                                 metadata = {"level": "advanced"} )

        base_model = type_safe__to__basemodel.convert_instance(original)                  # Convert to BaseModel
        back_to_type_safe = self.converter.convert_instance(base_model)                   # Convert back to Type_Safe

        assert back_to_type_safe.json() == original.json()                                # Verify round-trip fidelity

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

        type_safe = self.converter.convert_instance(customer_model)                       # Convert to Type_Safe

        assert type_safe.name                         == "John"                           # Verify complex structure
        assert len(type_safe.orders)                  == 1
        assert type_safe.orders[0].order_id           == "001"
        assert len(type_safe.orders[0].items)         == 2
        assert type_safe.orders[0].items[0].name      == "Widget"
        assert type_safe.orders[0].items[0].price     == 9.99
        assert type_safe.orders[0].metadata["source"] == "web"
        assert type_safe.obj()                        == __(name='John',
                                                            orders=[__(order_id='001',
                                                                       items=[__(id='1', name='Widget', price=9.99),
                                                                              __(id='2', name='Gadget', price=19.99)],
                                                                       metadata=__(source='web', priority='high'))])
        assert type_safe.json() == customer_model.model_dump()

    def test__field_with_default_factory(self):                                           # Test fields with default_factory
        class ModelWithFactory(BaseModel):
            id    : str
            items : List[str] = Field(default_factory=list)
            config: Dict[str, Any] = Field(default_factory=lambda: {"debug": False})

        model = ModelWithFactory(id="test")                                               # Create with defaults
        type_safe = self.converter.convert_instance(model)

        assert type_safe.id     == "test"
        assert type_safe.items  == []                                                     # Default factory worked
        assert type_safe.config == {"debug": False}                                       # Lambda factory worked

    def test__pydantic_field_info_handling(self):                                         # Test Pydantic Field metadata
        class ConstrainedModel(BaseModel):
            name     : str = Field(..., min_length=3, max_length=50)
            age      : int = Field(..., ge=0, le=150)
            email    : str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

        model = ConstrainedModel(name="John", age=30, email="john@example.com")
        type_safe = self.converter.convert_instance(model)

        assert type_safe.name  == "John"                                                  # Values preserved
        assert type_safe.age   == 30
        assert type_safe.email == "john@example.com"

        # Note: Constraints are not preserved in Type_Safe (by design)
        assert type_safe.obj() == __(name='John', age=30, email='john@example.com')


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

        TypeSafeClass = basemodel__to__type_safe.convert_class(TestModel)                 # Use singleton
        instance = TypeSafeClass(value=42)
        assert instance.value == 42

    def test__model_dump_compatibility(self):                                             # Test model_dump handling
        class DumpModel(BaseModel):
            data : Dict[str, Any]

        model = DumpModel(data={"key": "value", "number": 123})
        type_safe = self.converter.convert_instance(model)

        assert type_safe.data == {"key": "value", "number": 123}
        assert type_safe.json() == model.model_dump()                                     # Same structure

    def test__empty_collections(self):                                                    # Test empty collection handling
        class EmptyModel(BaseModel):
            empty_list : List[str]     = []
            empty_dict : Dict[str, int] = {}
            empty_set  : Set[str]       = set()

        model = EmptyModel()
        type_safe = self.converter.convert_instance(model)

        assert type_safe.empty_list == []
        assert type_safe.empty_dict == {}
        assert type_safe.empty_set  == set()