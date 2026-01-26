# ═══════════════════════════════════════════════════════════════════════════════
# Dict__Fast_API__Service__Clients_By_Type
# Type-safe dictionary for storing service clients indexed by their class type
# ═══════════════════════════════════════════════════════════════════════════════
from typing                                                                     import Type
from osbot_fast_api.services.registry.Fast_API__Service__Registry__Client__Base import Fast_API__Service__Registry__Client__Base
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict           import Type_Safe__Dict


class Dict__Fast_API__Service__Clients_By_Type(Type_Safe__Dict):                       # Maps client type → client instance
    expected_key_type   = Type[Fast_API__Service__Registry__Client__Base]                                                         # The client class itself
    expected_value_type = Fast_API__Service__Registry__Client__Base                    # Instance of client
