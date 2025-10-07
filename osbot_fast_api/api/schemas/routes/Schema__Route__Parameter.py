from typing                                                                     import Type, Any, Optional
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


class Schema__Route__Parameter(Type_Safe):                              # Represents a single route parameter with conversion metadata
    name                    : Safe_Str__Id                              # Parameter name
    param_type              : Type                                      # Original type annotation
    converted_type          : Optional[Type]              = None        # Type after conversion (BaseModel/primitive)
    is_primitive            : bool                        = False       # Is Type_Safe__Primitive
    is_type_safe            : bool                        = False       # Is Type_Safe (non-primitive)
    primitive_base          : Optional[Type]              = None        # Base type for primitives (str, int, float)
    requires_conversion     : bool                        = False       # Needs Type_Safe → BaseModel conversion
    default_value           : Any                         = None        # Default value if provided
    has_default             : bool                        = False       # Whether parameter has default
    # todo: see what is the types we should be using in the dict below
    nested_primitive_fields : dict                        = None        # Map of field_name → primitive_class for Type_Safe classes