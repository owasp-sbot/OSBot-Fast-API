import osbot_fast_api
from unittest                            import TestCase
from unittest.mock                       import MagicMock, patch
from osbot_utils.utils.Files             import path_combine, file_exists, parent_folder, folder_name
from osbot_utils.utils.Http              import is_port_open
from osbot_fast_api.utils.Uvicorn_Server import Uvicorn_Server, UVICORN_SERVER_NAME


class test_Uvicorn_Server(TestCase):

    def setUp(self):
        self.file_name      = 'server.py'
        self.python_file    = path_combine(parent_folder(osbot_fast_api.path),  self.file_name)
        self.uvicorn_server = Uvicorn_Server(python_file=self.python_file)


    def test__init__(self):
        assert file_exists(self.python_file)
        assert folder_name(parent_folder(self.python_file)) == 'OSBot-Fast-API'
        assert self.uvicorn_server.cwd                      == parent_folder(self.python_file)
        assert self.uvicorn_server.port                     > 19999
        assert self.uvicorn_server.process                  is None
        assert self.uvicorn_server.python_file              == self.python_file
        assert self.uvicorn_server.python_path              == 'python3'

    @patch('builtins.print')
    def test_read_stderr(self, mock_print):
        mock_stderr = MagicMock()
        mock_stderr.readline.return_value = 'error message\n'
        self.uvicorn_server.read_stderr(mock_stderr)
        mock_print.assert_any_call('in read_stderr')
        mock_print.assert_any_call('stderr:', 'error message\n', end='')

    @patch('builtins.print')
    def test_read_stdout(self, mock_print):
        mock_stdout = MagicMock()
        mock_stdout.readline.return_value = 'test output\n'
        self.uvicorn_server.read_stdout(mock_stdout)
        mock_print.assert_any_call('in read_stdout')
        mock_print.assert_any_call('stdout:', 'test output\n', end='')

    def test_start_stop(self):

        assert is_port_open(UVICORN_SERVER_NAME, self.uvicorn_server.port) is False
        assert self.uvicorn_server.start() is True

        assert is_port_open(UVICORN_SERVER_NAME, self.uvicorn_server.port) is True
        assert '<title>FastAPI - Swagger UI</title>' in self.uvicorn_server.http_GET('docs')

        assert self.uvicorn_server.stop() is True
        assert is_port_open(UVICORN_SERVER_NAME, self.uvicorn_server.port) is False
