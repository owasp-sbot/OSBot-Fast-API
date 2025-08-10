from unittest                       import TestCase
from tests.unit.fast_api__for_tests import fast_api_client


class test_Middleware__Request_Duration(TestCase):

    def setUp(self):
        self.client = fast_api_client

    def test_route__root(self):
        response = self.client.get('/docs', follow_redirects=False)
        assert response.status_code == 200