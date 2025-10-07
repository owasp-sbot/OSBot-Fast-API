import logging
import time
from decimal                                                                import Decimal
from fastapi                                                                import Response, Request
from osbot_fast_api.events.schemas.Schema__Fast_API__Http_Event__Info       import Schema__Fast_API__Http_Event__Info
from osbot_fast_api.events.schemas.Schema__Fast_API__Http_Event__Request    import Schema__Fast_API__Http_Event__Request
from osbot_fast_api.events.schemas.Schema__Fast_API__Http_Event__Response   import Schema__Fast_API__Http_Event__Response
from osbot_fast_api.events.schemas.Schema__Fast_API__Http_Event__Traces     import Schema__Fast_API__Http_Event__Traces
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid       import Random_Guid
from osbot_utils.helpers.trace.Trace_Call                                   import Trace_Call
from osbot_utils.utils.Misc                                                 import timestamp_utc_now, current_thread_id, str_to_bytes
from osbot_utils.utils.Objects                                              import pickle_to_bytes

HEADER_NAME__FAST_API_REQUEST_ID   = 'fast-api-request-id'
HEADER_NAME__CACHE_CONTROL         = "cache-control"
HTTP_RESPONSE__CACHE_DURATION      = "3600"                         # 3600 = 1 hour
HTTP_RESPONSE__CACHE_CONTENT_TYPES = ['text/css; charset=utf-8'         ,
                                      'text/javascript; charset=utf-8'  ,
                                      'image/png'                       ,
                                      'text/plain; charset=utf-8'       ]


class Fast_API__Http_Event(Type_Safe):
    http_event_info         : Schema__Fast_API__Http_Event__Info
    http_event_request      : Schema__Fast_API__Http_Event__Request
    http_event_response     : Schema__Fast_API__Http_Event__Response
    http_event_traces       : Schema__Fast_API__Http_Event__Traces
    event_id                : Random_Guid                                  # todo: rename to http_event_id

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_ids()

    def set_ids(self):
        self.http_event_info.event_id       = self.event_id
        self.http_event_request.event_id    = self.event_id
        self.http_event_response.event_id   = self.event_id
        self.http_event_traces.event_id     = self.event_id

    def add_log_message(self, message_text, level:int =  logging.INFO):
        timestamp_delta = timestamp_utc_now()  - self.http_event_info.timestamp
        message = dict( level     = level          ,
                        text      = message_text   ,
                        timestamp = timestamp_delta)
        self.http_event_info.log_messages.append(message)

    def add_traces(self, trace_call: Trace_Call):
        view_model             = trace_call.view_data()
        view_model_bytes       = pickle_to_bytes(view_model)
        self.http_event_traces.traces.append(view_model_bytes)
        self.http_event_traces.traces_count += len(view_model)
        self.add_log_message(f"added {len(view_model)} traces")

    def messages(self):

        messages = []
        for log_message in self.http_event_info.log_messages:
            messages.append(log_message.get('text'))
        return messages

    def on_request(self, request: Request):
        # http_event_request
        self.http_event_request.headers      = dict(request.headers)
        self.http_event_request.host_name    = request.url.hostname
        self.http_event_request.method       = request.method
        self.http_event_request.path         = request.url.path
        self.http_event_request.port         = request.url.port
        self.http_event_request.start_time   = Decimal(time.time())

        # http_event_info
        self.http_event_info.domain          = request.headers.get('cloudfront-domain'        )
        self.http_event_info.client_country  = request.headers.get('cloudfront-viewer-country')
        self.http_event_info.client_city     = request.headers.get('cloudfront-viewer-city'   )
        self.http_event_info.client_ip       = request.client.host
        self.http_event_info.timestamp       = timestamp_utc_now()
        self.http_event_info.thread_id       = current_thread_id()

    def on_response(self, response: Response):
        # http_event_response
        self.http_event_response.end_time   = Decimal(time.time())
        self.http_event_request.duration    = self.http_event_response.end_time - self.http_event_request.start_time    # todo: move this normalisation logic into the Http_Event_* classes
        self.http_event_request.start_time  = self.http_event_request.start_time .quantize(Decimal('0.001'))            # make sure these duration objects doing have move that 3 decimal points
        self.http_event_response.end_time   = self.http_event_response.end_time  .quantize(Decimal('0.001'))            # todo: see if there is a better way to do this (keeping the decimal points clean)
        self.http_event_request.duration    = self.http_event_request.duration   .quantize(Decimal('0.001'))            #       (maybe a custom Decimal class)

        if response:
            self.set_response_header_for_static_files_cache(response)
            self.http_event_response.content_type   = response.headers.get('content-type')
            self.http_event_response.content_length = response.headers.get('content-length')
            self.http_event_response.status_code    = response.status_code
            self.http_event_response.headers        = dict(response.headers)


    def set_response_header_for_static_files_cache(self, response:Response):
        if self.http_event_response.content_type in HTTP_RESPONSE__CACHE_CONTENT_TYPES:
            response.headers[HEADER_NAME__CACHE_CONTROL] = f"public, max-age={HTTP_RESPONSE__CACHE_DURATION}"



