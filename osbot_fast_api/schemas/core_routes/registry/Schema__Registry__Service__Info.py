from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Registry__Service__Info(Type_Safe):                               # Info about a registered service
    service_name   : str                                                        # e.g., "Cache__Service__Client"
    service_module : str                                                        # e.g., "mgraph_ai_service_cache_client.client"
    mode           : str                                                        # "IN_MEMORY" or "REMOTE"
    base_url       : str          = None                                        # Only for REMOTE mode (sanitized)
    has_api_key    : bool         = False                                       # True if API key configured
    has_fast_api   : bool         = False                                       # True if FastAPI app available
