# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Env_Var
# Defines an environment variable that a service client expects
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str

# todo: refactor this class to be Schema__Fast_API__Registry__Env_Var
#     : also:
#           name should a type of Schema__Env_Var__Name (which needs to be created)
#           we should also create an Schema__Env_Var__Value
#           add note to refactor these to the OSbot-Utils project
class Schema__Env_Var(Type_Safe):                                               # Pure data - environment variable definition
    name     : Safe_Str                                                        # Env var name (e.g., "URL__TARGET_SERVER__CACHE")
    required : bool      = True                                                # Must be present at startup?
