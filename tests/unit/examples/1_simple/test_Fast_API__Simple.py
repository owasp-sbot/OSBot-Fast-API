from unittest import TestCase

from fastapi import FastAPI
from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.examples.A_simple.Fast_API__Simple import Fast_API__Simple

class test_Fast_API__Simple(TestCase):

    def setUp(self):
        self.fast_api__simple = Fast_API__Simple()

    def test__init__(self):
        assert isinstance(self.fast_api__simple, Fast_API__Simple)
        assert isinstance(self.fast_api__simple, Fast_API        )
        assert type(self.fast_api__simple.app()) is FastAPI
        #assert type(self.fast_api__simple.fast_api) is Fast_API
        #assert self.fast_api__simple.fast_api.app().title == 'Fast_API__Simple'
        #assert self.fast_api__simple.fast_api.app().version == '0.1.0'