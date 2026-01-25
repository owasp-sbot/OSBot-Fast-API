# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Env_Var__Value
# Type-safe string for environment variable values
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Header__Value import Safe_Str__Http__Header__Value


# todo: for OSBot-Utils migration - consider moving this to osbot_utils.type_safe.primitives.domains.env
#     : see is Safe_Str__Http__Header__Value is the best base type to use here
class Safe_Str__Env_Var__Value(Safe_Str__Http__Header__Value):                                      # Environment variable value
    pass
