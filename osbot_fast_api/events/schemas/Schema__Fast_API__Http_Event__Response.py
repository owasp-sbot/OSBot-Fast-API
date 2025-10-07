from decimal                            import Decimal
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid    import Random_Guid


class Schema__Fast_API__Http_Event__Response(Type_Safe):
    content_length  : str           = None
    content_type    : str           = None
    end_time        : Decimal       = None
    event_id        : Random_Guid
    response_id     : Random_Guid
    status_code     : int           = None
    headers         : dict
