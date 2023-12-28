import threading
from urllib.parse import urljoin

import requests
from threading              import Thread
from fastapi                import FastAPI
from osbot_utils.utils.Http import wait_for_port, wait_for_port_closed
from uvicorn                import Config, Server
from osbot_utils.utils.Misc import random_port

FAST_API__HOST      = "127.0.0.1"
FAST_API__LOG_LEVEL = "info"

class Fast_API_Server:
    def __init__(self, app, port=None):
        self.app   : FastAPI = app
        self.port  : int     = port or random_port()
        self.config: Config  = Config(app=self.app, host=FAST_API__HOST, port=self.port, log_level=FAST_API__LOG_LEVEL)
        self.server: Server  = None
        self.thread: Thread  = None

    def start(self):
        self.server = Server(config=self.config)

        def run():
            self.server.run()

        self.thread = threading.Thread(target=run)
        self.thread.start()
        wait_for_port(host=FAST_API__HOST, port=self.port)
        return True

    def stop(self):
        self.server.should_exit = True
        self.thread.join()
        return wait_for_port_closed(host=FAST_API__HOST, port=self.port)

    def url(self):
        return f'http://{FAST_API__HOST}:{self.port}/'

    def requests_get(self, path=''):
        url = urljoin(self.url(), path)
        return requests.get(url)

