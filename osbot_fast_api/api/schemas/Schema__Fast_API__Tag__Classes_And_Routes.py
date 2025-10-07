from typing                                                                     import Set, List
from osbot_fast_api.api.schemas.routes.Schema__Fast_API__Route                  import Schema__Fast_API__Route
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe

class Schema__Fast_API__Tag__Classes_And_Routes(Type_Safe):
    classes : Set[Safe_Str__Id]
    routes  : List[Schema__Fast_API__Route]