from fastapi                                                          import Request, Response
from osbot_utils.utils.Misc                                           import str_to_bytes
from starlette.middleware.base                                        import BaseHTTPMiddleware
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid import Random_Guid


class Middleware__Request_ID(BaseHTTPMiddleware):                                           # Lightweight middleware for request ID generation and propagation

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id               = Random_Guid()                                            # Generate request ID once
        request.state.request_id = request_id                                               # Make available during request processing


        request.headers._list.append((b'fast-api-request-id', str_to_bytes(request_id)))    # Also add to request headers for consistency (though request.state is the preferred access method)

        response = await call_next(request)                                                 # Process request

        response.headers['fast-api-request-id'] = str(request_id)                           # Add to response headers for client

        return response