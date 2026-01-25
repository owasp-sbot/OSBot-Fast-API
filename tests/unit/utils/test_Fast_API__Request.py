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

    def test_create_headers(self):
        with Fast_API__Request() as _:
            assert _.headers.items() == []                                                              # no headers set

        with Fast_API__Request(scope_headers={'content-type': 'application/json'}) as _:
            assert _.headers.get('content-type') == 'application/json'                                  # single header

        with Fast_API__Request(scope_headers={'content-type': 'application/json',
                                              'accept'      : 'text/html'       }) as _:
            assert _.headers.get('content-type') == 'application/json'                                  # multiple headers
            assert _.headers.get('accept'      ) == 'text/html'

    def test_set_cookie(self):
        with Fast_API__Request() as _:
            assert _.cookies == {}                                                                      # no cookies set
        with Fast_API__Request().set_cookie('session_id', 'abc123') as _:
            assert _.cookies.get('session_id') == 'abc123'                                              # single cookie

    def test_set_cookies(self):
        cookies = [('session_id', 'abc123'), ('user_id', '42')]
        with Fast_API__Request().set_cookies(cookies) as _:
            assert _.cookies.get('user_id'   ) == '42'                                                  # note: starlette only keeps last cookie

    def test_set_header(self):
        with Fast_API__Request().set_header('x-custom', 'value') as _:
            assert _.headers.get('x-custom') == 'value'                                                 # single header via set_header

    def test_set_headers(self):
        headers = {'X-Custom-One': 'value1', 'X-Custom-Two': 'value2'}
        with Fast_API__Request().set_headers(headers) as _:
            assert _.headers.get('x-custom-one') == 'value1'                                            # keys are lowercased
            assert _.headers.get('x-custom-two') == 'value2'