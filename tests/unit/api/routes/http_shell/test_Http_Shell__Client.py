from unittest import TestCase

from osbot_fast_api.api.routes.http_shell.Http_Shell__Client import Http_Shell__Client


class test_Http_Shell__Client(TestCase):

    def setUp(self):
        self.client = Http_Shell__Client()