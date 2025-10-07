from unittest                                                                    import TestCase
from osbot_utils.testing.__                                                      import __
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id  import Safe_Str__Id
from osbot_fast_api.api.schemas.routes.Schema__Route__Signature                  import Schema__Route__Signature
from osbot_fast_api.api.schemas.routes.Schema__Route__Parameter                  import Schema__Route__Parameter

class test_Schema__Route__Signature(TestCase):

    def test__init__(self):                                                         # Test signature schema initialization
        with Schema__Route__Signature() as _:
            assert type(_) is Schema__Route__Signature
            assert type(_) is not Type_Safe
            assert issubclass(type(_), Type_Safe)

            assert _.obj() == __(function_name           = _.function_name          ,
                                 parameters              = []                       ,
                                 return_type             = None                     ,
                                 return_converted_type   = None                     ,
                                 return_needs_conversion = False                    ,
                                 has_body_params         = False                    ,
                                 has_path_params         = False                    ,
                                 has_query_params        = False                    ,
                                 primitive_conversions   = __()                     ,
                                 type_safe_conversions   = __()                     ,
                                 primitive_field_types   = __()                     )

    def test__init__with_function_name(self):                                       # Test initialization with function name
        with Schema__Route__Signature(function_name=Safe_Str__Id('test_endpoint')) as _:
            assert _.function_name == Safe_Str__Id('test_endpoint')
            assert type(_.function_name) is Safe_Str__Id

    def test__init__with_parameters(self):                                          # Test initialization with parameters list
        param1 = Schema__Route__Parameter(name=Safe_Str__Id('param1'))
        param2 = Schema__Route__Parameter(name=Safe_Str__Id('param2'))

        with Schema__Route__Signature(parameters=[param1, param2]) as _:
            assert len(_.parameters) == 2
            assert _.parameters[0].name == Safe_Str__Id('param1')
            assert _.parameters[1].name == Safe_Str__Id('param2')

    def test__init__with_return_type(self):                                         # Test initialization with return type info
        with Schema__Route__Signature(return_type            = dict              ,
                                      return_needs_conversion = True             ) as _:
            assert _.return_type             is dict
            assert _.return_needs_conversion is True

    def test__init__with_conversion_flags(self):                                    # Test initialization with body/path/query flags
        with Schema__Route__Signature(has_body_params  = True ,
                                      has_path_params  = True ,
                                      has_query_params = True ) as _:
            assert _.has_body_params  is True
            assert _.has_path_params  is True
            assert _.has_query_params is True

    def test__init__with_conversion_dicts(self):                                    # Test initialization with conversion mappings
        primitive_conversions = {'user_id': (Safe_Str__Id, str)}
        type_safe_conversions = {'data': (Type_Safe, object)}

        with Schema__Route__Signature(primitive_conversions = primitive_conversions ,
                                      type_safe_conversions = type_safe_conversions ) as _:
            assert 'user_id' in _.primitive_conversions
            assert 'data'    in _.type_safe_conversions

    def test_json_serialization(self):                                              # Test JSON round-trip serialization
        param = Schema__Route__Parameter(name=Safe_Str__Id('test_param'))

        with Schema__Route__Signature(function_name = Safe_Str__Id('endpoint')  ,
                                      parameters    = [param]                   ,
                                      return_type   = str                       ) as original:
            json_data = original.json()

            assert 'function_name' in json_data
            assert 'parameters'    in json_data

            restored = Schema__Route__Signature.from_json(json_data)
            assert restored.function_name == original.function_name
            assert len(restored.parameters) == 1

    def test_complete_signature_scenario(self):                                     # Test complete signature with all fields populated
        param1 = Schema__Route__Parameter(name              = Safe_Str__Id('user_id')  ,
                                          is_primitive      = True                      ,
                                          primitive_base    = str                       )

        param2 = Schema__Route__Parameter(name              = Safe_Str__Id('data')     ,
                                          is_type_safe      = True                      ,
                                          requires_conversion = True                    )

        with Schema__Route__Signature(function_name           = Safe_Str__Id('create_user')  ,
                                      parameters              = [param1, param2]            ,
                                      return_type             = dict                        ,
                                      return_converted_type   = object                      ,
                                      return_needs_conversion = True                        ,
                                      has_body_params         = True                        ,
                                      primitive_conversions   = {'user_id': (Safe_Str__Id, str)}  ,
                                      type_safe_conversions   = {'data': (Type_Safe, object)}     ) as _:

            assert _.function_name           == Safe_Str__Id('create_user')
            assert len(_.parameters)         == 2
            assert _.return_needs_conversion is True
            assert _.has_body_params         is True
            assert 'user_id' in _.primitive_conversions
            assert 'data'    in _.type_safe_conversions


