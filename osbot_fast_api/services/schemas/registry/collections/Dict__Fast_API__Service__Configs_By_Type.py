# ═══════════════════════════════════════════════════════════════════════════════
# Dict__Fast_API__Service__Configs_By_Type
# Type-safe dictionary for storing service configs indexed by client class type
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config           import Fast_API__Service__Registry__Client__Config
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                               import Type_Safe__Dict


class Dict__Fast_API__Service__Configs_By_Type(Type_Safe__Dict):                # Maps client type → config
    expected_key_type   = type                                                  # The client class itself (any type)
    expected_value_type = Fast_API__Service__Registry__Client__Config           # Config for that client type
