from unittest import TestCase

from osbot_fast_api.examples.ex_2_with_api_key.Fast_API__With_API_Key import Fast_API__With_API_Key


class test_Fast_API__With_API_Key(TestCase):

    def setUp(self):
        self.fast_api = Fast_API__With_API_Key()

    def test_routes(self):
        assert self.fast_api.routes_paths(include_default=True) == []