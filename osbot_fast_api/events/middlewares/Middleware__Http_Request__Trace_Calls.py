# from starlette.middleware.base  import BaseHTTPMiddleware
# from fastapi                    import Request
# from starlette.responses        import Response
#
# from osbot_fast_api.events.Fast_API__Http_Events      import Fast_API__Http_Events
# from osbot_utils.helpers.trace.Trace_Call import Trace_Call
# from osbot_utils.helpers.trace.Trace_Call__Config import Trace_Call__Config
#
#
# class Middleware__Http_Request__Trace_Calls(BaseHTTPMiddleware):
#
#     def __init__(self, app, http_events: Fast_API__Http_Events):
#         super().__init__(app)
#         self.http_events = http_events
#
#     async def dispatch(self, request: Request, call_next) -> Response:
#
#         if self.http_events.trace_calls is False:          # check if Trace is Enabled
#             return await call_next(request)
#
#         #trace_call               = self.start_trace()
#         #request.state.trace_call = trace_call
#         self.http_events.on_http_trace_start(request)
#
#         response = await call_next(request)
#
#         #self.stop_trace(trace_call)
#         self.http_events.on_http_trace_stop(request, response)
#         return response
#
#     # def start_trace(self):
#     #     trace_call_config = self.http_events.trace_call_config
#     #     trace_call = Trace_Call(config=trace_call_config)
#     #     trace_call.start()
#     #     return trace_call
#     #
#     # def stop_trace(self, trace_call):
#     #     trace_call.stop()