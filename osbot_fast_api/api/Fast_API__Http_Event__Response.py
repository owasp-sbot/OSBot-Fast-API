from decimal                            import Decimal
from osbot_utils.base_classes.Type_Safe import Type_Safe

class Fast_API__Http_Event__Response(Type_Safe):
    content_length  : str     = None
    content_type    : str     = None
    end_time        : Decimal = None
    status_code     : int     = None
    headers         : dict
