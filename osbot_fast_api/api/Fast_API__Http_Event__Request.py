from decimal                            import Decimal
from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.helpers.Random_Guid    import Random_Guid


class Fast_API__Http_Event__Request(Type_Safe):
    duration        : Decimal       = None
    event_id        : Random_Guid
    host_name       : str           = None
    headers         : dict
    method          : str           = None
    port            : int           = None
    request_id      : Random_Guid
    start_time      : Decimal       = None
    path            : str           = None
