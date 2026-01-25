# ═══════════════════════════════════════════════════════════════════════════════
# List__Fast_API__Registry__Env_Vars
# Type-safe list of environment variable definitions
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_fast_api.services.schemas.registry.Schema__Fast_API__Registry__Env_Var import Schema__Fast_API__Registry__Env_Var
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List             import Type_Safe__List


class List__Fast_API__Registry__Env_Vars(Type_Safe__List):                             # Collection of expected env vars
    expected_type = Schema__Fast_API__Registry__Env_Var
