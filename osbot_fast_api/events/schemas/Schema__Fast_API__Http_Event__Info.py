from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid    import Random_Guid


class Schema__Fast_API__Http_Event__Info(Type_Safe):
    fast_api_name           : str           = None
    log_messages            : list
    client_city             : str           = None
    client_country          : str           = None
    client_ip               : str           = None
    event_id                : Random_Guid
    info_id                 : Random_Guid
    domain                  : str           = None
    timestamp               : int
    thread_id               : int
