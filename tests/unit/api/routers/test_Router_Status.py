from unittest                                   import TestCase
from fastapi                                    import FastAPI
from starlette.testclient                       import TestClient
from osbot_fast_api.api.routers.Router_Status   import Router_Status
from osbot_fast_api.utils.Version               import Version


class test_Router_Status(TestCase):

    def setUp(self):
        self.app          = FastAPI()
        self.router_status = Router_Status(app=self.app)
        self.client        = TestClient(self.app)

    def test__init__(self):
        assert type(self.router_status)  is Router_Status
        assert self.router_status.tag    == 'status'
        assert self.router_status.app    == self.app
        assert self.router_status.router is not None

    def test_client__status(self):
        response = self.client.get("/status/status")
        assert response.status_code == 200
        assert response.json()      == {'status': 'ok'}

    def test_client__version(self):
        response = self.client.get("/status/version")
        assert response.status_code == 200
        assert response.json() == {'version': Version().value()}

