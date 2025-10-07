from typing                                                                     import Type, Any
from osbot_fast_api.client.schemas.enums.Enum__Param__Location                  import Enum__Param__Location
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id

class Schema__Endpoint__Param(Type_Safe):
    default      : Any                   = None               # Default value if provided
    location     : Enum__Param__Location = None
    description  : Safe_Str__Text        = None               # Description if provided
    name         : Safe_Str__Id                               # Parameter name
    param_type   : Type
    required     : bool                   = True               # Only meaningful for query/body params

