from osbot_fast_api.api.Fast_API                 import Fast_API
from osbot_fast_api.events.Fast_API__Http_Events import Fast_API__Http_Events


class Fast_API__With_Events(Fast_API):
    http_events : Fast_API__Http_Events                                       # Only in this subclass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.http_events.fast_api_name = self.config.name                     # Wire up the name

    def setup_middlewares(self):                                              # Add event middleware    (NOTE: the middleware execution is the reverse of the order they are added)
        self.setup_middleware__http_events()                                  # This will make this middleware to be the last one executed
        super().setup_middlewares()                                           # Call parent middlewares first

        return self

    def setup_middleware__http_events(self):                                  # Moved from base class
        from osbot_fast_api.events.middlewares.Middleware__Http_Request import Middleware__Http_Request

        self.app().add_middleware(Middleware__Http_Request, http_events=self.http_events)
        return self

    def event_id(self, request):                                              # Event tracking methods
        return self.http_events.event_id(request)

    def request_data(self, request):
        return self.http_events.request_data(request)

    def request_messages(self, request):
        return self.http_events.request_messages(request)

    def add_background_task(self, task):                                      # Background task management
        self.http_events.background_tasks.append(task)
        return self

    def enable_request_tracing(self, config=None):                            # Tracing configuration
        self.http_events.trace_calls = True
        if config:
            self.http_events.trace_call_config = config
        return self

    def disable_request_tracing(self):
        self.http_events.trace_calls = False
        return self

    def set_callback_on_request(self, callback):                              # Event callbacks
        self.http_events.callback_on_request = callback
        return self

    def set_callback_on_response(self, callback):
        self.http_events.callback_on_response = callback
        return self

    def get_recent_requests(self, count=10):                                  # Request history
        recent = list(self.http_events.requests_order)[-count:]
        return [self.http_events.requests_data.get(event_id) for event_id in recent]

    def clear_request_history(self):
        self.http_events.requests_data.clear()
        self.http_events.requests_order.clear()
        return self