# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Env_Var__Name
# Type-safe string for environment variable names
# Validates that names follow standard env var naming conventions
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Header__Name import Safe_Str__Http__Header__Name
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


# todo: for OSBot-Utils migration - consider moving this to osbot_utils.type_safe.primitives.domains.env
#     : see if Safe_Str__Id is the best primitive to use here
class Safe_Str__Env_Var__Name(Safe_Str__Id):                                           # Environment variable name
    pass
