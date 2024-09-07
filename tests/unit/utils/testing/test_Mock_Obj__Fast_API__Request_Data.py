from decimal import Decimal
from unittest import TestCase

from osbot_fast_api.api.Fast_API__Request_Data import Fast_API__Request_Data
from osbot_fast_api.utils.testing.Mock_Obj__Fast_API__Request_Data import Mock_Obj__Fast_API__Request_Data
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects import obj_data


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
            assert type(_) is Fast_API__Request_Data
            res_content_type   = self.mock_request_data.content_type
            res_content_length = str(len(self.mock_request_data.res_content))
            expected_data = {'client_city'              : self.mock_request_data.city               ,
                             'client_country'           : self.mock_request_data.country            ,
                             'client_ip'                : 'pytest'                                  ,
                             'domain'                   : self.mock_request_data.domain             ,
                             'fast_api_name'            : self.mock_request_data.fast_api_name      ,
                             'log_messages'             : []                                        ,
                             'request_duration'         : Decimal('0.000')                          ,
                             'request_headers'          : self.mock_request_data.req_headers_data   ,
                             'request_host_name'        : self.mock_request_data.hostname           ,
                             'request_id'               : _.request_id                              ,
                             'request_method'           : self.mock_request_data.method             ,
                             'request_path'             : self.mock_request_data.path               ,
                             'request_port'             : self.mock_request_data.port               ,
                             'request_start_time'       : _.request_start_time                      ,
                             'response_content_length'  : res_content_length                        ,
                             'response_content_type'    : res_content_type                          ,
                             'response_end_time'        : _.response_end_time                       ,
                             'response_headers'         : {'content-length'     : res_content_length,
                                                           'content-type'       : res_content_type  ,
                                                           'fast-api-request-id': _.request_id }    ,
                             'response_status_code'     : self.mock_request_data.res_status_code    ,
                             'thread_id'                : _.thread_id                               ,
                             'timestamp'                : _.timestamp                               ,
                             'traces'                   : []                                        ,
                             'traces_count'             : 0                                         }
            assert request_data.json() == expected_data


