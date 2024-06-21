import requests
import threading
from urllib.parse           import urljoin
from threading              import Thread
from fastapi                import FastAPI
from osbot_utils.utils.Http import wait_for_port, wait_for_port_closed, is_port_open
from uvicorn                import Config, Server
from osbot_utils.utils.Misc import random_port

FAST_API__HOST      = "127.0.0.1"
FAST_API__LOG_LEVEL = "error"

class Fast_API_Server:
    def __init__(self, app, port=None, log_level=None):
        self.app       : FastAPI = app
        self.port      : int     = port or random_port()
        self.log_level : str     = log_level or FAST_API__LOG_LEVEL
        self.config    : Config  = Config(app=self.app, host=FAST_API__HOST, port=self.port, log_level=self.log_level)
        self.server    : Server  = None
        self.thread    : Thread  = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def is_port_open(self):
        return is_port_open(host=FAST_API__HOST, port=self.port)

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

    def requests_get(self, path=''):
        url = urljoin(self.url(), path)
        return requests.get(url)

    def url(self):
        return f'http://{FAST_API__HOST}:{self.port}/'