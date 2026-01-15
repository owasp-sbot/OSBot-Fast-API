from typing                                                                                 import List, Type
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                        import Safe_UInt
from osbot_utils.type_safe.primitives.domains.http.enums.Enum__Http__Method                 import Enum__Http__Method
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id             import Safe_Str__Id
from osbot_fast_api.client.schemas.Schema__Endpoint__Param                                  import Schema__Endpoint__Param
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix                  import Safe_Str__Fast_API__Route__Prefix
from osbot_utils.type_safe.primitives.domains.python.safe_str.Safe_Str__Python__Module      import Safe_Str__Python__Module


class Schema__Endpoint__Contract(Type_Safe):

    # Endpoint identity - what FastAPI tells us
    operation_id : Safe_Str__Id                                 # Unique operation identifier
    method       : Enum__Http__Method                           # Single HTTP method for this contract
    path_pattern : Safe_Str__Fast_API__Route__Prefix            # URL pattern with {params}

    # Route class mapping - how the service organizes code
    route_class  : Safe_Str__Id                                 # e.g., "Routes__File__Store"
    route_method : Safe_Str__Id                                 # Original method name in route
    route_module : Safe_Str__Python__Module                     # Module path (e.g., "file", "admin")

    # Parameters - extracted from function signature
    path_params  : List[Schema__Endpoint__Param]
    query_params : List[Schema__Endpoint__Param]
    header_params: List[Schema__Endpoint__Param]

    # Request/Response schemas - Type names as strings for serialization
    request_schema : Type       = None           # Request body Type_Safe class name
    response_schema: Type       = None           # Response Type_Safe class name

    # Error handling - from AST analysis
    error_codes: List[Safe_UInt]                    # Status codes raised (excluding 400/422) # todo: we should be using Safe_UInt__Http__Error_Codes here
