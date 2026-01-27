# ═══════════════════════════════════════════════════════════════════════════════
# List__Fast_API__Service__Configs_Stack
# Type-safe list for storing saved config snapshots
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_fast_api.services.schemas.registry.collections.Dict__Fast_API__Service__Configs_By_Type import Dict__Fast_API__Service__Configs_By_Type
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List                              import Type_Safe__List


class List__Fast_API__Service__Configs_Stack(Type_Safe__List):                  # Stack of saved configs
    expected_type = Dict__Fast_API__Service__Configs_By_Type