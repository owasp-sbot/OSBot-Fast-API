# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__Service__Registry__Client__Config
# Configuration schema shared by all service clients
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                                   import FastAPI
from osbot_utils.type_safe.Type_Safe                                                           import Type_Safe
from osbot_fast_api.services.schemas.registry.enums.Enum__Client__Mode                         import Enum__Client__Mode
from osbot_fast_api.services.schemas.registry.safe_str.Safe_Str__Fast_API__Auth__Key_Name      import Safe_Str__Fast_API__Auth__Key_Name
from osbot_fast_api.services.schemas.registry.safe_str.Safe_Str__Fast_API__Auth__Key_Value     import Safe_Str__Fast_API__Auth__Key_Value
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                       import Safe_Str__Url


class Fast_API__Service__Registry__Client__Config(Type_Safe):                          # Pure data - client configuration
    mode          : Enum__Client__Mode                   = None                        # IN_MEMORY or REMOTE (None = not configured)
    fast_api_app  : FastAPI                              = None                        # FastAPI app for IN_MEMORY mode
    base_url      : Safe_Str__Url                        = None                        # Base URL for REMOTE mode
    api_key_name  : Safe_Str__Fast_API__Auth__Key_Name   = None                        # HTTP header name for auth
    api_key_value : Safe_Str__Fast_API__Auth__Key_Value  = None                        # HTTP header value for auth
