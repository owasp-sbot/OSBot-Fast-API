from unittest import TestCase

from osbot_fast_api.examples.ex_2_with_api_key.Fast_API__With_API_Key import Fast_API__With_API_Key, \
    ROUTES_PATHS__WITH_API_KEY, EX_2_API_KEY_NAME, EX_2_API_KEY_VALUE
from tests.unit.api.test_Fast_API import EXPECTED_ROUTES_PATHS


class test_Fast_API__With_API_Key(TestCase):

    def setUp(self):
        self.fast_api = Fast_API__With_API_Key().setup()
        self.client   = self.fast_api.client()


    def test_client__an_get_route(self):
        response = self.client.get('/an-get-route')
        assert response.status_code == 200
        assert response.json()      == 'hello from middleware'
        assert response.headers.get('extra_header') == 'goes here'

    def test_client__secure_data(self):
        response_1 = self.client.get('/secure-data')
        assert response_1.status_code                 == 403
        assert response_1.json()                      == {'detail': 'Not authenticated'}
        assert response_1.headers.get('extra_header') == 'goes here'

        headers    = {EX_2_API_KEY_NAME : EX_2_API_KEY_VALUE}
        response_2 = self.client.get(url='/secure-data', headers=headers)
        assert response_2.status_code                 == 200
        assert response_2.json()                      == {'message': 'Secure data accessed'}
        assert response_2.headers.get('extra_header') == 'goes here'

        headers    = {EX_2_API_KEY_NAME : 'aaaaaa'}
        response_3 = self.client.get(url='/secure-data', headers=headers)
        assert response_3.status_code                 == 403
        assert response_3.json()                      == {'detail': 'Invalid API Key'}
        assert response_3.headers.get('extra_header') == 'goes here'

    def test_client__the_answer(self):
        response = self.client.get('/the-answer')
        assert response.status_code == 200
        assert response.json()      == 42
        assert response.headers.get('extra_header') == 'goes here'

    def test_setup_middlewares(self):
        assert self.fast_api.user_middlewares() == [{'function_name': 'an_middleware', 'params': {}, 'type': 'BaseHTTPMiddleware'}]

    def test_setup_routes(self):
        assert self.fast_api.routes_paths() == sorted(EXPECTED_ROUTES_PATHS + ROUTES_PATHS__WITH_API_KEY)