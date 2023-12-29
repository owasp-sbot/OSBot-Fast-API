from pprint import pprint

from starlette.requests import Request

from osbot_fast_api.api.Fast_API import Fast_API

ROUTES_PATHS__WITH_API_KEY = ['/an-get-route']

class Fast_API__With_API_Key(Fast_API):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def setup_middlewares(self):
        @self.app().middleware("http")
        async def an_middleware(request: Request, call_next):
            response = await call_next(request)
            response.headers['extra_header'] = 'goes here'
            return response


    def setup_routes(self):
        def an_get_route(request: Request):
            pprint(request.headers)
            return "Hello World"

        self.add_route_get(an_get_route)