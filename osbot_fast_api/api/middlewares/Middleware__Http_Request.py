from fastapi                                     import Request
from starlette.middleware.base                   import BaseHTTPMiddleware
from starlette.responses                         import Response

from osbot_fast_api.api.Fast_API__Http_Events import Fast_API__Http_Events


class Middleware__Http_Request(BaseHTTPMiddleware):

    def __init__(self, app, http_events: Fast_API__Http_Events):
        super().__init__(app)
        self.http_events  = http_events

    async def dispatch(self, request: Request, call_next) -> Response:
        self.http_events.on_http_request(request)
        response = None
        try:
            response = await call_next(request)
        finally:
            self.http_events.on_http_response(request, response)
        return response