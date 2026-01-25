# ═══════════════════════════════════════════════════════════════════════════════
# List__Client_Types
# Type-safe list of client class types
# ═══════════════════════════════════════════════════════════════════════════════
from typing                                                             import Type
from osbot_fast_api.services.registry.Service__Client__Base             import Service__Client__Base
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List   import Type_Safe__List

# todo: rename this class to List__Fast_API__Service__Client_Types
class List__Client_Types(Type_Safe__List):                                      # Collection of registered client types
    expected_type = Type[Service__Client__Base]
