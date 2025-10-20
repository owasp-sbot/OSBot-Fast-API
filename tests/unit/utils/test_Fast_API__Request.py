from fastapi                                import Request
from unittest                               import TestCase
from starlette.datastructures               import Address
from osbot_fast_api.utils.Fast_API__Request import Fast_API__Request
from osbot_utils.testing.__                 import __


class test_Fast_API__Request(TestCase):
    def setUp(self):
        self.fast_api_request = Fast_API__Request()
        return self

    def test__init__(self):
        assert self.fast_api_request.obj() == __(address_host       = 'pytest'  ,
                                                 address_port       = 12345     ,
                                                 scope_method       = 'GET'     ,
                                                 scope_path         = '/an/path',
                                                 scope_type         = 'http'    ,
                                                 scope_headers      = __()      ,
                                                 scope_query_string = b''       )

    def test_address(self):
        assert self.fast_api_request.address() == Address('pytest', 12345)

    def test_request(self):
        request = self.fast_api_request.request()
        assert request.scope == self.fast_api_request.scope()

    def test_scope(self):
        assert self.fast_api_request.scope() == dict(type        = 'http'                  ,
                                                     client      = Address('pytest', 12345),
                                                     path        ='/an/path'               ,
                                                     method      ='GET'                    ,
                                                     headers     = []                      ,
                                                     query_string= b''                     )

    def test_enter(self):
        with self.fast_api_request as _:
            assert type(_) is Request
            assert _.scope == self.fast_api_request.scope()