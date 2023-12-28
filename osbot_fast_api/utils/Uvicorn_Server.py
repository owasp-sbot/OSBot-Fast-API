import selectors
import subprocess
from urllib.parse import urljoin

from osbot_utils.utils.Files import parent_folder
from osbot_utils.utils.Http import GET, wait_for_http, wait_for_port_closed
from osbot_utils.utils.Misc import random_port

UVICORN_SERVER_NAME = 'localhost'

class Uvicorn_Server:

    def __init__(self, python_file, port=None):
        self.cwd         = parent_folder(python_file)
        self.port        = port  or random_port()
        self.process     = None
        self.python_file = python_file
        self.python_path = 'python3'
        self.stdout      = None
        self.stderr      = None
        self.sel = None

    def start(self):
        self.process = subprocess.Popen(args=['uvicorn', "server:app", "--port", str(self.port)],
                                        cwd=self.cwd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        bufsize=1)

        self.sel = selectors.DefaultSelector()
        self.sel.register(self.process.stdout, selectors.EVENT_READ, self.read_stdout)
        self.sel.register(self.process.stderr, selectors.EVENT_READ, self.read_stderr)

        return self.wait_for_server_started()

    def read_stderr(self, stderr):
        print('in read_stderr')
        line = stderr.readline()
        if line:
            print('stderr:', line, end='')

    def read_stdout(self, stdout):          # todo: bug: figure out why the stdout and stderr are not being read
        print('in read_stdout')
        line = stdout.readline()
        if line:
            print('stdout:', line, end='')



    def stop(self):
        if self.process:
            self.process.kill()
            self.process.wait()
            self.sel.close()
        return self.wait_for_server_stopped()
            #print(f"stdout: {self.stdout.decode('utf-8')}")
            #print(f"stderr: {self.stderr.decode('utf-8')}")

    def url(self):
        return f'http://{UVICORN_SERVER_NAME}:{self.port}/'

    def http_GET(self, path):
        url = urljoin(self.url(), path)
        return GET(url)

    def wait_for_server_started(self):
        return wait_for_http(self.url())

    def wait_for_server_stopped(self):
        return wait_for_port_closed(host=UVICORN_SERVER_NAME, port=self.port)