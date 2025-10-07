import types
from collections                                                      import deque
from fastapi                                                          import Request
from starlette.responses                                              import Response
from osbot_utils.type_safe.Type_Safe                                  import Type_Safe
from osbot_utils.helpers.trace.Trace_Call__Config                     import Trace_Call__Config
from osbot_fast_api.events.Fast_API__Http_Event                       import Fast_API__Http_Event
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid import Random_Guid


HTTP_EVENTS__MAX_REQUESTS_LOGGED = 50

from typing import TYPE_CHECKING, Union






class Fast_API__Http_Events(Type_Safe):
    #log_requests          : bool = False                           # todo: change this to save on S3 and disk
    background_tasks      : list
    clean_data            : bool             = True
    callback_on_request   : Union[types.MethodType, types.FunctionType]
    callback_on_response  : Union[types.MethodType, types.FunctionType]
    trace_calls           : bool             = False
    trace_call_config     : Trace_Call__Config
    requests_data         : dict
    requests_order        : deque
    max_requests_logged   : int = HTTP_EVENTS__MAX_REQUESTS_LOGGED
    fast_api_name         : str

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.trace_call_config.ignore_start_with = ['osbot_fast_api.api.Fast_API__Http_Events']        # so that we don't see traces from this

    def on_http_request(self, request: Request):
        with self.request_data(request) as _:
            _.on_request(request)
            self.request_trace_start(request)
            if self.callback_on_request:
                self.callback_on_request(_)

    def on_http_response(self, request: Request, response: Response):
        with self.request_data(request) as _:
            _.on_response(response)
            # if StreamingResponse not in base_types(response):                          # handle the special case when the response is a StreamingResponse
            self.request_trace_stop(request)                                             # todo: change this to be on text/event-stream"; charset=utf-8 (which is the one that happens with the LLMs responses)
            self.clean_request_data(_)
            if self.callback_on_response:
                self.callback_on_response(response, _)

    def clean_request_data(self, request_data: Fast_API__Http_Event):
        if self.clean_data:
            self.clean_request_data_field(request_data.http_event_request , 'headers', 'cookie')
            self.clean_request_data_field(request_data.http_event_response, 'headers', 'cookie')

    def clean_request_data_field(self, request_data, variable_name, field_name):
        from osbot_utils.utils.Misc import str_md5

        with request_data as _:
            variable_data = getattr(_, variable_name)
            if type(variable_data) is dict:
                if field_name in variable_data:
                    value = variable_data.get(field_name)
                    if type(value) is not str:
                        value = f'{value}'
                    data_size = len(value)
                    data_hash = str_md5(value)
                    value = f"data cleaned: (size: {data_size}, hash: {data_hash})"
                    variable_data[field_name] = value
    # def on_response_stream_completed(self, request):      #todo: rewire this (needed for StreamingResponse from LLMs)
    #     self.request_trace_stop(request)
        #state = request.state._state
        #print(f">>>>> on on_response_stream_end : {state}")

    def create_request_data(self, request):
        from osbot_fast_api.events.Fast_API__Http_Event                       import Fast_API__Http_Event
        from osbot_fast_api.events.schemas.Schema__Fast_API__Http_Event__Info import Schema__Fast_API__Http_Event__Info

        if hasattr(request.state, 'request_id'):                            # Use existing request_id if available (from Middleware__Request_ID)
            event_id = request.state.request_id
        else:
            event_id = Random_Guid()                                        # Fallback if middleware not present

        kwargs                         = dict(fast_api_name = self.fast_api_name)
        http_event_info                = Schema__Fast_API__Http_Event__Info(**kwargs)
        http_event                     = Fast_API__Http_Event(http_event_info=http_event_info, event_id=event_id)
        event_id                       = http_event.event_id                # get the random request_id/guid that was created in the ctor of Fast_API__Request_Data
        request.state.http_events      = self                               # store a copy of this object in the request (so that it is available durant the request handling)
        request.state.request_id       = event_id                           # store request_id in request.state
        request.state.request_data     = http_event                         # store request_data object in request.stat
        self.requests_data[event_id]   = http_event                         # capture request_data in self.requests_data
        self.requests_order.append(event_id)                                # capture request order in self.requests_order

        if len(self.requests_order) > self.max_requests_logged:             # remove oldest request if we have more than max_requests_logged
            request_id_to_remove = self.requests_order.popleft()            # todo: move this to a separate method that is responsible for the size
            del self.requests_data[request_id_to_remove]                    #       in fact the whole requests_data should in a separate class

        return http_event

    def request_data(self, request: Request):                               # todo: refactor all this request_data into a Request_Data class
        if not hasattr(request.state, "request_data"):
            request_data = self.create_request_data(request)
        else:
            request_data = request.state.request_data
        return request_data


    def event_id(self, request):
        return self.request_data(request).event_id

    def request_messages(self, request):
        event_id   = self.event_id(request)
        http_event = self.requests_data.get(event_id)#.get('messages', [])
        if type(http_event) is Fast_API__Http_Event:
            return http_event.messages()
        if type(http_event) is dict:
            return http_event.get('messages', [])
        return []

    def request_trace_start(self, request):
        from osbot_utils.helpers.trace.Trace_Call import Trace_Call

        if self.trace_calls:
            trace_call_config = self.trace_call_config
            trace_call = Trace_Call(config=trace_call_config)
            trace_call.start()
            request.state.trace_call = trace_call

    def request_trace_stop(self, request: Request):
        from osbot_utils.helpers.trace.Trace_Call           import Trace_Call
        # pragma: no cover
        if self.trace_calls:
            trace_call: Trace_Call = request.state.trace_call
            trace_call.stop()

            request_data = self.request_data(request)
            request_data.add_traces(trace_call)

    # def request_traces_view_model(self, request):
    #     #return self.request_data(request).traces                                # todo: see if we need to store the traces in pickle
    #     request_traces = []
    #     for trace_bytes in self.request_data(request).traces:                 # support for multiple trace's runs
    #         request_traces.extend(pickle_from_bytes(trace_bytes))
    #     return request_traces


