import os
from collections import deque
from decimal import Decimal
from unittest import TestCase

import pytest
from fastapi                                        import Request
from starlette.responses                            import Response
from starlette.datastructures                       import MutableHeaders, Address
from osbot_fast_api.api.Fast_API__Http_Events       import Fast_API__Http_Events, HTTP_EVENTS__MAX_REQUESTS_LOGGED
from osbot_fast_api.api.Fast_API__Http_Event        import Fast_API__Http_Event
from osbot_utils.helpers.trace.Trace_Call__Config   import Trace_Call__Config
from osbot_utils.testing.Stdout                     import Stdout
from osbot_utils.utils.Env                          import in_pytest_with_coverage
from osbot_utils.utils.Misc                         import list_set, is_guid, wait_for
from osbot_utils.utils.Dev                          import pprint


class test_Fast_API__Http_Events(TestCase):

    def setUp(self):
        self.path         = '/an-path'
        self.http_events  = Fast_API__Http_Events()
        self.client       = Address('pytest', 123)
        self.scope        = dict(type='http', client=self.client, path=self.path, method='GET', headers=[], query_string=b'' )
        self.request      = Request(self.scope)
        self.response     = Response()
        self.request_data = self.http_events.request_data(self.request)
        self.request_id   = self.http_events.request_id  (self.request)       # this is needed by multiple methods


    def test__init__(self):
        with self.http_events as _:

            expected_locals = {'background_tasks'     : []                                   ,
                               'clean_data'           : True                                 ,
                               'callback_on_request'  : None                                 ,
                               'callback_on_response' : None                                 ,
                               'fast_api_name'        : ''                                   ,
                               'requests_data'        : { self.request_id: self.request_data},
                               'requests_order'       : deque([self.request_id])             ,
                               'max_requests_logged'  : HTTP_EVENTS__MAX_REQUESTS_LOGGED     ,
                               'trace_call_config'    : _.trace_call_config                  ,
                               'trace_calls'          : False                                }
            assert _.__locals__() == expected_locals
            assert type(_.trace_call_config)  == Trace_Call__Config
            assert is_guid(self.request_id)

    def test_request_id(self):
        with self.http_events as _:
            assert self.request_id                  == _.request_id(self.request)
            assert self.request_data                == _.request_data(self.request)
            assert _.requests_data[self.request_id] == self.request_data

    def test_on_http_request(self):
        with self.http_events as _:
            _.on_http_request(self.request)

            assert self.request.state.request_id    == self.request_id
            assert _.requests_data                  == { self.request_id: self.request_data}
            assert _.requests_order                 == deque([self.request_id])
            assert self.request_data.request_id     == self.request_id
            assert _.request_data(self.request)     == self.request_data
            assert _.requests_data[self.request_id] == self.request_data

            #message_timestamp = self.request_data.log_messages[0].get('timestamp')
            expected_data = { 'http_event_info'        : { 'client_city'    : None                  ,
                                                           'client_country' : None                  ,
                                                           'client_ip'      : 'pytest'              ,
                                                           'domain'         : None                  ,
                                                           'fast_api_name'  : ''                    ,
                                                           'log_messages'   : []                    },
                              'http_event_request'     : { 'duration'       : None                                              ,
                                                           'headers'        : {}                                                ,
                                                           'host_name'      : None                                              ,
                                                           'method'         : 'GET'                                             ,
                                                           'path'           : self.path                                         ,
                                                           'port'           : None                                              ,
                                                           'start_time'     : self.request_data.http_event_request.start_time   },
                              'request_id'             : self.request_id                        ,
                              'response_content_length': None                                   ,
                              'response_content_type'  : None                                   ,
                              'response_headers'       : {}                                     ,
                              'response_end_time'      : None                                   ,
                              'response_status_code'   : None                                   ,
                              'thread_id'              : self.request_data.thread_id            ,
                              'timestamp'              : self.request_data.timestamp            ,
                              'traces'                 : []                                     ,
                              'traces_count'           : 0                                      }
            assert self.request_data.json() == expected_data

    def test_on_http_response(self):

        with self.http_events as _:
            assert self.response.headers == MutableHeaders({'content-length': '0'})
            _.on_http_request (self.request)
            wait_for(0.001)
            _.on_http_response(self.request, self.response)

            #assert _.log_requests  is False
            assert _.requests_data == {self.request_id : self.request_data}

            assert self.response.headers == MutableHeaders({'content-length': '0', 'fast-api-request-id': self.request_id})



            expected_data = { 'http_event_info'         : { 'client_city'     : None     ,
                                                            'client_country'  : None     ,
                                                            'client_ip'       : 'pytest' ,
                                                            'domain'          : None     ,
                                                            'fast_api_name'   : ''       ,
                                                            'log_messages'    : []       },
                              'http_event_request'       : {  'duration'      : Decimal('0.001')                                ,
                                                              'host_name'     : None                                            ,
                                                              'headers'       : {}                                              ,
                                                              'method'        : 'GET'                                           ,
                                                              'path'          : self.path                                       ,
                                                              'port'          : None                                            ,
                                                              'start_time'    : self.request_data.http_event_request.start_time },
                              'request_id'              : self.request_id                         ,
                              'response_content_length' : '0'                                     ,
                              'response_content_type'   : None                                    ,
                              'response_headers'        : self.request_data.response_headers      ,
                              'response_end_time'       : self.request_data.response_end_time     ,
                              'response_status_code'    : 200                                     ,
                              'thread_id'               : self.request_data.thread_id             ,
                              'timestamp'               : self.request_data.timestamp             ,
                              'traces'                  : []                                      ,
                              'traces_count'            : 0                                       }

            assert self.request_data.http_event_request.duration == Decimal(0.001).quantize(Decimal('0.001'))
            assert self.request_data.json()                      == expected_data


    def test_clean_request_data(self):
        with self.request_data as _:
            original_request_data = _.json()
            assert original_request_data.get('http_event_request').get('headers' ) == {}
            assert original_request_data.get('response_headers') == {}
            request_headers  = {}
            response_headers = {}
            _.http_event_request.headers  = request_headers
            _.response_headers            = response_headers
            assert _.http_event_request.headers  == request_headers                # confirm there are not headers captures in the request
            assert _.response_headers            == response_headers               # and response

            # use case without cookies
            request_headers ['a'] = 42                                                  # set request and response headers
            response_headers['a'] = 42
            assert _.http_event_request.headers  == {"a": 42}                      # confirm non-sensitive values before
            assert _.response_headers            == {"a": 42}

            self.http_events.clean_request_data(_)                                                      # ... calling clean_request_data
            assert _.http_event_request.headers  == {"a": 42}                      # ... have not been modified
            assert _.response_headers            == {"a": 42}

            # use case with cookies
            request_headers ['cookie'] = "this is a sensitive string (in request)"
            response_headers['cookie'] = "this is a sensitive string (in response)"
            self.http_events.clean_request_data(_)
            assert _.http_event_request.headers  == {"a": 42, 'cookie': 'data cleaned: (size: 39, hash: 2cec8b658de78fce49ad9e140669763a)'}
            assert _.response_headers            == {"a": 42, 'cookie': 'data cleaned: (size: 40, hash: 023287fb0f329d27b128359cde5c4574)'}






    @pytest.mark.skip("test needs refactoring/fixing") # due to the current change of not using picket to store the raw traces, and only storing the actual print_str of the traces
    def test_on_http_trace_start(self):
        with self.http_events as _:
            _.trace_call_config.trace_capture_contains = ['pprint']
            _.trace_calls  = True

            #############################################
            # 1st execution with trace_enabled (no traceable calls)
            _.on_http_trace_start(self.request)                                     # on_http_trace_start
            trace_call_1 = self.request.state.trace_call
            trace_call_config = trace_call_1.config

            assert trace_call_config       == _.trace_call_config
            assert type(trace_call_config) is Trace_Call__Config
            assert trace_call_1.started    is True

            _.on_http_trace_stop(self.request, self.response)
            assert trace_call_1.started    is False

            view_model_1 = _.request_traces_view_model(self.request)
            assert len(view_model_1)  == 1

            if in_pytest_with_coverage() is False:
                assert trace_call_1.stats() == {'calls': 15, 'calls_skipped': 15, 'exceptions': 0, 'lines': 30, 'returns': 12, 'unknowns': 0}

            for item in view_model_1:
                assert list_set(item) == ['duration', 'emoji', 'extra_data', 'lines', 'locals', 'method_name', 'method_parent', 'parent_info', 'prefix', 'source_code', 'source_code_caller', 'source_code_location', 'tree_branch']

            #############################################
            # 2nd execution with trace_enabled
            _.on_http_trace_start(self.request)
            with Stdout():
                pprint('some pprint')                                            # some call to generate some traces
            _.on_http_trace_stop(self.request, self.response)

            trace_call_2   = self.request.state.trace_call

            view_model_2 = _.request_traces_view_model(self.request)
            assert len(view_model_2) == 6
            if in_pytest_with_coverage() is False:
                assert trace_call_2.stats() == {'calls': 32, 'calls_skipped': 28, 'exceptions': 0, 'lines': 97, 'returns': 29, 'unknowns': 0}
            for item in view_model_2:
                assert list_set(item) == ['duration', 'emoji', 'extra_data', 'lines', 'locals', 'method_name',
                                          'method_parent', 'parent_info', 'prefix', 'source_code', 'source_code_caller',
                                          'source_code_location', 'tree_branch']

            # 3rd execution with trace_disabled
            #_.log_requests = False
            _.trace_call_config.trace_capture_contains = ['pprint']
            _.on_http_trace_start(self.request)
            assert trace_call_1.started is False                            # this value should not change
            with Stdout():
                pprint('some pprint')                                       # some call to generate some traces
            Fast_API__Http_Event()
            _.on_http_trace_stop(self.request, self.response)
            assert trace_call_1.started is False

            trace_call_3 = self.request.state.trace_call
            view_model_3 = _.request_traces_view_model(self.request)
            assert len(view_model_3) == 11
            assert trace_call_3.stats() == {'calls': 253, 'calls_skipped': 249, 'exceptions': 0, 'lines': 1608, 'returns': 250, 'unknowns': 0}

