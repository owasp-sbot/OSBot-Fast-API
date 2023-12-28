from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from osbot_fast_api.api.Fast_API import Fast_API


class test_Fast_API_Utils(TestCase):

    def setUp(self):
        self.fast_api       = Fast_API()
        self.fast_api_utils = self.fast_api.fast_api_utils()

    def test_fastapi_routes(self):
        routes  = self.fast_api_utils.fastapi_routes(include_default=False)
        assert routes == [{'http_methods': ['GET'        ], 'http_path': '/'      , 'method_name': 'redirect_to_docs'}]