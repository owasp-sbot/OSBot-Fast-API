from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from osbot_fast_api.examples.ex_2_with_api_key.Fast_API__With_API_Key import Fast_API__With_API_Key, \
    ROUTES_PATHS__WITH_API_KEY


class test_Fast_API__With_API_Key(TestCase):

    def setUp(self):
        self.fast_api = Fast_API__With_API_Key()
        self.client   = self.fast_api.client()


    def test_client__an_get_route(self):
        response = self.client.get('/an-get-route')
        assert response.status_code == 200
        assert response.json()        == 'Hello World'
        assert response.headers.get('extra_header') == 'goes here'

    def test_setup_middlewares(self):
        assert self.fast_api.user_middlewares() == [{'function_name': 'an_middleware', 'params': {}, 'type': 'BaseHTTPMiddleware'}]

    def test_setup_routes(self):
        assert self.fast_api.routes_paths() == ROUTES_PATHS__WITH_API_KEY