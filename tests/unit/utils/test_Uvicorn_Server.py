from unittest import TestCase

from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import path_combine, file_exists, parent_folder, folder_name
from osbot_utils.utils.Http import is_port_open

import osbot_fast_api
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


    def test_start_stop(self):
        with Duration(prefix='start'):
            assert is_port_open(UVICORN_SERVER_NAME, self.uvicorn_server.port) is False
            assert self.uvicorn_server.start() is True

        with Duration(prefix='requesrt'):
            assert is_port_open(UVICORN_SERVER_NAME, self.uvicorn_server.port) is True
            assert '<title>FastAPI - Swagger UI</title>' in self.uvicorn_server.http_GET('docs')
        with Duration(prefix='stop'):
            assert self.uvicorn_server.stop() is True
            assert is_port_open(UVICORN_SERVER_NAME, self.uvicorn_server.port) is False
