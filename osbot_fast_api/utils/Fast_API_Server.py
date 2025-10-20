import requests
import threading
from urllib.parse                    import urljoin
from threading                       import Thread
from fastapi                         import FastAPI
from osbot_utils.utils.Objects       import base_types
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.testing.Stderr      import Stderr
from osbot_utils.testing.Stdout      import Stdout
from osbot_utils.utils.Http          import wait_for_port, wait_for_port_closed, is_port_open, url_join_safe
from uvicorn                         import Config, Server
from osbot_utils.utils.Misc          import random_port

FAST_API__HOST      = "127.0.0.1"
FAST_API__LOG_LEVEL = "error"

class Fast_API_Server(Type_Safe):
    app       : FastAPI
    port      : int
    log_level : str     = FAST_API__LOG_LEVEL
    config    : Config  = None
    server    : Server  = None
    thread    : Thread  = None
    running   : bool    = False
    stdout    : Stdout
    stderr    : Stderr

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.port == 0:
            self.port = random_port()
        if self.config is None:
            self.config = Config(app=self.app, host=FAST_API__HOST, port=self.port, log_level=self.log_level)

    def __enter__(self):
        self.stderr.start()
        self.stdout.start()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.stdout.stop()
        self.stderr.stop()
        pass

    def is_port_open(self):
        return is_port_open(host=FAST_API__HOST, port=self.port)

    def start(self):
        self.server = Server(config=self.config)

        def run():
            self.server.run()

        self.thread = threading.Thread(target=run)
        self.thread.start()
        wait_for_port(host=FAST_API__HOST, port=self.port)
        self.running = True
        return True

    def stop(self):
        self.server.should_exit = True
        self.thread.join()
        result = wait_for_port_closed(host=FAST_API__HOST, port=self.port)
        self.running = False
        return result

    def requests_delete(self, path='', **kwargs):
        url = url_join_safe(self.url(), path)
        return requests.delete(url, **kwargs)

    def requests_get(self, path='', **kwargs):
        url = url_join_safe(self.url(), path)
        return requests.get(url, **kwargs)

    def requests_post(self, path='', data=None, json=None, **kwargs):
        if json is None:
            if Type_Safe in base_types(data):
                json = data.json()
            elif type(data) is dict:
                json = data
            else:
                raise ValueError("data must be a Type_Safe or a dict")
        url = urljoin(self.url(), path)
        return requests.post(url, json=json, **kwargs)

    def url(self):
        return f'http://{FAST_API__HOST}:{self.port}/'