from typing                                                                      import Type, Dict, List, Optional, Tuple
from osbot_fast_api.api.schemas.routes.Schema__Route__Parameter                  import Schema__Route__Parameter
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id  import Safe_Str__Id



class Schema__Route__Signature(Type_Safe):                              # Complete analysis of a route function's signature
    function_name           : Safe_Str__Id                              # Name of the function
    parameters              : List[Schema__Route__Parameter]            # All parameters analyzed
    return_type             : Optional[Type]              = None        # Return type annotation
    return_converted_type   : Optional[Type]              = None        # Converted return type (BaseModel)
    return_needs_conversion : bool                        = False       # Return needs Type_Safe → BaseModel conversion
    has_body_params         : bool                        = False       # Has parameters that go in request body
    has_path_params         : bool                        = False       # Has parameters in URL path
    has_query_params        : bool                        = False       # Has query string parameters
    # todo: change these tuple to Type_Safe class (so that we have a strong type on them)
    primitive_conversions   : Dict[str, Tuple[Type,Type]]                          # param_name → (Type_Safe__Primitive, base_type)
    type_safe_conversions   : Dict[str, Tuple[Type,Type]]                          # param_name → (Type_Safe, BaseModel)
    # todo: change this dict to leverage a Type_Safe or Type_Safe__Primitive base classes
    primitive_field_types   : Dict[str, dict ]                          # param_name → {field_name → primitive_class}