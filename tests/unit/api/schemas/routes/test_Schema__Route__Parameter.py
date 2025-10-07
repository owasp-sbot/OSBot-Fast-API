from unittest                                                                    import TestCase
from osbot_utils.testing.__                                                      import __
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id  import Safe_Str__Id
from osbot_fast_api.api.schemas.routes.Schema__Route__Parameter                  import Schema__Route__Parameter

class test_Schema__Route__Parameter(TestCase):

    def test__init__(self):                                                         # Test parameter schema initialization
        with Schema__Route__Parameter() as _:
            assert type(_) is Schema__Route__Parameter
            assert issubclass(type(_), Type_Safe)

            assert _.obj() == __(name                    = _.name                   ,
                                 param_type              = _.param_type             ,
                                 converted_type          = None                     ,
                                 is_primitive            = False                    ,
                                 is_type_safe            = False                    ,
                                 primitive_base          = None                     ,
                                 requires_conversion     = False                    ,
                                 default_value           = None                     ,
                                 has_default             = False                    ,
                                 nested_primitive_fields = None                     )

    def test__init__with_name(self):                                                # Test initialization with parameter name
        with Schema__Route__Parameter(name=Safe_Str__Id('user_id')) as _:
            assert _.name == Safe_Str__Id('user_id')
            assert type(_.name) is Safe_Str__Id

    def test__init__primitive_parameter(self):                                      # Test initialization for primitive parameter
        with Schema__Route__Parameter(name              = Safe_Str__Id('count')    ,
                                      param_type        = int                       ,
                                      is_primitive      = True                      ,
                                      primitive_base    = int                       ,
                                      requires_conversion = True                    ) as _:
            assert _.name              == Safe_Str__Id('count')
            assert _.param_type        is int
            assert _.is_primitive      is True
            assert _.primitive_base    is int
            assert _.requires_conversion is True

    def test__init__type_safe_parameter(self):                                      # Test initialization for Type_Safe parameter
        with Schema__Route__Parameter(name                = Safe_Str__Id('data')   ,
                                      param_type          = Type_Safe               ,
                                      is_type_safe        = True                    ,
                                      requires_conversion = True                    ) as _:
            assert _.name              == Safe_Str__Id('data')
            assert _.param_type        is Type_Safe
            assert _.is_type_safe      is True
            assert _.requires_conversion is True

    def test__init__with_default(self):                                             # Test initialization with default value
        with Schema__Route__Parameter(name          = Safe_Str__Id('limit')        ,
                                      default_value = 10                            ,
                                      has_default   = True                          ) as _:
            assert _.name          == Safe_Str__Id('limit')
            assert _.default_value == 10
            assert _.has_default   is True

    def test__init__with_converted_type(self):                                      # Test initialization with converted type
        with Schema__Route__Parameter(name           = Safe_Str__Id('data')        ,
                                      param_type     = Type_Safe                    ,
                                      converted_type = dict                         ) as _:
            assert _.param_type     is Type_Safe
            assert _.converted_type is dict

    def test__init__with_nested_primitives(self):                                   # Test initialization with nested primitive fields
        nested_fields = {'name': Safe_Str__Id, 'count': int}

        with Schema__Route__Parameter(name                    = Safe_Str__Id('complex_data')  ,
                                      nested_primitive_fields = nested_fields                 ) as _:
            assert _.nested_primitive_fields is not None
            assert 'name'  in _.nested_primitive_fields
            assert 'count' in _.nested_primitive_fields

    def test_json_serialization(self):                                              # Test JSON round-trip serialization
        with Schema__Route__Parameter(name              = Safe_Str__Id('user_id')  ,
                                      param_type        = str                       ,
                                      is_primitive      = True                      ,
                                      primitive_base    = str                       ) as original:
            json_data = original.json()

            assert 'name'         in json_data
            assert 'is_primitive' in json_data

            restored = Schema__Route__Parameter.from_json(json_data)
            assert restored.name         == original.name
            assert restored.is_primitive == original.is_primitive

    def test_complete_parameter_scenario(self):                                     # Test complete parameter with all metadata
        nested_fields = {'field1': Safe_Str__Id, 'field2': int}

        with Schema__Route__Parameter(name                    = Safe_Str__Id('complex_param')  ,
                                      param_type              = Type_Safe                       ,
                                      converted_type          = dict                            ,
                                      is_primitive            = False                           ,
                                      is_type_safe            = True                            ,
                                      primitive_base          = None                            ,
                                      requires_conversion     = True                            ,
                                      default_value           = None                            ,
                                      has_default             = False                           ,
                                      nested_primitive_fields = nested_fields                   ) as _:

            assert _.name                == Safe_Str__Id('complex_param')
            assert _.param_type          is Type_Safe
            assert _.converted_type      is dict
            assert _.is_type_safe        is True
            assert _.requires_conversion is True
            assert _.nested_primitive_fields is not None
            assert len(_.nested_primitive_fields) == 2