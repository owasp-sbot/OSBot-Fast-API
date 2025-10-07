from osbot_utils.type_safe.Type_Safe                                  import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid import Random_Guid

class Schema__Fast_API__Http_Event__Traces(Type_Safe):
    event_id    : Random_Guid
    traces_id   : Random_Guid
    traces      : list
    traces_count: int
