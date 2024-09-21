from decimal import Decimal

from osbot_utils.base_classes.Type_Safe import Type_Safe


class Fast_API__Http_Event__Request(Type_Safe):
    duration        : Decimal       = None
    host_name       : str           = None
    headers         : dict
    method          : str           = None
    port            : int           = None
    start_time      : Decimal       = None
    path            : str           = None
