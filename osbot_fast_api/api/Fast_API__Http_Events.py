import threading
from collections import deque

from osbot_utils.base_classes.Type_Safe             import Type_Safe
from fastapi                                        import Request
from starlette.responses                            import Response, StreamingResponse

from osbot_utils.helpers.trace.Trace_Call import Trace_Call
from osbot_utils.helpers.trace.Trace_Call__Config   import Trace_Call__Config
from osbot_utils.utils.Dev                          import pprint
from osbot_utils.utils.Misc                         import random_guid
from osbot_utils.utils.Objects import base_types, pickle_to_bytes, pickle_from_bytes

HEADER_NAME__FAST_API_REQUEST_ID = 'fast-api-request-id'
HTTP_EVENTS__MAX_REQUESTS_LOGGED = 100

class Fast_API__Http_Events(Type_Safe):
    log_requests          : bool = False
    trace_calls           : bool = False
    trace_call_config     : Trace_Call__Config
    requests_data         : dict
    requests_order        : deque
    max_requests_logged   : int = HTTP_EVENTS__MAX_REQUESTS_LOGGED
    fast_api_name         : str
    add_header_request_id : bool = True

    def on_http_duration(self, request, request_duration):
        self.log_request_message(request, f'{request.state.request_id} took : {request_duration.get("duration")} seconds')

    def on_http_request(self, request: Request):
        request_id = self.request_id(request)

        request_url    = request.url
        request_method = request.method
        thread_id      = self.current_thread_id()

        self.log_request_message(request, f'>> on_http_request {thread_id} : {self.fast_api_name} | {request_id} with {len(self.requests_data)} requests, for url: {request_method} {request_url}')

    def on_http_response(self, request: Request, response:Response):
        request_id = request.state.request_id
        self.set_response_headers(request, response)
        self.log_request_message(request, f'** on_http_response :{self.fast_api_name} | {request_id} with {len(self.requests_data)} requests, for url: {request.method} {request.url}')

    def on_http_trace_start(self, request: Request):
        #print(">>>>>> on on_http_trace_start")
        self.request_trace_start(request)

    def on_http_trace_stop(self, request: Request, response: Response):             # pragma: no cover
        if StreamingResponse not in base_types(response):                           # handle the special case when the response is a StreamingResponse
            self.request_trace_stop(request)

    def current_thread_id(self):
        return threading.current_thread().native_id

    def log_request_message(self, request, message):
        if self.log_requests:
            request_data = self.request_data(request)
            request_data['messages'].append(message)

    def on_response_stream_completed(self, request):
        self.request_trace_stop(request)
        #state = request.state._state
        #print(f">>>>> on on_response_stream_end : {state}")

    def request_data(self, request: Request):                   # todo: refactor all this request_data into a Request_Data class
        request_id   = self.request_id(request)
        request_data = self.requests_data.get(request_id)
        if not request_data:
            request_data = dict(request_id  = request_id       ,   # todo: this is should be creation of a new Fast_API__Request_Data object
                                request_url = request.url.path ,
                                messages    = []               ,
                                traces      = []               )
            self.requests_data[request_id] = request_data
            self.requests_order.append(request_id)
        return request_data


    def request_id(self, request):
        if hasattr(request.state, "request_id"):
            return request.state.request_id
        else:
            return self.set_request_id(request)

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

            if self.log_requests:
                self.log_request_message(request, f'{request_id} on trace stop: {trace_call}')
                self.request_traces_append(request)

    def request_traces_view_model(self, request):
        request_traces = []
        for trace_bytes in self.request_data(request).get('traces'):        # support for multiple trace's runs
            request_traces.extend(pickle_from_bytes(trace_bytes))
        return request_traces

    def request_traces_append(self, request):
        if self.log_requests:
            trace_call: Trace_Call = request.state.trace_call
            request_id       = request.state.request_id
            request_data     = self.requests_data.get(request_id)
            view_model       = trace_call.view_data()
            view_model_bytes = pickle_to_bytes(view_model)
            request_data['traces'].append(view_model_bytes)
        return self

    def set_request_id(self, request):
        request_id = random_guid()
        request.state.request_id = request_id
        request.state.http_events = self             # todo: see if this is best place to put this
        return request_id

    def set_response_headers(self, request: Request, response:Response):
        if self.add_header_request_id and response:
            request_id = request.state.request_id
            response.headers[HEADER_NAME__FAST_API_REQUEST_ID] = request_id
        return self

