import sys
from threading                            import Thread
from unittest                             import TestCase
from fastapi                              import FastAPI
from uvicorn                              import Config, Server
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server, FAST_API__LOG_LEVEL, FAST_API__HOST


class test_Fast_API_Server(TestCase):

    def setUp(self):
        self.app             = FastAPI()
        self.fast_api_server = Fast_API_Server(app=self.app)

    def test__init__(self):
        assert self.fast_api_server.app              == self.app
        assert self.fast_api_server.server           is None
        assert self.fast_api_server.thread           is None
        assert type(self.fast_api_server.config)     is Config
        assert self.fast_api_server.config.host      == FAST_API__HOST
        assert self.fast_api_server.config.port      == self.fast_api_server.port
        assert self.fast_api_server.config.log_level == FAST_API__LOG_LEVEL

    def test_start__start(self):
        assert self.fast_api_server.start() is True

        assert type(self.fast_api_server.server) is Server          # confirm these values are now set
        assert type(self.fast_api_server.thread) is Thread

        assert self.fast_api_server.server.config         == self.fast_api_server.config
        assert self.fast_api_server.server.force_exit     is False
        assert self.fast_api_server.server.last_notified  == 0.0
        assert self.fast_api_server.server.should_exit    is False
        assert self.fast_api_server.server.started        is True
        assert self.fast_api_server.thread.daemon         is False
        assert self.fast_api_server.thread.name.startswith('Thread')

        response = self.fast_api_server.requests_get()

        assert response.status_code                       == 404
        assert response.text                              == '{"detail":"Not Found"}'
        assert self.fast_api_server.stop()                is True
        assert self.fast_api_server.server.should_exit    is True


    def test__start_using_context(self):
        with Fast_API_Server() as _:
            assert _.requests_get('openapi.json').json() == { 'info'   : {'title': 'FastAPI', 'version': '0.1.0'},
                                                              'openapi': '3.1.0',
                                                              'paths'  : {}}

    def test_capture_logs(self):
        app = FastAPI()

        @app.get("/ping")
        def ping():
            print("in ping")
            print("error in ping", file=sys.stderr)
            return {"it's": "pong"}

        with Fast_API_Server(app=app) as _:
            assert _.requests_get('ping').json() == {"it's": "pong"}
            assert _.stdout.value() == 'in ping\n'
            assert _.stderr.value() == 'error in ping\n'


