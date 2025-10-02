from typing                                                                   import Dict
from osbot_utils.type_safe.Type_Safe                                          import Type_Safe
from osbot_fast_api.schemas.Safe_Str__Fast_API__Route__Tag                    import Safe_Str__Fast_API__Route__Tag
from osbot_fast_api.schemas.routes.Schema__Fast__API__Tag__Classes_And_Routes import Schema__Fast__API__Tag__Classes_And_Routes

class Schema__Fast__API__Tags__Classes_And_Routes(Type_Safe):
    by_tag : Dict[Safe_Str__Fast_API__Route__Tag, Schema__Fast__API__Tag__Classes_And_Routes]
