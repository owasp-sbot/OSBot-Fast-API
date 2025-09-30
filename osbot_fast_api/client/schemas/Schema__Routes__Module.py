from typing                                                                         import List
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id     import Safe_Str__Id
from osbot_fast_api.client.schemas.Schema__Endpoint__Contract                       import Schema__Endpoint__Contract


class Schema__Routes__Module(Type_Safe):                  # Represents a module of routes (e.g., 'file', 'admin', 'data')
    module_name  : Safe_Str__Id                           # e.g., "file", "admin"
    route_classes: List[Safe_Str__Id]                     # e.g., ["Routes__File__Store", "Routes__File__Retrieve"]
    endpoints    : List[Schema__Endpoint__Contract]       # All endpoints in this module
