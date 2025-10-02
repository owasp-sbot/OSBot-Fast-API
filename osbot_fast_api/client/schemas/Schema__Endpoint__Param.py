from typing import Any, Type
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from osbot_fast_api.client.schemas.enums.Enum__Param__Location                  import Enum__Param__Location

class Schema__Endpoint__Param(Type_Safe):
    name         : Safe_Str__Id                           # Parameter name
    location     : Enum__Param__Location                  # Where parameter appears
    param_type   : Type
    required     : bool                     = True        # Is parameter required?
