from collections                                    import deque
from osbot_fast_api.api.Fast_API__Request_Data      import Fast_API__Request_Data
from osbot_utils.base_classes.Type_Safe             import Type_Safe
from fastapi                                        import Request
from starlette.responses                            import Response
from osbot_utils.helpers.trace.Trace_Call           import Trace_Call
from osbot_utils.helpers.trace.Trace_Call__Config   import Trace_Call__Config


HTTP_EVENTS__MAX_REQUESTS_LOGGED = 50

class Fast_API__Http_Events(Type_Safe):
    #log_requests          : bool = False                           # todo: change this to save on S3 and disk
    trace_calls           : bool = False
    trace_call_config     : Trace_Call__Config
    requests_data         : dict
    requests_order        : deque
    max_requests_logged   : int = HTTP_EVENTS__MAX_REQUESTS_LOGGED
    fast_api_name         : str
    #add_header_request_id : bool = True

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.trace_call_config.ignore_start_with = ['osbot_fast_api.api.Fast_API__Http_Events']        # so that we don't see traces from this

    def on_http_request(self, request: Request):
        with self.request_data(request) as _:
            _.on_request(request)
            _.log_message("on_http_request")

    def on_http_response(self, request: Request, response:Response):
        with self.request_data(request) as _:
            _.on_response(response)
            _.log_message("on_http_response")

    def on_http_trace_start(self, request: Request):
        #print(">>>>>> on on_http_trace_start")
        self.request_trace_start(request)

    def on_http_trace_stop(self, request: Request, response: Response):             # pragma: no cover
        #if StreamingResponse not in base_types(response):                          # handle the special case when the response is a StreamingResponse
        self.request_trace_stop(request)                                            # todo: change this to be on text/event-stream"; charset=utf-8 (which is the one that happens with the LLMs responses)



    def on_response_stream_completed(self, request):
        self.request_trace_stop(request)
        #state = request.state._state
        #print(f">>>>> on on_response_stream_end : {state}")

    def create_request_data(self, request):
        kwargs        = dict(request_url       = request.url.path    ,
                             request_method    = request.method      ,
                             request_port      = request.url.port    ,
                             request_host_name = request.url.hostname,
                             fast_api_name     = self.fast_api_name  )
        request_data = Fast_API__Request_Data(**kwargs)
        request_id   = request_data.request_id                              # get the random request_id/guid that was created in the ctor of Fast_API__Request_Data
        request.state.http_events      = self                               # store a copy of this object in the request (so that it is available durant the request handling)
        request.state.request_id       = request_id                         # store request_id in request.state
        request.state.request_data     = request_data                       # store request_data object in request.stat
        self.requests_data[request_id] = request_data                       # capture request_data in self.requests_data
        self.requests_order.append(request_id)                              # capture request order in self.requests_order

        if len(self.requests_order) > self.max_requests_logged:             # remove oldest request if we have more than max_requests_logged
            request_id_to_remove = self.requests_order.popleft()            # todo: move this to a separate method that is responsible for the size
            del self.requests_data[request_id_to_remove]                    #       in fact the whole requests_data should in a separate class

        return request_data

    def request_data(self, request: Request):                   # todo: refactor all this request_data into a Request_Data class
        if not hasattr(request.state, "request_data"):
            request_data = self.create_request_data(request)
        else:
            request_data = request.state.request_data
        return request_data


    def request_id(self, request):
        return self.request_data(request).request_id

    def request_messages(self, request):
        request_id = self.request_id(request)
        return self.requests_data.get(request_id, {}).get('messages', [])

    def request_trace_start(self, request):
        if self.trace_calls:
            trace_call_config = self.trace_call_config
            trace_call = Trace_Call(config=trace_call_config)
            trace_call.start()
            request.state.trace_call = trace_call

    def request_trace_stop(self, request: Request):                                                         # pragma: no cover
        if self.trace_calls:
            request_id: str = self.request_id(request)
            trace_call: Trace_Call = request.state.trace_call
            trace_call.stop()

            self.request_traces_append(request)

    def request_traces_view_model(self, request):
        return self.request_data(request).traces                                # todo: see if we need to store the traces in pickle
        # request_traces = []
        # for trace_bytes in self.request_data(request).traces:                 # support for multiple trace's runs
        #     request_traces.extend(pickle_from_bytes(trace_bytes))
        # return request_traces

    def request_traces_append(self, request):
        if self.trace_calls:
            request_data           = self.request_data(request)
            trace_call: Trace_Call = request.state.trace_call
            #view_model             = trace_call.view_data()                    # todo: see if it is better to store the view_data (as pickle) instead of the serialised view as str (used below)
            #view_model_bytes       = pickle_to_bytes(view_model)
            # request_data.traces.append(view_model_bytes)
            traces_str             = trace_call.print_to_str()
            request_data.traces.append(traces_str)
        return self


