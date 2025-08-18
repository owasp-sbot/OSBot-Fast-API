from functools                              import wraps
from fastapi                                import Request
from osbot_utils.helpers.trace.Trace_Call   import Trace_Call

# this is needed to add support for tracing a request for the FastAPI requests that execute in the threat pool
#   i.e. any request that doesn't use async in the method definition


def fast_api_thread_trace_request(func):
    @wraps(func)
    def wrapper(self, request: Request=None, *args, **kwargs):
        root_node = func.__name__
        with Fast_API__Thread__Trace_Request(request, root_node=root_node):
            return func(self, request, *args, **kwargs)
    return wrapper



class Fast_API__Thread__Trace_Request:
    trace_call : Trace_Call

    def __init__(self, request, root_node=None):
        self.request     = request
        self.event_id    = None
        self.trace_call  = None
        self.root_node   = root_node

    def __enter__(self):
        if self.request:
            self.event_id   = getattr(self.request.state, 'event_id', None)
            self.trace_call = getattr(self.request.state, 'trace_call', None)

        if self.trace_call:
            self.trace_call.start__on_thread(root_node=self.root_node)


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.trace_call:
            self.trace_call.stop__on_thread()