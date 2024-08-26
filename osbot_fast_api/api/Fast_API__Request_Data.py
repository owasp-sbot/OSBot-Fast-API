import logging
import time
from decimal                                import Decimal
from fastapi                                import Response, Request
from osbot_utils.base_classes.Type_Safe     import Type_Safe
from osbot_utils.helpers.Random_Guid import Random_Guid
from osbot_utils.utils.Misc import timestamp_utc_now, current_thread_id

HEADER_NAME__FAST_API_REQUEST_ID   = 'fast-api-request-id'
HEADER_NAME__CACHE_CONTROL         = "cache-control"
HTTP_RESPONSE__CACHE_DURATION      = "3600"                         # 3600 = 1 hour
HTTP_RESPONSE__CACHE_CONTENT_TYPES = ['text/css; charset=utf-8']


class Fast_API__Request_Data(Type_Safe):
    fast_api_name           : str
    messages                : list
    response_content_length : str           = None
    response_content_type   : str           = None
    response_end_time       : Decimal       = None
    response_status_code    : int           = None
    request_id              : Random_Guid
    request_duration        : Decimal       = None
    request_host_name       : str           = None
    request_method          : str           = None
    request_port            : int           = None
    request_start_time      : Decimal       = None
    request_url             : str           = None
    timestamp               : int
    thread_id               : int
    traces                  : list

    def log_message(self, message_text, level:int =  logging.INFO):
        timestamp_delta = timestamp_utc_now()  - self.timestamp
        message = dict( level     = level          ,
                        text      = message_text   ,
                        timestamp = timestamp_delta)
        self.messages.append(message)

    def on_request(self, request: Request):
        self.timestamp          = timestamp_utc_now()
        self.request_start_time = Decimal(time.time())
        self.thread_id          = current_thread_id()
        # todo: add support for capturing request.headers and other request values (including request.url)

    def on_response(self, response: Response):
        self.response_end_time       = Decimal(time.time())
        self.request_duration        = self.response_end_time - self.request_start_time
        self.request_start_time      = self.request_start_time.quantize(Decimal('0.001')) # make sure these duration objects doing have move that 3 decimal points
        self.response_end_time       = self.response_end_time .quantize(Decimal('0.001')) # todo: see if there is a better way to do this (keeping the decimal points clean)
        self.request_duration        = self.request_duration  .quantize(Decimal('0.001')) #       (maybe a custom Decimal class)

        if response:
            self.response_content_type   = response.headers.get('content-type')
            self.response_content_length = response.headers.get('content-length')
            self.response_status_code    = response.status_code
            self.set_response_headers(response)


    def set_response_headers(self, response:Response):
        response.headers[HEADER_NAME__FAST_API_REQUEST_ID] = self.request_id
        self.set_response_header_for_static_files_cache(response)
        return self

    def set_response_header_for_static_files_cache(self, response:Response):
        if self.response_content_type in HTTP_RESPONSE__CACHE_CONTENT_TYPES:
            response.headers[HEADER_NAME__CACHE_CONTROL] = f"public, max-age={HTTP_RESPONSE__CACHE_DURATION}"




