from osbot_fast_api.api.events.Fast_API__Http_Event                        import Fast_API__Http_Event
from decimal                                                        import Decimal
from unittest                                                       import TestCase
from osbot_fast_api.utils.testing.Mock_Obj__Fast_API__Request_Data import Mock_Obj__Fast_API__Request_Data


class test_Mock_Obj__Fast_API__Request_Data(TestCase):

    def setUp(self):
        self.mock_request_data = Mock_Obj__Fast_API__Request_Data()

    def test__init__(self):
        expected_data = {'address': None,
                         'city': '',
                         'content_type': '',
                         'country': '',
                         'domain': '',
                         'fast_api_name': '',
                         'hostname': '',
                         'ip_address': '',
                         'method': '',
                         'path': '',
                         'port': 0,
                         'querystring': b'',
                         'req_headers': [],
                         'req_headers_data': {},
                         'request': None,
                         'request_data': None,
                         'res_content': b'',
                         'res_headers': {},
                         'res_status_code': 0,
                         'response': None,
                         'scope': {},
                         'type': '',
                         'url': ''}
        assert self.mock_request_data.json()       == expected_data
        assert self.mock_request_data.__locals__() == expected_data
        assert type(self.mock_request_data)        is Mock_Obj__Fast_API__Request_Data

    def test_create(self):
        request_data =  self.mock_request_data.create()
        with request_data as _:
            assert type(_) is Fast_API__Http_Event
            res_content_type   = self.mock_request_data.content_type
            res_content_length = str(len(self.mock_request_data.res_content))
            duration           = request_data.http_event_request.duration
            expected_data = {'http_event_info'          : { 'client_city'   : self.mock_request_data.city                ,
                                                            'client_country': self.mock_request_data.country             ,
                                                            'client_ip'     : 'pytest'                                   ,
                                                            'domain'        : self.mock_request_data.domain              ,
                                                            'event_id'      : request_data.event_id                      ,
                                                            'info_id'       : request_data.http_event_info.info_id       ,
                                                            'fast_api_name' : self.mock_request_data.fast_api_name       ,
                                                            'log_messages'  : []                                         ,
                                                            'thread_id'     : _.http_event_info.thread_id                ,
                                                            'timestamp'     : _.http_event_info.timestamp                },
                             'http_event_request'       : { 'duration'      : duration                                   ,
                                                            'event_id'      : request_data.event_id                      ,
                                                            'headers'       : self.mock_request_data.req_headers_data    ,
                                                            'host_name'     : self.mock_request_data.hostname            ,
                                                            'method'        : self.mock_request_data.method              ,
                                                            'path'          : self.mock_request_data.path                ,
                                                            'port'          : self.mock_request_data.port                ,
                                                            'request_id'     : request_data.http_event_request.request_id,
                                                            'start_time'    : _.http_event_request.start_time           },
                             'event_id'                 : _.event_id                              ,
                             'http_event_response'      : { 'content_length': res_content_length                        ,
                                                            'content_type'  : res_content_type                          ,
                                                            'end_time'      : _.http_event_response.end_time            ,
                                                            'event_id'      : request_data.event_id                     ,
                                                            'headers'       : { 'content-length'    : res_content_length,
                                                                                'content-type'      : res_content_type  },
                                                            'response_id'   : request_data.http_event_response.response_id,
                                                            'status_code'   : self.mock_request_data.res_status_code    },
                             'http_event_traces'        : { 'event_id'      : request_data.event_id                     ,
                                                            'traces'                   : []                             ,
                                                            'traces_count'             : 0                              ,
                                                            'traces_id'     : request_data.http_event_traces.traces_id  }}
            assert request_data.json() == expected_data



