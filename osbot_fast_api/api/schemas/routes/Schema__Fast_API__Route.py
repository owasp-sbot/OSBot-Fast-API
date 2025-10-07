from typing                                                                     import List, Type
from osbot_fast_api.api.schemas.enums.Enum__Fast_API__Route__Type               import Enum__Fast_API__Route__Type
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text
from osbot_fast_api.client.schemas.Schema__Endpoint__Param                      import Schema__Endpoint__Param
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.http.enums.Enum__Http__Method     import Enum__Http__Method
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix      import Safe_Str__Fast_API__Route__Prefix
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag         import Safe_Str__Fast_API__Route__Tag


class Schema__Fast_API__Route(Type_Safe):                                                 # Single route information
    body_params   : List[Schema__Endpoint__Param]         = None                          # or body_schema
    description   : Safe_Str__Text                                                        # endpoint description from docstring
    http_path     : Safe_Str__Fast_API__Route__Prefix                                     # The actual HTTP path
    http_methods  : List[Enum__Http__Method]                                              # HTTP methods supported
    is_default    : bool                                  = False                         # Is this a default FastAPI route
    is_mount      : bool                                  = False                         # Is this a mount point
    method_name   : Safe_Str__Id                          = None                          # Method/function name
    path_params   : List[Schema__Endpoint__Param]         = None
    query_params  : List[Schema__Endpoint__Param]         = None
    return_type   : Type                                  = None
    route_type    : Enum__Fast_API__Route__Type           = None
    route_class   : Safe_Str__Id                          = None                          # Class name if from Routes__* class
    route_tags    : List[Safe_Str__Fast_API__Route__Tag]  = None                          # Route tag/category








