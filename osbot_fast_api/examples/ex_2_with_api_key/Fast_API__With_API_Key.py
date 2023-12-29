from fastapi                     import Request, HTTPException, Security
from fastapi.security.api_key    import APIKeyHeader, APIKey
from osbot_fast_api.api.Fast_API import Fast_API

ROUTES_PATHS__WITH_API_KEY = ['/an-get-route', '/secure-data', '/the-answer']
EX_2_API_KEY_NAME          = 'X-API-KEY'
EX_2_API_KEY_VALUE         = 'ex_2_test_api_key'

class Fast_API__With_API_Key(Fast_API):


    def add_secure_method(self):
        app = self.app()

        api_key_header = APIKeyHeader(name=EX_2_API_KEY_NAME, auto_error=True)

        async def get_api_key(api_key_header: str = Security(api_key_header)):
            if api_key_header == EX_2_API_KEY_VALUE:
                return api_key_header
            else:
                raise HTTPException(status_code=403, detail="Invalid API Key")

        @app.get("/secure-data")
        def secure_data(api_key: APIKey = Security(get_api_key)):
            return {"message": "Secure data accessed"}

    def setup_middlewares(self):
        @self.app().middleware("http")
        async def an_middleware(request: Request, call_next):
            request.state.user_message = 'hello from middleware'
            response = await call_next(request)
            response.headers['extra_header'] = 'goes here'
            return response

    def setup_routes(self):
        def an_get_route(request: Request):
            return request.state.user_message

        def the_answer():
            return 42
        self.add_route_get(an_get_route)
        self.add_route_get(the_answer)
        self.add_secure_method()
