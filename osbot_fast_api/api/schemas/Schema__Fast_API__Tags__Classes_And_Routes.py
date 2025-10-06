from typing                                                           import Dict
from osbot_utils.type_safe.Type_Safe                                  import Type_Safe
from osbot_fast_api.api.schemas.Schema__Fast_API__Tag__Classes_And_Routes import Schema__Fast_API__Tag__Classes_And_Routes
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag   import Safe_Str__Fast_API__Route__Tag


class Schema__Fast__API_Tags__Classes_And_Routes(Type_Safe):
    by_tag : Dict[Safe_Str__Fast_API__Route__Tag, Schema__Fast_API__Tag__Classes_And_Routes]
