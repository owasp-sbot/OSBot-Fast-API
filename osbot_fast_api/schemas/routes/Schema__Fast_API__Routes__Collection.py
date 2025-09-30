from typing                                                 import List
from osbot_utils.type_safe.Type_Safe                        import Type_Safe
from osbot_fast_api.schemas.routes.Schema__Fast_API__Route  import Schema__Fast_API__Route


class Schema__Fast_API__Routes__Collection(Type_Safe):                    # Collection of routes
    routes        : List[Schema__Fast_API__Route]
    total_routes  : int                           = 0
    has_mounts    : bool                          = False
    has_websockets: bool                          = False