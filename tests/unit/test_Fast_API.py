from unittest import TestCase

from fastapi import FastAPI

from osbot_fast_api.Fast_API import Fast_API


class test_First_Class(TestCase):

    def setUp(self):
        self.fast_api = Fast_API()

    def test__init__(self):
        assert type(self.fast_api.app()) is FastAPI

