# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Service__Client__Config
# Configuration schema shared by all service clients
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                            import FastAPI
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from mgraph_ai_service_cache_client.client.requests.schemas.enums.Enum__Client__Mode    import Enum__Client__Mode
from osbot_fast_api.services.schemas.registry.safe_str.Safe_Str__API_Key__Name          import Safe_Str__API_Key__Name
from osbot_fast_api.services.schemas.registry.safe_str.Safe_Str__API_Key__Value         import Safe_Str__API_Key__Value
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                import Safe_Str__Url

# todo: rename this class to Fast_API__Service__Registry__Client__Config

class Schema__Service__Client__Config(Type_Safe):                               # Pure data - client configuration
    mode          : Enum__Client__Mode             = None                       # IN_MEMORY or REMOTE (None = not configured)
    fast_api_app  : FastAPI                        = None                       # FastAPI app for IN_MEMORY mode
    base_url      : Safe_Str__Url                  = None                       # Base URL for REMOTE mode
    api_key_name  : Safe_Str__API_Key__Name        = None                       # HTTP header name for auth
    api_key_value : Safe_Str__API_Key__Value       = None                       # HTTP header value for auth
