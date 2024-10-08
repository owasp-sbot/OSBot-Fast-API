from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.helpers.Random_Guid import Random_Guid


class Fast_API__Http_Event__Traces(Type_Safe):
    event_id    : Random_Guid
    traces_id   : Random_Guid
    traces      : list
    traces_count: int
