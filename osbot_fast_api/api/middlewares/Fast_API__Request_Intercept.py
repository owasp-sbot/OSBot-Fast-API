import time
from decimal                                      import Decimal
from fastapi                                     import Request
from starlette.responses                         import Response
from starlette.middleware.base                   import RequestResponseEndpoint
from starlette.middleware.base                   import BaseHTTPMiddleware

class Fast_API__Request_Intercept(BaseHTTPMiddleware):

    def __init__(self, *args, **kwargs):
        if 'name' in kwargs:
            del kwargs['name']                                  # todo: find better way to pass params to this Fast_API__Request_Intercept
        super().__init__(*args, **kwargs)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = Decimal(time.time())
        response   = await call_next(request)
        end_time   = Decimal(time.time())
        duration   = end_time - start_time
        duration   = duration.quantize(Decimal('0.001'))
        url        = request.url                            # todo: add a way to capture this from the callers
        return response