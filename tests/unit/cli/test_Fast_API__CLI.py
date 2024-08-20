import requests
from unittest import TestCase
from unittest.mock import patch
from osbot_fast_api.cli.Fast_API__CLI import Fast_API__CLI


class test_Fast_API__CLI(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fast_api_cli = Fast_API__CLI().setup()
        assert cls.fast_api_cli.fast_api_server.running is False
        cls.fast_api_cli.start()
        assert cls.fast_api_cli.fast_api_server.running is True


    @classmethod
    def tearDownClass(cls):
        cls.fast_api_cli.stop()
        assert cls.fast_api_cli.fast_api_server.running is False

    def test__init__(self):
        with self.fast_api_cli as _:
            assert _.__attr_names__() == ['app', 'fast_api', 'fast_api_server']
            assert _.registered_commands_names() == ['start', 'stop', 'python']
            assert _.fast_api.routes_paths() == ['/', '/config/status', '/config/version']
            assert requests.get(_.fast_api_server.url(), allow_redirects=False).status_code == 307


    def test_command_completions(self):
        with self.fast_api_cli as _:
            assert _.command_completions(    ) == ['start', 'stop', 'python']
            assert _.command_completions('s' ) == ['start', 'stop']
            assert _.command_completions('st') == ['start', 'stop']
            assert _.command_completions('p' ) == ['python']
            assert _.command_completions('x' ) == []

    @patch('readline.get_line_buffer')
    def test_completer_returns_completion(self, mock_get_line_buffer):
        with self.fast_api_cli as _:
            mock_get_line_buffer.return_value = 'an line value'
            assert _.completer('s', 0) == 'start'
            assert _.completer('s', 1) == 'stop'
            assert _.completer('s', 2) is None
            assert _.completer('x', 2) is None

