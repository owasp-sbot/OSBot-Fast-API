from typing                                                                     import Any
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text
from osbot_fast_api.client.schemas.enums.Enum__Param__Location                  import Enum__Param__Location
from osbot_fast_api.client.schemas.safe_str.Safe_Str__Python_Type               import Safe_Str__Python__Type


class Schema__Endpoint__Param(Type_Safe):
    name         : Safe_Str__Id                           # Parameter name
    location     : Enum__Param__Location                  # Where parameter appears
    param_type   : Safe_Str__Python__Type                 # Type as string (for serialization)
    required     : bool                     = True        # Is parameter required?
    default      : Any                      = None        # Default value if any
    description  : Safe_Str__Text           = None        # Parameter documentation
