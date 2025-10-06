from unittest                                       import TestCase
from osbot_fast_api.api.Fast_API                    import Fast_API
from osbot_fast_api.api.schemas.consts.consts__Fast_API import ROUTES__CONFIG, ROUTE_REDIRECT_TO_DOCS


class test_Fast_API_Utils(TestCase):

    def setUp(self):
        self.fast_api       = Fast_API().setup()
        self.fast_api_utils = self.fast_api.fast_api_utils()

    def test_fastapi_routes(self):
        routes  = self.fast_api_utils.fastapi_routes(include_default=False)
        assert routes == [ROUTE_REDIRECT_TO_DOCS] + ROUTES__CONFIG