# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__Service__Registry__Client__Config
# Configuration schema shared by all service clients
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                                                    import FastAPI
from osbot_fast_api.api.Fast_API                                                                                import Fast_API
from osbot_utils.type_safe.Type_Safe                                                                            import Type_Safe
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode             import Enum__Fast_API__Service__Registry__Client__Mode
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Header__Name                        import Safe_Str__Http__Header__Name
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Header__Value                       import Safe_Str__Http__Header__Value
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                                        import Safe_Str__Url


class Fast_API__Service__Registry__Client__Config(Type_Safe):                   # Pure data - client configuration
    mode          : Enum__Fast_API__Service__Registry__Client__Mode = None      # IN_MEMORY or REMOTE (None = not configured)
    fast_api      : Fast_API                                        = None      # Fast_API instance for IN_MEMORY mode
    fast_api_app  : FastAPI                                         = None      # FastAPI app for IN_MEMORY mode
    base_url      : Safe_Str__Url                                   = None      # Base URL for REMOTE mode
    api_key_name  : Safe_Str__Http__Header__Name                    = None      # HTTP header name for auth
    api_key_value : Safe_Str__Http__Header__Value                   = None      # HTTP header value for auth
