from typing                                                                     import List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Prefix                   import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Tag                      import Safe_Str__Fast_API__Route__Tag
from osbot_fast_api.schemas.for_osbot_utils.enums.Enum__Http__Method            import Enum__Http__Method
from osbot_fast_api.schemas.routes.enums.Enum__Route__Type                      import Enum__Route__Type


class Schema__Fast_API__Route(Type_Safe):                                           # Single route information
    http_path     : Safe_Str__Fast_API__Route__Prefix                               # The actual HTTP path
    method_name   : Safe_Str__Id                                                    # Method/function name
    http_methods  : List[Enum__Http__Method]                                        # HTTP methods supported
    route_type    : Enum__Route__Type               = Enum__Route__Type.API_ROUTE
    route_class   : Safe_Str__Id                    = None                          # Class name if from Routes__* class
    route_tag     : Safe_Str__Fast_API__Route__Tag  = None                          # Route tag/category
    is_default    : bool                            = False                         # Is this a default FastAPI route
    is_mount      : bool                            = False                         # Is this a mount point
