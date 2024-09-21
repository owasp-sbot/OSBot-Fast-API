from osbot_utils.base_classes.Type_Safe import Type_Safe


class Fast_API__Http_Event__Info(Type_Safe):
    fast_api_name           : str           = None
    log_messages            : list
    client_city             : str           = None
    client_country          : str           = None
    client_ip               : str           = None
    domain                  : str           = None
    timestamp               : int
    thread_id               : int
