from typing                                                                         import List
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now    import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version     import Safe_Str__Version
from osbot_fast_api.client.schemas.Schema__Endpoint__Contract                       import Schema__Endpoint__Contract
from osbot_fast_api.client.schemas.Schema__Routes__Module                           import Schema__Routes__Module
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Name                                import Safe_Str__Fast_API__Name
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Prefix                       import Safe_Str__Fast_API__Route__Prefix


class Schema__Service__Contract(Type_Safe):
    service_name : Safe_Str__Fast_API__Name               # Service identifier
    version      : Safe_Str__Version                      # Contract version
    base_path    : Safe_Str__Fast_API__Route__Prefix      # Base URL path
    modules      : List[Schema__Routes__Module]           # Organized route modules
    endpoints    : List[Schema__Endpoint__Contract]       # All service endpoints (flat list)

    # Metadata for tracking and versioning
    generated_at    : Timestamp_Now                       # When contract was generated
    service_version : Safe_Str__Version                   # Version of service
    client_version  : Safe_Str__Version                   # Minimum client version required
