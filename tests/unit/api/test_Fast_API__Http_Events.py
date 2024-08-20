import os
from collections import deque
from unittest import TestCase
from fastapi                                        import Request
from starlette.responses                            import Response
from starlette.datastructures                       import MutableHeaders
from osbot_fast_api.api.Fast_API__Http_Events import Fast_API__Http_Events, HTTP_EVENTS__MAX_REQUESTS_LOGGED
from osbot_utils.helpers.trace.Trace_Call__Config   import Trace_Call__Config

from osbot_utils.utils.Dev                          import pprint
from osbot_utils.utils.Env import in_pytest_with_coverage
from osbot_utils.utils.Json import json_to_str
from osbot_utils.utils.Misc import random_guid, list_set
from osbot_utils.utils.Objects import pickle_to_bytes, pickle_from_bytes


class test_Fast_API__Http_Events(TestCase):

    def setUp(self):
        self.http_events = Fast_API__Http_Events()
        self.scope       = dict(type='http', path='/', method='GET', headers=[], query_string=b'' )
        self.request     = Request(self.scope)
        self.response    = Response()
        self.request_id  = self.http_events.set_request_id(self.request)       # this is needed by multiple methods


    def test__init__(self):
        with self.http_events as _:
            expected_locals = {'add_header_request_id': True                              ,
                               'fast_api_name'        : ''                                ,
                               'log_requests'         : False                             ,
                               'requests_data'        : {}                                ,
                               'requests_order'       : deque([])                         ,
                               'max_requests_logged'  : HTTP_EVENTS__MAX_REQUESTS_LOGGED  ,
                               'trace_call_config'    : _.trace_call_config               ,
                               'trace_calls'          : False                             }
            assert _.__locals__() == expected_locals
            assert type(_.trace_call_config)  == Trace_Call__Config

    def test_on_http_duration(self):
        with self.http_events as _:
            duration         = '0.123'
            request_duration = {'duration': duration}
            _.on_http_duration(self.request, request_duration)

            assert _.log_requests  is False
            assert _.requests_data == {}

            _.log_requests = True
            _.on_http_duration(self.request, request_duration)

            message = f'{self.request_id} took : {duration} seconds'
            assert _.requests_data == {self.request_id: {'messages'     : [message]      ,
                                                         'request_id'   : self.request_id,
                                                         'request_url'  : '/'            ,
                                                         'traces'       : []             }}

    def test_on_http_request(self):
        with self.http_events as _:
            _.on_http_request(self.request)

            assert _.log_requests   is False
            assert _.requests_data  == {}
            assert _.requests_order == deque([])

            request_id    = _.request_id(self.request)
            empty_request = { 'messages'    : []         ,
                              'request_id' : request_id  ,
                              'request_url': '/'         ,
                              'traces'     : []          }
            thread_id      = _.current_thread_id()
            fast_api_name  = _.fast_api_name
            request_method = self.request.method
            request_url    = self.request.url
            request_data   = _.request_data(self.request)  # this will trigger the creation of the request_data object

            assert request_data == empty_request

            assert _.requests_data == {request_id: request_data}
            assert _.requests_order == deque([self.request_id])
            _.log_requests = True
            _.on_http_request(self.request)


            message  = f'>> on_http_request {thread_id} : {fast_api_name} | {request_id} with {len(_.requests_data)} requests, for url: {request_method} {request_url}'
            assert _.request_messages(self.request) == [message]
            assert _.requests_data == {request_id: request_data}
            assert request_data    == { 'messages'   : [message]   ,
                                        'request_id' : request_id  ,
                                        'request_url': '/'         ,
                                        'traces'     : []          }
    def test_on_http_response(self):

        with self.http_events as _:
            assert self.response.headers == MutableHeaders({'content-length': '0'})
            _.on_http_response(self.request, self.response)

            assert _.log_requests  is False
            assert _.requests_data == {}
            assert self.response.headers == MutableHeaders({'content-length': '0', 'fast-api-request-id': self.request_id})

            request_data     = _.request_data(self.request)
            request_messages = _.request_messages(self.request)
            expected_message = f'** on_http_response :{_.fast_api_name} | {self.request_id} with {len(_.requests_data)} requests, for url: {self.request.method} {self.request.url}'

            _.log_requests = True
            _.on_http_response(self.request, self.response)

            assert _.requests_data  == {self.request_id: request_data}
            assert request_messages == [expected_message]

    def test_on_http_trace_start(self):
        with self.http_events as _:
            _.trace_call_config.trace_capture_contains = ['fast_api']
            _.log_requests = True

            # 2nd execution with trace_enabled
            _.on_http_trace_start(self.request)                                     # on_http_trace_start
            trace_call_1 = self.request.state.trace_call
            trace_call_config = trace_call_1.config

            assert trace_call_config       == _.trace_call_config
            assert type(trace_call_config) is Trace_Call__Config
            assert trace_call_1.started    is True

            _.on_http_trace_stop(self.request, self.response)
            assert trace_call_1.started    is False

            view_model_1 = _.request_traces_view_model(self.request)
            assert len(view_model_1)  == 3
            if in_pytest_with_coverage() is False:
                assert trace_call_1.stats() == {'calls': 14, 'calls_skipped': 12, 'exceptions': 0, 'lines': 35, 'returns': 11, 'unknowns': 0}
            for item in view_model_1:
                assert list_set(item) == ['duration', 'emoji', 'extra_data', 'lines', 'locals', 'method_name', 'method_parent', 'parent_info', 'prefix', 'source_code', 'source_code_caller', 'source_code_location', 'tree_branch']

            # 2nd execution with trace_enabled
            _.on_http_trace_start(self.request)
            _.request_data(self.request)                                    # some call to generate some traces
            _.on_http_trace_stop(self.request, self.response)

            trace_call_2   = self.request.state.trace_call
            view_model_2 = _.request_traces_view_model(self.request)
            assert len(view_model_2) == 8
            if in_pytest_with_coverage() is False:
                assert trace_call_2.stats() == {'calls': 18, 'calls_skipped': 14, 'exceptions': 0, 'lines': 45, 'returns': 15, 'unknowns': 0}
            for item in view_model_2:
                assert list_set(item) == ['duration', 'emoji', 'extra_data', 'lines', 'locals', 'method_name',
                                          'method_parent', 'parent_info', 'prefix', 'source_code', 'source_code_caller',
                                          'source_code_location', 'tree_branch']

            # 3rd execution with trace_disabled
            _.log_requests = False
            _.on_http_trace_start(self.request)
            assert trace_call_1.started is False                            # this value should not change

            _.request_data(self.request)                                    # some call to generate some traces
            _.on_http_trace_stop(self.request, self.response)
            assert trace_call_1.started is False

            trace_call_3 = self.request.state.trace_call
            view_model_3 = _.request_traces_view_model(self.request)
            assert len(view_model_3)    == len(view_model_2)                # no change in stats
            assert trace_call_3.stats() == trace_call_2.stats()             # no change in stats


