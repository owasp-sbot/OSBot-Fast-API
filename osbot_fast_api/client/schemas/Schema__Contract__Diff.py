from typing                                                                  import List
from osbot_utils.type_safe.Type_Safe                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text import Safe_Str__Text
from osbot_fast_api.client.schemas.Schema__Endpoint__Contract                import Schema__Endpoint__Contract


class Schema__Contract__Diff(Type_Safe):                        # Represents differences between two contracts
    added_endpoints     : List[Schema__Endpoint__Contract]
    removed_endpoints   : List[Schema__Endpoint__Contract]
    modified_endpoints  : List[Schema__Endpoint__Contract]
    breaking_changes    : List[Safe_Str__Text]
    non_breaking_changes: List[Safe_Str__Text]

    # todo : move this logic outside this schema
    def has_changes(self) -> bool:
        return bool(self.added_endpoints or self.removed_endpoints or self.modified_endpoints)

    def has_breaking_changes(self) -> bool:
        return bool(self.breaking_changes or self.removed_endpoints)