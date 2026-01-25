# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Fast_API__Registry__Env_Var
# Defines an environment variable that a service client expects
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                                   import Type_Safe
from osbot_fast_api.services.schemas.registry.safe_str.Safe_Str__Env_Var__Name         import Safe_Str__Env_Var__Name

# todo: for OSBot-Utils migration - consider moving Safe_Str__Env_Var__Name/Value to osbot_utils

class Schema__Fast_API__Registry__Env_Var(Type_Safe):                                  # Pure data - environment variable definition
    name     : Safe_Str__Env_Var__Name                                                 # Env var name (e.g., "URL__TARGET_SERVER__CACHE")
    required : bool                    = True                                          # Must be present at startup?
