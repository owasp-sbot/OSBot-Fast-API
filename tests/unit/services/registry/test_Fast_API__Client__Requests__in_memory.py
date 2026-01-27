# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Fast_API__Client__Requests
# Validates generic transport layer with IN_MEMORY and REMOTE modes
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import fast_api__service__registry
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode
from tests.unit.services.registry.test_Fast_API__Client__Requests                                       import Fake__Test__Service__Client, create_test_app, Fake__Test__Service__Client__Requests


class test_Fast_API__Client__Requests__in_memory(TestCase):

    @classmethod
    def setUpClass(cls):
        fast_api__service__registry.clear()
        app    = create_test_app()
        config = Fast_API__Service__Registry__Client__Config(mode         = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY,
                                                             fast_api_app = app                                                      )
        fast_api__service__registry.register(Fake__Test__Service__Client, config)

    @classmethod
    def tearDownClass(cls):
        fast_api__service__registry.clear()

    def test__execute__get_request(self):                                       # Test GET request
        requests = Fake__Test__Service__Client__Requests()

        response = requests.execute("GET", "/health")

        assert response.status_code       == 200
        assert response.json()["status"]  == "ok"

    def test__execute__get_with_path_param(self):                               # Test GET with path parameter
        requests = Fake__Test__Service__Client__Requests()

        response = requests.execute("GET", "/users/42")

        assert response.status_code      == 200
        assert response.json()["id"]     == 42
        assert response.json()["name"]   == "User 42"

    def test__execute__post_request(self):                                      # Test POST request
        requests = Fake__Test__Service__Client__Requests()

        response = requests.execute("POST", "/echo", body={"message": "hello"})

        assert response.status_code                     == 200
        assert response.json()["received"]["message"]   == "hello"

    def test__test_client__cached(self):                                        # Test TestClient is cached
        requests = Fake__Test__Service__Client__Requests()

        client_1 = requests.test_client()
        client_2 = requests.test_client()

        assert client_1 is client_2