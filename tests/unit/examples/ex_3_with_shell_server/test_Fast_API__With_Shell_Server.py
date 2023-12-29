from unittest import TestCase

from osbot_fast_api.examples.ex_3_with_shell_server.Fast_API__With_Shell_Server import Fast_API__With_Shell_Server


class test_Fast_API__With_Shell_Server(TestCase):

    def setUp(self) -> None:
        self.fast_api = Fast_API__With_Shell_Server()

    def test_routes_paths(self):
        assert self.fast_api.routes_paths() == []

