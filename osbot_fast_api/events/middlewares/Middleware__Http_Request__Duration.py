# import time
# from decimal                                     import Decimal
# from fastapi                                     import Request
# from starlette.middleware.base                   import BaseHTTPMiddleware
# from starlette.responses                         import Response
#
# from osbot_fast_api.events.Fast_API__Http_Events      import Fast_API__Http_Events
#
#
# class Middleware__Http_Request__Duration(BaseHTTPMiddleware):
#
#     def __init__(self, app, http_events: Fast_API__Http_Events):
#         super().__init__(app)
#         self.http_events = http_events
#
#     async def dispatch(self, request: Request, call_next) -> Response:
#         start_time       = Decimal(time.time())
#         response         = None
#         try:
#             response         = await call_next(request)
#         finally:
#             end_time         = Decimal(time.time())
#             duration         = end_time - start_time
#             duration         = duration.quantize(Decimal('0.001'))
#             request_duration = dict(start_time = start_time,
#                                     end_time   = end_time  ,
#                                     duration   = duration  )
#             request.state.request_duration  = request_duration
#             #if self.client:
#             self.http_events.on_http_duration(request, request_duration)
#         return response