from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from osbot_fast_api.api.Fast_API import Fast_API


class test_integration__Fast_API(TestCase):
    def setUp(self):
        self.fast_api = Fast_API()

    def test_app(self):
        pprint('here')